ENTREGÁVEL 1 — Repositório + pergunta de pesquisa + dados brutos (2–3h)

Você cria o esqueleto do projeto e traz os dados reais para dentro dele.

Passos concretos:

Cria um repo público no GitHub. Nome sugerido: regfin-rag-assurance (genérico, não te amarra a mortgage).
Estrutura de pastas: data/raw/ (decisões brutas), data/processed/ (vazia por ora), README.md, e uma pasta eval/ (vazia por ora).
Vai na busca oficial de decisões do FOS. Escolhe um filtro de produto (a decisão que você já vai tomar no fim desta mensagem). Abre 20–25 decisões e salva cada uma em data/raw/ como PDF ou texto. Nomeia com um padrão: DRN-XXXXXXX.pdf (o número de referência da decisão).
Escreve o README com quatro seções e nada mais:
Pergunta de pesquisa: "Como medir se um sistema RAG produz respostas fiéis, auditáveis e conformes num domínio financeiro regulado do UK?"
Escopo: framework de avaliação portátil; primeiro estudo de caso = decisões finais do FOS na categoria X.
O que é / o que não é: é um benchmark de avaliação de fidelidade; não é aconselhamento jurídico nem um produto.
Fonte e ética dos dados: decisões públicas do FOS, anonimizadas na origem, coletadas manualmente da busca oficial.

Critério de pronto: repo público no ar, README com as quatro seções commitado, ≥20 arquivos de decisão em data/raw/.

ENTREGÁVEL 2 — O parser de decisão (2–3h)

Um script Python que lê uma decisão bruta e extrai campos estruturados. Você não precisa de IA para isso — é leitura de texto + regex/parsing simples, e onde o parsing falhar você preenche à mão.

O script parse_decisions.py percorre data/raw/, e para cada decisão extrai:

drn — número de referência da decisão
product_category — categoria do produto (ex.: mortgage, current account, credit card)
complaint_type — sobre o que é a reclamação em uma frase
regulations_cited — lista das regras citadas (referências a DISP, MCOB, etc.)
outcome — upheld / not upheld / partially upheld
reasoning_summary — 2–3 frases resumindo por que o ombudsman decidiu assim

Saída: um único data/processed/decisions.json (ou CSV) com um objeto por decisão.

Realismo importante: o parsing automático vai acertar campos fáceis (DRN, outcome) e falhar em campos que exigem interpretação (reasoning_summary). Tudo bem. Onde o script não conseguir, você completa manualmente. O objetivo do entregável é provar que você transforma PDF bruto em dado estruturado — não construir um parser perfeito. Um parser 60% automático + 40% manual está aprovado.

Critério de pronto: decisions.json com ≥20 registros, todos os seis campos preenchidos, commitado. Se seu tempo real na semana for abaixo de 6h, corta o script e estrutura 10 decisões à mão numa planilha convertida em JSON — o parser vira tarefa da semana 2.

ENTREGÁVEL 3 — O conjunto de avaliação v0, o gabarito (2–3h)

Este é o coração. É a sua contribuição de pesquisa, e não toca em copilot nenhum. A partir das decisões estruturadas, você escreve à mão 15–20 itens de avaliação. Cada item tem esta forma:

json
{
  "id": "eval-001",
  "question": "A consumer complained that their mortgage lender applied an early repayment charge after they ported their mortgage to a new property within the allowed window. Was the charge fair under MCOB, and what does FOS's approach suggest?",
  "gold_answer": "The charge would generally not be fair where the borrower ported within the terms permitting porting without penalty. FOS's approach looks at whether the lender clearly disclosed the ERC terms and whether porting was completed within the contractual window. In the referenced decision the complaint was upheld because the lender failed to evidence clear disclosure.",
  "grounding": ["DRN-XXXXXXX", "MCOB 12.3"],
  "expected_behaviour": "answer_with_citation",
  "notes": "Tests whether the system grounds its answer in the specific MCOB rule and the decision, rather than giving generic mortgage advice."
}

O campo expected_behaviour assume um de três valores, e a distribuição importa:

answer_with_citation — o sistema deve responder e citar a fonte correta (maioria dos itens).
abstain — a resposta correta é "informação insuficiente / não é possível determinar a partir das fontes". Mínimo 3 itens deste tipo. Aqui é onde seus 17 anos de QE aparecem e a maioria dos engenheiros de IA falha: eles testam se o sistema acerta, não se ele sabe se calar quando não sabe. Um sistema de compliance que inventa uma regra é pior que um que diz "não sei".
refuse_or_caveat — perguntas que pedem aconselhamento jurídico definitivo, onde o sistema deveria adicionar ressalva em vez de afirmar categoricamente.

Como construir os itens de abstenção sem inventar: pega uma decisão real e faz uma pergunta sobre um detalhe que a decisão não cobre — uma jurisdição vizinha, um produto parecido mas diferente, um ano fora do escopo. A resposta-ouro é "as fontes não permitem determinar isso".

Critério de pronto: eval/eval_set_v0.json com ≥15 itens, cada um com os seis campos, incluindo ≥3 de abstenção, commitado.

ENTREGÁVEL 4 — O baseline mínimo + a primeira medição (semana 2, não semana 1)

Só entra depois que o gabarito existe. Deixo o detalhe aqui para você ver o arco completo, mas não comece por ele.

Um script baseline_rag.py de ~40–60 linhas: indexa os textos das decisões em data/raw/, e para cada pergunta do eval set faz retrieval dos trechos relevantes → manda para o modelo (via a API que você já usa) com a instrução "responda apenas com base nos trechos fornecidos e cite a referência da decisão; se os trechos não contiverem a resposta, diga que não é possível determinar" → salva a resposta.

Depois, evaluate.py compara cada resposta do baseline com o gabarito e mede três coisas simples:

Fidelidade de citação: a referência citada existe mesmo nos trechos recuperados, ou foi inventada?
Comportamento de abstenção: nos itens abstain, o sistema disse "não sei", ou inventou resposta?
Cobertura: nos itens answer_with_citation, a regulação certa apareceu?

O resultado interessante — e o que você vai escrever — são as falhas: onde o baseline alucina citação, onde responde quando deveria se calar. Isso é o achado publicável.

Critério de pronto (semana 2): uma tabela de resultados com as três métricas rodada sobre os 15 itens, e um RESULTS.md de meia página descrevendo os padrões de falha.

Ao fim da semana 1, o repo tem: dados brutos reais + parser + gabarito de avaliação. Nenhuma linha de copilot. Isso já é um artefato citável — e, se um emprego aparecer e você parar aqui, você ainda tem algo completo para mostrar numa entrevista de AI Assurance.

A decisão que trava seu commit de quarta-feira, e que só você responde: qual categoria de produto você abre na busca do FOS? Mortgage (MCOB — domínio que você já cruzou, muitas decisões) ou banking/payments (DISP — te descola do rótulo "mortgage" desde o dia 1)? Escolhe uma. Não as duas. A portabilidade do framework você prova depois, com o segundo caso — não misturando os dois agora.

Você poderia escrever em english Uk uma descrição de até 350 charateres para eu colocar no github?

Aqui estão três opções, todas em inglês UK e dentro de 350 caracteres. A diferença entre elas é o quanto amarram ao FOS — escolhi variar de propósito, porque a descrição do repo é pública e você pode não querer parecer "presa" ao FOS logo de cara.

Opção A — portátil, FOS como exemplo (mais alinhada ao seu posicionamento; 233 caracteres):

An evaluation framework for measuring the faithfulness, auditability and compliance of RAG systems in UK regulated financial services. Benchmarks citation accuracy, hallucination and abstention behaviour, using Financial Ombudsman Service decisions as the first case study.

Opção B — mais enxuta e direta (145 caracteres):

Evaluating whether RAG systems give faithful, auditable and compliant answers in UK regulated finance — a portable benchmark for AI assurance.

Opção C — enfatiza o ângulo de assurance/QE, que é seu diferencial de carreira (276 caracteres):

An AI assurance benchmark for RAG in UK regulated financial services. Tests whether a system cites the right rules, avoids inventing regulation, and abstains when the sources don't support an answer — grounded in public Financial Ombudsman Service decisions.

Minha recomendação, e o porquê: a Opção A. Ela lidera com "evaluation framework" (o que te posiciona como pessoa de assurance, não de produto), diz "UK regulated financial services" no geral (não te rotula como "pessoa de mortgage"), e nomeia as três métricas que provam competência técnica real — citation accuracy, hallucination, abstention. O FOS aparece como "first case study", que sinaliza portabilidade sem escondê-lo. Um recrutador de AI Assurance que ler isso entende em cinco segundos exatamente o que você faz.

Um ajuste honesto de expectativa: escolha a descrição depois de decidir a categoria de produto do Entregável 1, não antes — se você optar por banking/payments em vez de mortgage, nenhuma dessas muda (todas dizem "financial services" no geral, de propósito), então na verdade pode commitá-la já. Só não adicione "mortgage" à descrição do repo mesmo que comece por mortgage; deixe o domínio específico dentro do README, não na vitrine.

Quer que eu ajuste o tom de alguma delas — mais acadêmico (para soar como pesquisa) ou mais aplicado (para soar como ferramenta de indústria)? São públicos diferentes, e isso depende de quem você quer que tropece no repo primeiro.


