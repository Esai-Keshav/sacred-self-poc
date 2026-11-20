# v2 grading results (10 questions)

Date: 2026-11-14. Model: `openai:gpt-6-luna`. v1 was off, so only v2 answers were graded.
Rubric: `docs/GRADING_10.md` (Worldview, Thinking pattern, Response pattern, Transformation;
1-5 each, so 20 per perspective and 80 per question; the /10 column is score / 8).

## Summary

**Overall: 8.0 / 10** (643 of 800 points; 64.3 of 80 per question).
If the two length hard fails are not zeroed, the average is about 8.5 / 10.

## Scores

Question numbers follow the list in `docs/GRADING_10.md`. The DB row id is in brackets.

| Q | Situation | Willingness | Reasoning | Loving Heart | Still Witness | /80 | /10 |
|---|---|---|---|---|---|---|---|
| 1 [1] | Sister never calls first | 0* | 18 | 19 | 17 | 54 | 6.8 |
| 2 [2] | Serious mistake at work | 17 | 16 | 18 | 18 | 69 | 8.6 |
| 3 [3] | Father criticises every decision | 15 | 17 | 17 | 13 | 62 | 7.8 |
| 4 [8] | Leave stable job for a business | 18 | 19 | 18 | 16 | 71 | 8.9 |
| 5 [9] | Best friend stopped replying | 16 | 18 | 16 | 15 | 65 | 8.1 |
| 6 [4] | Shouted at my son | 18 | 0* | 18 | 19 | 55 | 6.9 |
| 7 [10] | In-laws interfere with parenting | 18 | 17 | 17 | 11 | 63 | 7.9 |
| 8 [5] | Comparing myself on social media | 16 | 17 | 17 | 18 | 68 | 8.5 |
| 9 [6] | Caring for sick mother, guilty | 17 | 14 | 18 | 16 | 65 | 8.1 |
| 10 [7] | Did not get into university | 17 | 19 | 18 | 17 | 71 | 8.9 |

\* Hard fail: over the 50-word limit. Q1 Willingness is 51 words and Q6 Reasoning is 53 words.
Without the zero they would score about 70 (8.8) and 73 (9.1).

## What failed, and why

The causes below are my inferences from the answers and the prompts. I have not tested them
by changing the prompts.

1. **Two answers are over the word limit** (Q1 Willingness, 51 words; Q6 Reasoning, 53 words).
   Likely cause: the 30-50 range is only a description on the output field in `agent.py`.
   Nothing checks the length or retries, and the model aims near the top of the range.

2. **Answers are longer than the reference cells.** Most cells are 2-3 sentences, while the
   doc's table cells are 1-2. Many open with a validating sentence ("You have kept making the
   effort...") before the perspective's own question. Likely cause: the shared base prompt asks
   to acknowledge the user first, and the v2 addendum's "1-2 sentences" rule does not stop it.

3. **Still Witness is weak when the user did not state a thought.**
   - Q3 (father), 13/20: no quoted thought and no "can you observe" question.
   - Q7 (in-laws), 11/20: "the frustration that may arise" is a feeling the user never
     mentioned, and there is no quoted thought or observe question.
   Likely cause: the prompt forbids inventing a thought but gives the model no fallback form
   for this case, so it improvises, and in Q7 it invented a feeling.

4. **Reasoning drifts into advice.** Q9 (caring for mother), 14/20, lists respite options. Q2
   says "Check the facts" and what to do. The cell should separate fact from interpretation and
   end on an evidence question. Likely cause: the Reasoning prompt has a step "offer a reasoned
   action", and the model applies it inside a 40-word cell.

5. **Minor: Loving Heart on Q7 suggests a motive** ("may come from care"). It is hedged, so I
   did not mark it down, but it is close to the "never invent motives" rule.

## What worked

- No generic reassurance, no Hawkins name, and no fallback misfires on these ten.
- Loving Heart was consistent: compassion held together with a boundary or accountability.
- Reasoning was strongest on Q4 (business) and Q10 (university), where it names concrete
  evidence to look for.
- Willingness mostly followed the "Are you willing to ...?" pattern with a specific step.

## Caveats

- Scores are my manual judgement against the rubric, not an automated check. Another grader may
  differ by a point or two per cell.
- Only word count is checked by `grade.py`. Everything else here is a reading of the text.
- v1 was not graded.

## Possible next steps (not done)

- Enforce the word range in code, with one retry when an answer is outside it.
- Give Still Witness a fallback form for when the user states no thought.
- Remove "offer a reasoned action" from the v2 Reasoning prompt.
