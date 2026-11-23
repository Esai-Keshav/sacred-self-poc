# Grade 2: same five thoughts after the closer, length and paragraph changes

## What changed since grade 1
- `expanded`: target raised to 60-70 words, in 2-3 paragraphs separated by a blank line.
- Closer: must be built on a concrete image or act from the card. The "Your X is still Y" closers are banned.
- Examples and the Depth moves list were updated to match. `say_it` was left alone, as you asked.
- Tests: 47 pass, including a new check that examples have 2-3 paragraphs.

## Results (live model, no Supabase saves). Raw output: `scratchpad/cards_grade2.json`

| # | Thought | Hook (25-30) | Expanded (60-70) | Paragraphs | Practise | Validator | Closer |
|---|---|---|---|---|---|---|---|
| 1 | Shouted at daughter | 25 | **79** | 2 | 20 | pass | "Open that door gently." |
| 2 | Father passed, exhausted | 29 | **75** | 2 | 23 | pass | "One small step is enough for now." |
| 3 | Job offer, scared | 29 | **84** | 2 | 22 | pass | "Let one honest page steady your next step." |
| 4 | Friend forgot birthday | n/a | n/a | n/a | n/a | **no card** (see below) | n/a |
| 5 | Comparing with classmates | 28 | **74** | 2 | 16 | pass | "Put one foot on your own path." |

### Checks that passed
- **Closers:** none of the four cards use the "Your X is still Y" shape. Each closer names a concrete act or image.
- **Paragraphs:** every expanded text has exactly two paragraphs.
- **Hooks:** all are within 25-30 words.
- **Practise:** all have a deadline and one action, 16-23 words.

### Checks that failed
1. **Length overshoot (4 of 4).** Expanded runs 74-84 words against the 60-70 target. The model overshoots by 10-15 words. In grade 1, with a 50-60 target, it wrote 54-64. The validator does not check expanded length, so nothing catches it.
2. **Friend card failed once.** The model used up its retries, so no card was returned. A rerun of the same thought worked. The cause is not confirmed. It looks intermittent. The same failure happened on the crisis case in an earlier run.
3. **`say_it` card 2 starts "My father passed away..."** and is two sentences. You asked to leave `say_it` alone, so I have not changed it. Card 1 uses a curly apostrophe ("I’m"), which my checker counts as not first-person. The sentence is first-person, so that is a checker false negative, not a card problem.

## Voice and depth (1-10, judgement against the rubric)

| # | Feeling received | Teaching woven in | Personal warmth | Rhythm | Closing line | Overall |
|---|---|---|---|---|---|---|
| 1 | 8 | 8 | 8 | 8 | 8 | 8/10 |
| 2 | 8 | 7 | 7 | 8 | 7 | 7.5/10 |
| 3 | 8 | 8 | 8 | 8 | 9 | 8/10 |
| 5 | 7 | 7 | 7 | 7 | 8 | 7/10 |

Average over the four cards: about 7.6/10, up from 7.0 in grade 1. Card 3 has the best closer in the set: "Let one honest page steady your next step."

### Card notes
1. **Daughter.** The step is concrete: say sorry, then listen. "It does not make you a bad mother" lands. The closer is a short imperative, which avoids the template.
2. **Father.** The step is tiny, as the prompt asks. "Rest or a meal" is a gentle, specific act. The say_it issue above applies.
3. **Job offer.** The hook is the strongest line: "Fear can sit beside a willing heart; it does not have to choose for you." The closer uses a clear image.
4. **Comparing.** "Put one foot on your own path" is a good image closer. The hook repeats the expanded idea ("does not take yours away"), which is a small redundancy.

## Feedback
- The closer change worked. The template from grade 1 is gone.
- The paragraph split reads well on screen, since each card has a clear break.
- The main problem now is length. The prompt range is not being followed, and the validator does not enforce it.
- The occasional total failure (no card) is a reliability issue. It matters more than voice, because the user gets nothing.

## Decisions for you
- [ ] **Length:** choose one.
  - (a) Add an expanded-length check to the validator, with a retry if it is over 70. This enforces the range, but may cause more retry failures like the friend case.
  - (b) Tell the model to aim for 62-66 words in the prompt. No code change, but it is not enforced.
  - (c) Accept what the model writes and set the range to about 70-85 in `config.py`.
- [ ] **Friend-card failure:** investigate the retry cause and raise the retry limit, or leave it as is. I haven't confirmed the cause yet.
- [ ] **`say_it`:** leave it as is, or change the rule to always start with "I" (you asked to leave it alone, so I have not changed it).

I haven't changed any prompt or code in this round beyond the approved plan.
