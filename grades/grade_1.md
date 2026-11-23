# Grade 1: test plan for five new thoughts

## Context
Another test round: five thoughts run through the model, then graded. This is a fresh test, separate from the earlier prompt edits. The prompt is tested as it stands now. That includes the "Depth moves" list, the 4-10 word closing line and the trimmed examples. It does not include the three recommended fixes (ban repeated closers, require one concrete act in `expanded`, change the husband `say_it` example), which are not yet approved.

## The five thoughts
1. Parenting anger: "I shouted at my daughter today over homework and I can't stop feeling like a bad mother."
2. Grief and exhaustion (tests the "tiny step, longest deadline" rule): "My father passed away last month and I'm exhausted all the time."
3. Fear before a decision: "I got a job offer in another city but I'm scared to leave my family and fail."
4. Friendship hurt: "My best friend forgot my birthday and I feel invisible."
5. Comparison and self-doubt: "I keep comparing my progress with my classmates and I feel I'm falling behind."

## Steps
1. Run the five through the live model with `agent._run`, which does not save to Supabase. Write the output to `cards_test5.json` in the scratchpad.
2. Count words and check validator rules with `check_punctuation` and `check_hook_length` from `agent.py`.
3. Grade each card two ways:
   - **Voice and depth, 1-10**: feeling received, teaching woven in, personal warmth, rhythm, closing line. Reference points: the pasted cards scored 8-9; the last regenerated set scored 6-7.
   - **Rule check**: hook 25-30 words, expanded 50-60, practise at most 25 words with a deadline and one action, `say_it` one first-person sentence with no question mark, no banned phrases or foreign terms, and no feelings the person did not state.
4. Look across the five cards for repeated closers or phrasing.
5. Report scores, supporting quotes, and suggested prompt changes. No prompt files are edited in this round.

## Verification
- `uv run pytest` should still pass (46 tests), since nothing in the repo changes.
- Scores are a judgement against the rubric. Voice quality still needs a human read.

## Results

Run on the current prompt, with the live model. Nothing was saved to Supabase. Raw output: `scratchpad/cards_test5.json`.

### Rule check

| # | Thought | Hook (25-30) | Expanded (50-60) | Practise | Validator | `say_it` first-person | Pass? |
|---|---|---|---|---|---|---|---|
| 1 | Shouted at daughter | 25 | 57 | 17 | pass | yes | Yes |
| 2 | Father passed, exhausted | 25 | **64** | 16 | pass | **no**, starts "My father" and is two sentences | No |
| 3 | Job offer, scared | 25 | 59 | 19 | pass | yes | Yes |
| 4 | Friend forgot birthday | 30 | 54 | 18 | pass | yes | Yes |
| 5 | Comparing with classmates | 29 | **61** | 15 | pass | yes | No (length only) |

The validator passes on all five. Card 2's `say_it` is not caught by the validator because the code only checks for a question mark. Our prompt says `say_it` is one first-person sentence, so this breaks the prompt rule, not the code rule.

### Voice and depth (1-10)

| # | Feeling received | Teaching woven in | Personal warmth | Rhythm | Closing line | Overall |
|---|---|---|---|---|---|---|
| 1 | 8 | 8 | 7 | 7 | 6 | 7/10 |
| 2 | 8 | 7 | 7 | 7 | 6 | 7/10 |
| 3 | 7 | 7 | 6 | 7 | 5 | 6/10 |
| 4 | 8 | 8 | 8 | 8 | 8 | 8/10 |
| 5 | 7 | 7 | 7 | 7 | 6 | 7/10 |

Average: 7.0/10. These are judgements against the rubric. Voice still needs a human read.

### Card notes
1. **Shouted at daughter.** Strong concrete act: a gentle apology and a way back to homework. Closer "Your care is still here" is generic.
2. **Father passed.** Best permission in the set ("you do not need to push that feeling away"). The step is tiny and the deadline is long, as the prompt asks. Expanded is 64 words, and `say_it` breaks the first-person rule.
3. **Job offer.** Good reframe: "one question at a time". The hook and practise both ask the person to write things down, so the card repeats its action. Closer "You can meet this thoughtfully" is the weakest. "Not a verdict" is used again.
4. **Friend forgot birthday.** Best card. "Your worth is not decided by one forgotten birthday" separates the event from the person. The `say_it` uses the person's own word "invisible". Hook is at the 30-word cap.
5. **Comparing with classmates.** "Their own way of shining" is taken from the teachings, which is fine. Expanded is 61 words. The closer "Your pace is still yours" repeats the pattern from the last round.

### Across the set
- **Closer template:** three of five close on "Your X is still Y" or similar ("Your care is still here", "Your pace is still yours", "Your voice matters"). The problem from the last round is still there.
- **"Verdict" appears twice** (cards 3 and 4 use the same "not a verdict" idea). This is the same word-choice problem the prompt warns about.
- **Practise-hook overlap:** card 3 hook and practise both say "write down". Card 5 hook and practise both say "write down one step".
- **Length overshoot:** 2 of 5 expanded texts are over 60 words, the same pattern as the earlier runs.

## Feedback (for you to decide)

I have not changed any prompt or code. These are options, not applied changes.

1. **Fix the closer template.** Add a rule to `prompt/willingness.md`: do not end on "your X is still Y" or "your X matters". Close on a concrete image or act from the card. This addresses the biggest repeated flaw.
2. **Fix `say_it` on grief-type cards.** Tell the model that `say_it` is always one sentence starting with "I" or "I'd". This is a prompt rule, since the validator does not check it. Optionally, add a validator check for the first-person start too.
3. **Tighten expanded length.** Two cards overshot. Options: state "aim for the middle of the range" in the prompt, or add a validator check for expanded length with a retry.
4. **Reduce repeated actions.** Ask that the hook names the reframe and the practise names the act, so the same verb does not appear in both.
5. **Keep as is:** the "Depth moves" list is working. Cards 2 and 4 show the permission and separation moves landing well.

## Decisions for you
- [ ] Apply fix 1 (closer rule)?
- [ ] Apply fix 2 (`say_it` first-person rule in the prompt, and/or a validator check)?
- [ ] Apply fix 3 (length: prompt wording, or validator retry)?
- [ ] Apply fix 4 (hook and practise should not repeat the same verb)?
- [ ] Rerun the five thoughts after any approved fixes, to compare against this round?

Tell me which to apply. I won't change the prompt until you do.
