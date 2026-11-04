# CLAUDE.md

## What this project does and why
AI Fraud-Review Copilot is an agent that takes a flagged transaction, retrieves relevant fraud-pattern knowledge via RAG, pulls customer and merchant context through tool calls, and drafts a structured case note with a recommendation. It never makes the final call — every note is routed to a human analyst for decision. The goal is to cut the manual triage time fraud/risk analysts spend writing these notes by hand, while keeping the reasoning consistent and auditable for compliance.

## Architecture at a glance (five stages)
1. **Flag** — rule-based flagger tags a transaction (amount spike, new merchant category, geo anomaly, velocity).
2. **Retrieve** — RAG pulls the relevant fraud-pattern doc from the Chroma knowledge base.
3. **Tool calls** — agent calls `lookup_customer_history(customer_id)` and `lookup_merchant_info(merchant_id)`.
4. **Generate** — agent drafts a structured case note (risk factors, evidence, recommendation, confidence) via the Google Gemini API (`google-genai`).
5. **Guardrail** — output is checked before returning: no definitive fraud claims, PII redacted.

Automated end to end except the final decision — the analyst always makes the call.

## Where things live
fraud-review-copilot/
├── data/
│ ├── generate_data.py # builds the synthetic dataset
│ ├── transactions.csv
│ ├── customers.csv
│ └── merchants.csv
├── knowledge_base/
│ ├── card_not_present.md # amount-spike evidence (repurposed — see below)
│ ├── account_takeover.md # new-category evidence (repurposed — see below)
│ ├── velocity_fraud.md # velocity_spike evidence
│ └── geo_anomaly.md # geo_anomaly evidence
├── src/
│ ├── schemas.py # CaseNote model + Recommendation enum
│ ├── flagger.py # rule-based flagging
│ ├── retrieval.py # embeddings + Chroma lookup
│ ├── tools.py # lookup_customer_history, lookup_merchant_info
│ ├── agent.py # orchestration: retrieve → call tools → generate
│ ├── guardrail.py # PII redaction + language constraints
│ └── api.py # FastAPI app
├── eval/
│ ├── eval_set.json # 19 hand-labeled cases
│ └── run_eval.py # scores the agent against eval_set.json
└── tests/


Note: `card_not_present.md` and `account_takeover.md` are named for their standard fraud-ops meaning but written to ground `amount_spike` and `new_merchant_category` evidence respectively, since those two flag reasons had no directly-named pattern doc. Retrieval matches on content, not filename, so this is intentional — not a mismatch to fix.

## How to run it locally
```bash
# install deps
pip install -r requirements.txt

# generate synthetic data (first run only)
python data/generate_data.py

# run the rule-based flagger (fills in flag_reason)
python src/flagger.py

# embed the knowledge base into Chroma (first run only, or after editing a doc)
python src/retrieval.py

# draft a case note for one transaction (manual check)
python -m src.agent <transaction_id>

# run the API
uvicorn src.api:app --reload

# call it
curl -X POST localhost:8000/review/{transaction_id}

# run the eval set against the agent (paces calls to stay under the
# model's free-tier requests-per-minute cap -- see run_eval.py for why)
python -m eval.run_eval
```

## Conventions to keep
- Always run `python -m eval.run_eval` before committing a prompt or retrieval change — a prompt change that tanks eval accuracy should be caught before it's pushed.
- Guardrail checks are code-level (regex/rule), not just prompt instructions — never remove or weaken this in favor of a prompt-only fix.
- Keep tool calls (`tools.py`) deterministic and boring — they simulate backend systems, not model logic.
- No real financial data or real PII enters this repo at any point — synthetic data only.
- Branch + PR for every change, even solo — real PR descriptions, not placeholders.
- Flagger thresholds are tuned against the actual generated data's trigger rates, not picked abstractly — re-check counts after any regeneration (e.g. after editing `generate_data.py`, flag distribution can shift even with the same rule logic).
- Retrieval queries must be natural-language phrasings built from the flag reason, not the raw `flag_reason` string — confirmed via manual testing (Day 2) that enum strings retrieve incorrectly for at least one flag type.
- Scripts that import from other `src/` modules (`agent.py` and beyond) must be run with `python -m src.<name>`, not `python src/<name>.py` — only standalone scripts with no cross-module imports (`flagger.py`, `retrieval.py`, `tools.py`) support the direct form. This applies to `eval/run_eval.py` too: run as `python -m eval.run_eval`.

## Known gaps (dated)
- **Eval accuracy, 2026-11-05: 18/18 (100%) on the original 18 cases in a full local run; 6/6 on the CI subset (GitHub Actions run 41916910504). Meets SCOPE.md's 80% bar.** Up from **61.1% (11/18) on Day 4** (`geo_anomaly` 4/5, `velocity_spike` 3/4, `amount_spike` 3/5, `new_merchant_category` 1/4). The gain has two sources, reported separately:
  - **Agent got better (prompt fix in `src/agent.py`):** two instructions were added — compare earlier purchase sizes before treating a familiar merchant as reassuring, and let a risk factor that matches a reference pattern meaningfully affect the recommendation. This fixed T0078 (familiar merchant read as reassuring) and T0133 (28-day-old account recognized as a risk, then cleared anyway).
  - **Answer key changed:** T0143 was relabeled escalate -> clear on Day 6 (Action 23) after the agent's own evidence showed C026 already had purchases above the $89.12 ceiling. Scored against the original label, the same run is 17/18. The reasoning for the relabel was replaced on 2026-11-05 (see the T0143 entry below); the label itself did not change.
  - **Not attributed:** T0071 passed on a rerun with no fix, so it is treated as ordinary variation. The Day 4 misses T0091 and two others were never named in the record, so how they were fixed is unknown. The Day 4 `eval_set.json` was never committed, so other label changes between Day 4 and now can't be ruled out.
  - Scores vary between runs (T0018 once failed after the prompt change, then passed; confidence on T0133 was 0.65 and 0.75 on two runs). Treat 18/18 as one good run, not a guarantee. CI tolerates one miss in 6.
- **T0143 label re-derived 2026-11-05 (still `clear`, now a documented close call).** The Day 6 reasoning leaned on T0063 and T0125 as proof of normal spending, but both were flagged and unreviewed. The label was re-derived from the transaction data alone (1.55x ceiling, home location, familiar low-risk merchant, no second signal) and stays `clear`, consistent with T0078 and T0014. Caveat: the person re-deriving it had already seen the agent clear it, so this is not a fully blind label; review it. It no longer conflicts with T0081, which treats the T0063 cluster as suspicious.
- **T0081 (`velocity_spike`, escalate) currently FAILS — added 2026-11-05, the first velocity escalate case.** Before it, all 4 velocity cases were `clear`, so nothing tested escalating a real burst. T0081 is the third transaction for C026 in about 16 hours, across three locations and three merchants, with T0063 ($164.50) above the customer's ceiling. The agent cleared it (0.85) while listing "burst of activity" and "location mismatch" as risk factors; its evidence text discussed only T0081's own amount and merchant and never mentioned the earlier transactions. With T0081 the full eval is 18/19 (94.7%). It is not in the CI subset, so CI is unaffected. Root-cause or re-examine the label before changing the prompt, and run the full eval after any prompt change.
- **Evidence text can contradict the recommendation.** On T0133 the note listed one reason to escalate and several reasons the transaction looks normal ("However..."), so an analyst may wonder why it escalated. Not fixed.
- **Missing spaces in generated evidence** ("Thetransaction", "merchantis") seen once on the Render deployment, not locally. Not caused by `redact_pii`: it only substitutes name parts with `[CUSTOMER]` and never deletes characters (checked 2026-11-05), so this is model output. Cosmetic; not fixed.
- **The deployed API has no authentication.** Anyone with the Render address can call `/review/{transaction_id}` and spend the Gemini quota.
