"""
baseline_rag.py — Baseline RAG mínimo para o benchmark regfin-rag-assurance.

O que este script faz, em uma frase:
para cada pergunta do gabarito (eval_set_v0.json), encontra a decisão do FOS
relevante, manda o texto dela + a pergunta para o Claude com instruções estritas,
e salva a resposta. Essas respostas serão depois avaliadas por evaluate.py.

Este é um baseline DELIBERADAMENTE SIMPLES (o "aluno" mais básico possível):
- Retrieval por número de decisão (DRN), não por embeddings. Como o gabarito já
  diz qual decisão fundamenta cada pergunta (campo "grounding"), o baseline
  recupera essa decisão diretamente. Isso testa a GERAÇÃO de forma limpa, sem o
  ruído de um retrieval imperfeito. Versões futuras podem trocar por busca real.

SEGURANCA: a chave da API é lida de variavel de ambiente, NUNCA escrita aqui.
"""

import os
import json
import glob
from pathlib import Path

import pypdf
import anthropic

# ---------------------------------------------------------------------------
# CONFIGURACAO — ajuste estes caminhos para a sua maquina
# ---------------------------------------------------------------------------

# Pasta onde estao os PDFs das decisoes do FOS (FORA do repo, so na sua maquina).
# Troque pelo caminho real. Ex Windows: r"C:\Users\voce\decisoes_fos"
DECISIONS_DIR = r"C:\Projects\Dcoumentos do rag-assurance"

# Caminho do gabarito (dentro do repo).
EVAL_SET_PATH = "./eval/eval_set_v0.json"

# Onde salvar as respostas geradas pelo baseline.
OUTPUT_PATH = "./baseline/baseline_responses.json"

# Modelo a usar. Sonnet e um bom equilibrio custo/qualidade para um baseline.
MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# 1. Carregar e indexar as decisoes por DRN
# ---------------------------------------------------------------------------

def extrair_texto_pdf(caminho):
    """Extrai o texto de um PDF. Retorna string vazia se falhar."""
    try:
        leitor = pypdf.PdfReader(caminho)
        return "\n".join((pagina.extract_text() or "") for pagina in leitor.pages)
    except Exception as e:
        print(f"  [aviso] falha ao ler {caminho}: {e}")
        return ""

def indexar_decisoes(pasta):
    """
    Le todos os PDFs da pasta e monta um dicionario {DRN: texto}.
    O DRN e extraido do nome do arquivo (ex: 'DRN-6476426.pdf' -> 'DRN-6476426')
    OU do proprio texto, se o nome do arquivo nao contiver o DRN.
    """
    indice = {}
    padroes = ["*.pdf", "*.PDF"]
    arquivos = []
    for p in padroes:
        arquivos.extend(glob.glob(os.path.join(pasta, "**", p), recursive=True))

    if not arquivos:
        raise SystemExit(
            f"Nenhum PDF encontrado em {pasta}. "
            f"Ajuste DECISIONS_DIR ou a variavel de ambiente FOS_DECISIONS_DIR."
        )

    for caminho in arquivos:
        texto = extrair_texto_pdf(caminho)
        if not texto.strip():
            continue
        # Tenta achar o DRN no texto (formato DRN-XXXXXXX)
        import re
        m = re.search(r"DRN-\d{6,8}", texto)
        if m:
            drn = m.group(0)
        else:
            # fallback: usa o nome do arquivo
            drn = Path(caminho).stem
        indice[drn] = texto
        print(f"  indexado: {drn}  ({len(texto)} chars)  <- {Path(caminho).name}")

    return indice

# ---------------------------------------------------------------------------
# 2. Montar o prompt e chamar o modelo
# ---------------------------------------------------------------------------

INSTRUCAO_SISTEMA = (
    "You are a compliance assistant answering questions about UK APP scam "
    "reimbursement under the FPS Reimbursement Rules. Answer ONLY using the "
    "decision text provided. Cite the decision by its DRN reference. If the "
    "provided text does not contain enough information to answer, or the "
    "question concerns something the decision does not address, you MUST say "
    "that it is not possible to determine the answer from the source rather "
    "than guessing. Do not invent rules, figures, or citations."
)

def responder(cliente, pergunta, texto_decisao, drn):
    """Manda a pergunta + o texto da decisao ao modelo e devolve a resposta."""
    conteudo = (
        f"Decision {drn}:\n\n{texto_decisao}\n\n"
        f"---\n\nQuestion: {pergunta}\n\n"
        f"Answer using only the decision above."
    )
    resposta = cliente.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=INSTRUCAO_SISTEMA,
        messages=[{"role": "user", "content": conteudo}],
    )
    # Junta os blocos de texto da resposta
    return "".join(b.text for b in resposta.content if b.type == "text")

# ---------------------------------------------------------------------------
# 3. Loop principal
# ---------------------------------------------------------------------------

def main():
    # A chave e lida do ambiente pelo proprio SDK (ANTHROPIC_API_KEY).
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "Defina a variavel de ambiente ANTHROPIC_API_KEY antes de rodar. "
            "NUNCA escreva a chave no codigo."
        )
    cliente = anthropic.Anthropic()

    print("Indexando decisoes...")
    indice = indexar_decisoes(DECISIONS_DIR)
    print(f"{len(indice)} decisoes indexadas.\n")

    print("Carregando gabarito...")
    gabarito = json.load(open(EVAL_SET_PATH, encoding="utf-8"))
    itens = gabarito["items"]
    print(f"{len(itens)} itens no gabarito.\n")

    resultados = []
    for item in itens:
        drns = item.get("grounding", [])
        # Junta o texto de todas as decisoes que fundamentam este item
        textos = []
        faltando = []
        for drn in drns:
            if drn in indice:
                textos.append(indice[drn])
            else:
                faltando.append(drn)
        if faltando:
            print(f"  [aviso] {item['id']}: decisoes nao encontradas: {faltando}")
        texto_juntado = "\n\n=====\n\n".join(textos) if textos else ""

        if not texto_juntado:
            resposta_sistema = "[SEM DECISAO INDEXADA — nao foi possivel gerar resposta]"
        else:
            drn_label = ", ".join(drns)
            print(f"  respondendo {item['id']} (fonte {drn_label})...")
            resposta_sistema = responder(cliente, item["question"], texto_juntado, drn_label)

        resultados.append({
            "id": item["id"],
            "type": item["type"],
            "question": item["question"],
            "expected_behaviour": item["expected_behaviour"],
            "grounding": drns,
            "gold_answer": item["gold_answer"],
            "system_response": resposta_sistema,
        })

    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    json.dump(resultados, open(OUTPUT_PATH, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"\nRespostas salvas em {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
