# Grill a spec: make a draft spec's foggy parts explicit before it is ready

Use this on a spec in `specs/` that is still `draft`, or that a partner is about to set to `ready`. If no spec is named, ask which one.
Before asking anything, read the spec, `specs/00-project.md` and `data/README.md` in full. Learn about the data only with `scripts/inspect_data.py`.

Ask the five hardest questions about the spec, one at a time, in this order:

1. Assumptions: what does the spec take for granted?
2. Data: does the data it needs exist, is it accessible, and is it clean enough?
3. Falsification: what result would show the approach is wrong?
4. Feasibility: what is the smallest check that could run this week?
5. Scope: what is explicitly out of scope?

Ask one question, then wait for the answer. If an answer is vague, ask a follow-up on that point before moving on.
Use plain language: the partner may not write code.

When all five are answered, add a block under the spec's **Open questions**, headed `Grill YYYY-MM-DD`, with:

- each answer, in the partner's words;
- suggested acceptance criteria that a test or eval could check, written as `DATA-004 (suggested): ...` with the next unused ID. Do not bold them: bold IDs count as real criteria. The partner copies the ones they want into **Acceptance criteria**;
- **Still foggy:** every point that was not clearly answered. Do not mark these resolved.

Do not edit any other part of the spec, change its Status, or write code.
