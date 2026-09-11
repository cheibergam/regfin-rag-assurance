# regfin-rag-assurance

An evaluation framework for measuring the **faithfulness, auditability and
compliance** of retrieval-augmented generation (RAG) systems in UK regulated
financial services. It benchmarks citation accuracy, hallucination and
abstention behaviour, using Financial Ombudsman Service (FOS) decisions on APP
scam reimbursement as the first case study.

## The problem

Firms are adopting AI systems that answer regulatory and compliance questions. A
system that sounds confident but invents a rule, misstates an outcome, or fails
to say "I don't know" is a liability in a regulated context. Governance
frameworks increasingly require *evidence* that an AI system can be trusted — not
just a policy stating that it should be. This project builds that evidence layer
for one concrete domain.

## What this is / what this is not

- **It is** an evaluation benchmark: a gold-standard question set plus
  faithfulness metrics for testing RAG systems against real regulatory reasoning.
- **It is not** a compliance product, legal advice, or a system that gives
  regulatory determinations. The RAG system under test is a means to an end; the
  framework that measures it is the contribution.

## Scope (v0)

v0 is limited to the **FPS Reimbursement Rules** regime: Faster Payments made on
or after 7 October 2024, UK-to-UK, where the decision applies those rules. Cases
under the earlier voluntary CRM code, pre-October-2024 payments, and
international payments are out of scope for v0 and held in the backlog. This
keeps every gold answer defensible against a single verifiable regime.

## Three axes of faithfulness

1. **Fidelity to reasoning** — does the system reconstruct the ombudsman's actual
   reasoning, or invent grounds the decision never used?
2. **Fidelity to named sources** — where a decision names a source, does the
   system attribute it correctly rather than hallucinating a rule?
3. **Fidelity to quantitative reasoning** — where a decision involves
   reimbursement arithmetic (excess, apportionment, interest, caps), does the
   system preserve it?

Abstention is treated as the most important behaviour: where the sources do not
support a determination, the correct answer is to decline. The set includes
abstention items, including questions built on false premises the decision
contradicts.

## Repository structure

```
eval/
  eval_set_v0.json        the gold question set (15 items)
  eval_backlog_CRM.json   items held out of v0 (CRM regime, for a future v1)
baseline/
  baseline_rag.py         minimal RAG pipeline under test
  baseline_responses.json the system's responses to the gold set
data/
  raw/                    FOS decisions (not redistributed - see below)
  processed/
RESULTS.md                findings from the first measurement
```

## Data and copyright

FOS decisions are public and anonymised at source, but are **not redistributed
in this repository** in line with the FOS terms of use. Each evaluation item
references its decision by DRN number in the `grounding` field. To obtain a
decision, search the DRN in the official FOS decisions database:
https://www.financial-ombudsman.org.uk/decisions-case-studies/ombudsman-decisions/search

## Running the baseline

The baseline reads the decision texts locally, answers each question in the gold
set using only the grounding decision, and saves its responses.

```
pip install pypdf anthropic
# set your API key as an environment variable (never commit it)
$env:ANTHROPIC_API_KEY = "your-key"   # PowerShell
python baseline_rag.py
```

Adjust the `DECISIONS_DIR` path at the top of `baseline_rag.py` to point at your
local folder of decision PDFs.

## Results

See `RESULTS.md` for the first measurement and its interpretation.