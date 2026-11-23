# Grade 3: ten student and young-adult thoughts

## Context
Ten new thoughts run through the live model with `agent._run`. Nothing was saved to Supabase. Prompt version `v4`, model `openai:gpt-6-luna`. Raw output: `scratchpad/cards_grade3.json`. No prompt or code was changed.

## Rule check

Targets from `config.py` and the prompt: hook 20-30 words in two sentences (first 8-10 words, second 14-18), expanded 60-70 words in two paragraphs, about 8 sentences averaging 8 words, practise one sentence with a deadline and one action.

| # | Thought | Hook words | Hook sentences | Expanded words | Exp. sentences (avg) | Practise words | Pass? |
|---|---|---|---|---|---|---|---|
| 1 | Friends placed, I am unemployed | 26 | 11 + 15 (**fail**) | 65 | 6 (10.8) | 11 | No |
| 2 | Failed exam after hard study | 26 | 11 + 15 (**fail**) | 62 | 6 (10.3) | 8 | No |
| 3 | Best friend ignoring me | 26 | 10 + 16 | 65 | 6 (10.8) | 15 | Yes |
| 4 | Everyone smarter than me | 24 | 10 + 14 | 70 | 7 (10.0) | 15 | Yes |
| 5 | Parents compare me | 23 | 12 + 11 (**fail**) | 61 | 6 (10.2) | 12 | No |
| 6 | Backlogs, ruined future | 26 | 11 + 15 (**fail**) | 61 | 7 (8.7) | 11 | No |
| 7 | Crush likes someone else | 22 | 8 + 14 | 69 | 6 (11.5) | 10 | Yes |
| 8 | Group blames me | 23 | 10 + 13 (**fail**) | 59 | 7 (8.4) | 13 | No (expanded 59 is under 60) |
| 9 | Scrolling Instagram | 22 | 9 + 13 (**fail**) | 70 | 6 (11.7) | 14 | No (practise has two tasks) |
| 10 | Lonely among friends | 23 | 9 + 14 | 64 | 7 (9.1) | 11 | Yes |

Passes on every card: total hook words, two paragraphs, no exclamation marks, no gender words, no semicolons, no em dashes, at most one question, no banned stock phrases, practise has a deadline of 1 to 7 days.

## Voice and depth (1-10, judgement)

| # | Score | Why |
|---|---|---|
| 1 | 6 | Hook repeats the message ("friends placed while you are still unemployed"). Opens by restating it. "You have kept going through this uncertain time" is effort the person never wrote. |
| 2 | 7 | Best use of the teaching ("a setback can show where life is shaping you"). Practise is tiny and exact: review one question you got wrong. Hook sentences are 11 and 15, each one word over. |
| 3 | 7.5 | Good "Maybe... or maybe..." run for the friend's reasons. Hook structure is correct. Practise (one calm message) is concrete. "Meet the uncertainty" is close to the banned "meet this moment". |
| 4 | 7 | "What if this feeling points to something you want to learn?" is a real turn. The closer, "not measured by someone else's pace", is a "not this" shape. |
| 5 | 6 | Hook second sentence is only 11 words. "Someone else's pace" does not fit comparison with cousins. Practise asks the person to tell their parents how the comparing lands. That is a charged act for a 12-word line, with no tiny step first. |
| 6 | 6.5 | Gentle and sensible. "One piece at a time" is a stock closer. The "ruined my future" fear is received but not lifted much. |
| 7 | 6 | Practise ("write one thing you value about yourself") is generic. It does not touch "I can't stop thinking about it". Two to three days for a one-minute task is a mismatch. |
| 8 | 6.5 | Practise (list your contributions) is concrete and fits the blame. Expanded is 59 words, one under the minimum. "Their choices do not have to become your burden" is the "not this, that" reveal the guide bans. |
| 9 | 5.5 | Practise joins two tasks with "and": "set a 20-minute study timer and keep your phone out of reach". The prompt says never to. Hook 9 + 13 fails the structure. |
| 10 | 7 | Best practise of the ten: a first-person line to say to one friend. But "it does not mean you are ungrateful" invents a feeling. "I have seen how a little honesty can make room" is a personal claim that is not one of Lakshana's stories. |

Average: **6.5/10**. Grade 2 was 7.6, but on a different set of thoughts, so the two numbers are not a clean comparison.

## What is wrong (patterns across the ten)

1. **Hook structure fails on 6 of 10.** The 8-10 then 14-18 split is in the prompt but not checked in code. Only cards 3, 4, 7 and 10 pass.
2. **Opener restates the message on 10 of 10.** Guide section 5 step 1 bans "Your X did Y, and you feel Z" openers. Every card starts "Your friends are getting placed, and you are...", "You studied so hard, and the result hurts", "Your best friend has gone quiet...", and so on.
3. **"Of course" in 7 of 10 cards** (3, 4, 5, 6, 7, 8, 10). The guide says do not lean on one permission phrase.
4. **"What if" in 6 cards** (4, 5, 6, 7, 8, 9). Each card has one, and it sits in the same place in paragraph 2.
5. **Repeated shapes across cards.**
   - "does not take away your chance" (cards 1 and 4).
   - "pace" as the closing image (1, 4, 5).
   - "one X at a time" closers (2, 4, 6, 9).
   - "You can..." as the last line in 8 of 10.
6. **Hooks repeat the person's message** (1, 4, 6, 8, 9), against the hook rule.
7. **Invented details:** card 1 "kept going", card 10 "ungrateful" and "I have seen".
8. **Practise:** card 9 has two tasks joined by "and". Card 7 is off-topic. Card 5 is too heavy for the energy. "By Friday" or "Within 3 days" is the deadline on 9 of 10, so they read the same.
9. **Expanded sentence length.** The prompt asks for about 8 sentences averaging 8 words. The model writes 6 to 7 sentences averaging 8.4 to 11.7, so the cards read as longer, flatter lines than the spoken rhythm in the guide.

## What is missing

In the prompt:
- No rule on how often a permission phrase or "What if" can be used across cards.
- No example of a hook that does not echo the message, in this exact two-sentence form.
- No guidance for practise on a thought where the problem is a thought loop (card 7) rather than an event.

In the code, nothing enforces these, so the model gets no retry:
- Hook sentence split (8-10, 14-18).
- Expanded minimum of 60 words (`check_expanded` only checks the maximum).
- Practise: one task (no " and " joining two verbs), a deadline, and at most 25 words.
- Expanded opener that restates the message.

In the test set:
- No crisis or fallback thought in these ten, so safety and scope were not exercised.
- Cards 6 and 10 are the nearest to heavier feelings, and both came through as normal cards.

## Tests
`uv run pytest`: 85 passed, 2 failed. The failures are in `tests/test_prompts.py` (`test_v2_guide_sections_in_order` is one). They are not caused by this run, because nothing was edited. I did not look into them further.

## Decisions for you
- [ ] **Hook split:** add a validator check for 8-10 then 14-18 (it will cause more retries), or relax the prompt to a single 20-30 total.
- [ ] **Expanded minimum:** add a minimum check of 60 words next to the maximum.
- [ ] **Practise "and" check:** reject practise lines that join two verbs with "and".
- [ ] **Repeated phrases:** add a short "vary these" list to the prompt (permission phrase, "What if", "one at a time", "pace"), or leave it.
- [ ] **Failing tests:** look at the two `test_prompts.py` failures.
