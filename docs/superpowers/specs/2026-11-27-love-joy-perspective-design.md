# Love & Joy perspective

## Goal

One message gives two cards: Willingness first, Love & Joy second. The reader sees one situation in two different ways.

## Decisions

- Two concurrent model calls, one per perspective.
- Same card shape and validators for both.
- Love & Joy uses `language_common.md` and `love_joy.md` only. The v5 voice guide and examples stay Willingness only.
- `cards.perspective` stores which perspective wrote each row.
- If one call fails, the other card is shown with a warning.

## Known limits

- Token cost roughly doubles.
- A crisis message shows two similar crisis cards.
- History's 50-row limit covers about 25 messages.
