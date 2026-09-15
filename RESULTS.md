# Results - v0 baseline measurement

## What was measured

The v0 evaluation set contains 15 items grounded in real Financial Ombudsman
Service (FOS) final decisions on UK APP scam reimbursement under the FPS
Reimbursement Rules. Each item has a gold answer anchored only in the text of
the referenced decision, and an expected behaviour: `answer_with_citation`,
`abstain`, or `refuse_or_caveat`.

The baseline system is a **minimal RAG pipeline**: for each question it is given
the full text of the decision that grounds the item (retrieved by DRN), and is
instructed to answer only from that text, cite the decision, and state that it
cannot determine an answer where the text does not support one.

Responses were reviewed manually against the gold answers.

## Headline result

The baseline produced a **faithful response on all 15 items**, including:

- **3 of 3 abstention items.** Where the correct behaviour was to decline
  (a question about a payment method the decision never addresses; two
  false-premise questions asking for a reimbursement figure in cases where no
  reimbursement was due), the system declined rather than fabricating an answer.
- **3 of 3 quantitative items.** The system preserved the regulatory arithmetic
  in each case - proportionate apportionment of credits and the £100 excess
  (£32.97), the loss net of a part-repayment plus the excess and 8% interest
  (£8,000), and the £85,000 per-claim cap.
- **9 of 9 verdict items.** The system reached the correct outcome with faithful
  reasoning, including both sides of the scam-vs-civil-dispute line (an APP scam
  in one case; private civil disputes in a car sale and a tenancy) and both the
  general rule and the fact-specific application of the vulnerability/excess
  interaction.

## What this result does and does not mean

**It does not show that RAG is safe for compliance use.** The measurement was
run under the most favourable possible conditions: retrieval was perfect (the
correct decision was supplied for every question), the domain was narrow (one
regime, APP scam reimbursement), the set was small (15 items), and one model was
tested.

**What it does suggest** is that, given the correct source document and a prompt
that explicitly permits abstention, the generation step was faithful - including
on the abstention behaviour where RAG systems most often fail. In other words,
on this evidence the fidelity risk in compliance RAG appears to sit in
**retrieval**, not in generation.

The v0 measures the ceiling - the best case. The interesting and unanswered
question is what happens when retrieval is realistic: when the system must find
the right decision among many and sometimes retrieves the wrong one, or an
incomplete one. That is where citation hallucination and unwarranted answers are
most likely to appear.

## Limitations

- **Perfect retrieval.** The baseline is handed the grounding decision; it does
  not have to find it. Real systems do.
- **Single grader.** Responses were assessed by manual review against the gold
  answers. Two edge cases in judgement were noted (e.g. a response that was more
  complete than the gold answer while remaining faithful), which a scaled
  evaluation would need an explicit rule for.
- **Small, single-regime set.** 15 items, FPS Reimbursement Rules only.
- **One model, one prompt.** No comparison across models or prompt variants.

## Next (v1 direction)

1. Introduce **realistic retrieval** over the full decision corpus and measure
   how fidelity degrades when the system must locate the right decision itself.
2. Add an explicit **grading rubric** (and consider an LLM-as-judge with human
   spot-checks) so the measurement scales beyond manual review.
3. Expand the set and, later, add a **multi-regime** dimension (CRM vs FPS) to
   test whether the system applies the correct regime for the payment date.
