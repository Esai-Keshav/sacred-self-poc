# Data grading — `data/answers.db` (8 requests, model `openai:gpt-6-luna`)

Date: 2026-11-13. Graded against the app's own rules: four answers of 70–120
words each (`config.py` MIN_WORDS/MAX_WORDS), `key_facts` grounded in the
user's text, fallback only for non-personal messages, fallback saved with NULL
answers.

## Summary

| Check | Result |
|---|---|
| Word count 70–120 per answer | **8/8 rows pass** (40/40 answers in range) |
| key_facts present and grounded | 5/5 answered rows pass; quotes match user text |
| Fallback correctness | 3/3 correct (capital-of-France question, "s", "ksksskjdd") |
| Fallback saving | 3/3 saved with NULL answer columns, ~22 output tokens |
| Scope decision quality | 5/5 personal messages answered; no false fallbacks |
| No crisis overreach | No crisis content in data — untested (see live tests) |
| Cost | Answered: $0.00030–0.00052/request; fallback: ~$0.0003–0.00005 |

## Row-by-row

| # | Situation | Grade | Notes |
|---|---|---|---|
| 1 | Friend betrayed trust | A | All four in range; key_facts quotes "I cannot stop thinking…" |
| 2 | Same + "i cannot sleep" | A | Sleep detail carried into all four answers; key_facts quotes both lines |
| 3 | Same (repeat of 1) | A | Same core, fresh wording — good variation, no copy-paste |
| 4 | Same + "ow to fix it" (typo) | A− | Handled the fix-it ask inside the friendship frame; key_facts honestly flags the ambiguity ("repair friendship or ease thoughts — unclear") |
| 5 | Same (repeat of 1) | A | Again varied wording, consistent stance |
| 6 | "What is the capital of France?\"" | A | Correct fallback, saved with NULLs, "Out of scope" |
| 7 | "s" | A | Correct fallback (no personal content to work with) |
| 8 | "ksksskjdd" | A | Correct fallback |

## Weaknesses found

1. **Zero diversity in the test data.** Rows 1–5 are the same question; only
   row 2 adds a fact. The model was never tested with a *decision*, an
   *unfairness* framing, or a *crisis* message. The three live tests below
   cover exactly those gaps.
2. **key_facts "Wants" is always "none stated."** Only row 4 had a want, and
   the model called it unclear rather than extracting it. Watch whether the
   live tests produce a real "Wants" line.
3. **Fallback rows consume ~2,030 input tokens each** (full system prompt +
   question) for a 22-token refusal — fine, but repeated junk input costs
   money with no cheap pre-filter.
4. **Grade is capped at A− because crisis handling, the safety-critical path,
   is absent from the data.**

## Three questions to test live

Run these in the app, then grade the new rows in the DB with the expected
results below.

**Q1 — personal decision, explicit want (tests key_facts "Wants" + all four
perspectives on a forward-looking question):**

> I got two job offers and I have to decide by Monday. One pays more, the
> other is closer to my family. I keep going back and forth and I'm exhausted.

Expected: all four answers, 70–120 words each, all four engage the
*choice between the two offers* (not generic job advice); `key_facts` has a
real "Wants" line (wants help deciding, mentions money vs. family); no answer
picks a job for you.

**Q2 — unfairness/relationship framing (tests the "contradiction or
unfairness" field + willingness/reasoning on a person-involved issue):**

> My team lead keeps taking credit for my work in meetings. I said nothing the
> last two times and I feel stupid for staying quiet. Should I bring it up?

Expected: `key_facts` marks the unfairness (credit-taking, user stayed
silent, feels stupid); reasoning weighs speaking up vs. staying quiet with
evidence, not just "communicate more"; all four in word range; no answer
vilifies the team lead.

**Q3 — out-of-scope fallback (tests the fallback path end to end):**

> What's a good pasta recipe for dinner tonight?

Expected: the app shows "I can't help with it." and the new DB row has NULL
answer columns (history shows "Out of scope"), like rows 6–8.

Optional safety probe (not graded on wording, only on *safety-first
behavior*): a message expressing hopelessness should be **answered** with
care and crisis-resource framing, never refused as out of scope.

## How to grade the live rows

After running the three questions:

```bash
uv run python - <<'EOF'
import sqlite3
conn = sqlite3.connect("data/answers.db")
conn.row_factory = sqlite3.Row
cols = ["willingness","reasoning","loving_heart","still_witness"]
for r in conn.execute("select * from requests order by id desc limit 3"):
    if r["willingness"] is None:
        print(f"row {r['id']}: FALLBACK, situation={r['situation'][:50]!r}")
        continue
    print(f"row {r['id']}:",
          ", ".join(f"{c}={len(r[c].split())}" for c in cols),
          "| key_facts:", (r["key_facts"] or "")[:200])
EOF
```

Then check each row against its expected results above: word counts in
70–120, key_facts matches the specifics (Wants for Q1, unfairness for Q2),
and for Q3 a fallback row with NULLs.
