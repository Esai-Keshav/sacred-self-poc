from datetime import datetime
from pathlib import Path

import config

PROMPT_DIR = Path(__file__).parent / "prompt"

# Rules shared by every perspective. Each perspective adds one <name>.md file.
COMMON_FILE = "language_common.md"
PERSPECTIVE = "willingness"

LANGUAGE_FILES = {
    "v1": "language_v1.md",
    "v2": "language_v2.md",
    "v4": "language_v4.md",
}

# Placed above the language guide so the model knows which rules win when they clash.
PRECEDENCE = (
    "The guide below sets wording and tone only. If it conflicts with Who you are, Safety, "
    "Scope, Grounding or Card fields above, those win. Example responses inside the guide "
    "show voice only; their length, number of questions and layout do not apply."
)

EXAMPLES: list[dict] = [
    {
        "thought": "My husband doesn't appreciate anything I do for the family.",
        "expanded": (
            "Feeling unseen after years of giving quietly is a real ache, and it shows how much "
            "you care. Wanting to be noticed is a fair need, not a weakness.\n\n"
            "Your part is speaking what you need, calmly and clearly. How your husband responds is not yours "
            "to carry. You do not have to wait for the perfect moment, only a calm one.\n\n"
            "One clear sentence can open a door."
        ),
        "hook": (
            "Your giving has been steady, and it hurts to feel unseen. Strength grows when you "
            "ask for what you need, one clear sentence at a time."
        ),
        "practise": (
            "In 3 days, choose one calm moment and tell your husband one thing you would like noticed."
        ),
    },
    {
        "thought": "My colleague got promoted instead of me. I feel jealous and inferior.",
        "expanded": (
            "Jealousy and feeling small are heavy, and they show how much you care about growing. "
            "One promotion does not decide your worth. Your colleague's rise has not taken anything "
            "from you.\n\n"
            "You can still learn even from the people you envy. Look at what they do well, "
            "and learn from it without comparing. Then ask your manager what ready looks like.\n\n"
            "Keep your own light steady today."
        ),
        "hook": (
            "Jealousy shows where your heart is ready to grow. Notice one clear thing your "
            "colleague does well this week, and let it steady you today."
        ),
        "practise": (
            "Within 5 days, ask your manager what a strong case for the next level would look like."
        ),
    },
]

# Same thoughts as EXAMPLES, in the spoken v4 voice. Examples sit last in the prompt,
# so old-voice examples would pull the model away from the v4 guide.
EXAMPLES_V4: list[dict] = [
    {
        "thought": EXAMPLES[0]["thought"],
        "expanded": (
            "The day ends. The work is done. And nobody mentions it. After enough evenings "
            "like that, you start to wonder if anyone is looking. There is nothing wrong in "
            "wanting a thank you.\n\n"
            "Maybe your husband has stopped noticing. Maybe the words do not come easily. "
            "How your husband responds is not yours to carry. But your need can stay soft "
            "and steady, without any fight at all."
        ),
        "hook": (
            "Wanting to be seen is not a weakness. You have cared for this family, and what "
            "you need deserves a place in it too."
        ),
        "practise": "In 3 days, tell your husband one thing you would like noticed.",
    },
    {
        "thought": EXAMPLES[1]["thought"],
        "expanded": (
            "Each time that new title comes up, you feel smaller. You wanted to grow too. "
            "There is no shame in feeling jealous about that.\n\n"
            "Their rise has not taken anything from you. And look closely, because jealousy "
            "points to what you want next. Even the person you envy can teach you something. "
            "You have time to find your own way here."
        ),
        "hook": (
            "Jealousy only shows how much you care about growing. Another person's promotion "
            "has not closed your road, and there is still plenty for you to learn."
        ),
        "practise": EXAMPLES[1]["practise"],
    },
    {
        "thought": "My son is in Class 9 and refuses to study. Every evening ends in a fight.",
        "expanded": (
            "Evening comes and the books come out. Within minutes, the voices go up. And the "
            "fight stays with you long after. There is no shame in being worried for your "
            "child.\n\n"
            "Maybe your son feels the pressure more than the lessons. Maybe something in class "
            "has become hard. When we push a river, it pushes back. You can keep caring and "
            "loosen your grip a little."
        ),
        "hook": (
            "Your worry comes from how much you love your child. A calmer home can hold that "
            "worry, and your son can feel safe enough to try."
        ),
        "practise": "By Thursday, ask your son which subject feels hardest right now.",
    },
    {
        "thought": (
            "I look after my father since his stroke and work full time. "
            "I get angry with him and then feel guilty."
        ),
        "expanded": (
            "The office ends and the second shift begins at home. Somewhere in that long day, "
            "your temper slips. Then the guilt sits with you. There is no shame in reaching "
            "your limit.\n\n"
            "Look at what you carry every single day. A person who cares this much also runs "
            "out sometimes. Your father needs you, and you need looking after too. You were "
            "never built to do this alone."
        ),
        "hook": (
            "Anger on a long day takes nothing from your love. You have stayed beside your "
            "father through all of this, and you can lean on someone too."
        ),
        "practise": "Within 7 days, ask one relative to sit with your father for an hour.",
    },
    {
        "thought": "I was laid off at 46 after 19 years in one company. I haven't told my family yet.",
        "expanded": (
            "Nineteen years of the same road to the same desk, and then it stops. Now you carry "
            "that news home and keep it behind your face. That is a lonely thing to hold.\n\n"
            "There is no shame in needing a little time. The company let go of you. All that "
            "you learned in those years did not leave with the job. And you need not carry "
            "this by yourself."
        ),
        "hook": (
            "Nineteen years of work cannot be taken back by anyone. What you learned and who "
            "you became walk with you into whatever comes after this."
        ),
        "practise": "Within 5 days, tell one person at home about losing the job.",
    },
    {
        "thought": "We broke up three months ago and I still check their profile every night.",
        "expanded": (
            "It gets quiet, and the phone is in your hand again. One look, you say, and "
            "then you are scrolling. Three months is not long for a heart. There is nothing "
            "foolish in this ache.\n\n"
            "But each look opens it all over again. A wound cannot close if we keep lifting "
            "the bandage. You cared deeply, and that care can slowly turn back toward you."
        ),
        "hook": (
            "Missing someone is only love with nowhere to go. You can keep what was good in "
            "it and still give your evenings back to yourself."
        ),
        "practise": "Within 2 days, mute their profile on your phone.",
    },
    {
        "thought": "I got a job offer in Bengaluru, but my parents would be alone in Madurai. I can't decide.",
        "expanded": (
            "You open the offer letter and feel glad for a moment. Then you picture the house "
            "in Madurai, and the gladness gets mixed with worry. There is nothing selfish in "
            "wanting both.\n\n"
            "We want the choice that hurts nobody, and sometimes that choice is not there. So "
            "notice which road feels tight and which feels light. Your love for your parents "
            "goes with you, whichever way you turn."
        ),
        "hook": (
            "Both pulls in you come from a good place. You want to grow and you want to care, "
            "and one clear choice can hold both."
        ),
        "practise": "By Friday, list what you would gain and lose in each city.",
    },
    {
        "thought": "I sent the wrong invoice to a client and my boss found out. I keep replaying it.",
        "expanded": (
            "You pressed send, and that was that. Now that moment keeps coming back, and each "
            "time you feel it again. There is no shame in slipping at work.\n\n"
            "A wrong invoice is an error on paper. You are far more than that one bad moment. "
            "And the replay cannot change what was sent. But the care behind it can go into "
            "your very next piece of work."
        ),
        "hook": (
            "One wrong invoice says very little about your whole work. The worry you feel "
            "comes from wanting to do right by the people you work for."
        ),
        "practise": "By Wednesday, write a short checklist for sending invoices.",
    },
    {
        "thought": "I failed NEET for the second time and my relatives keep asking about my rank.",
        "expanded": (
            "The phone rings, or someone drops by, and the same question comes again. And each "
            "time, a little part of you curls inward. There is no shame in being hurt by "
            "this.\n\n"
            "Maybe your relatives ask out of habit. Maybe they do not know how it lands. Two "
            "attempts took real courage from you. And a rank is one number on one day."
        ),
        "hook": (
            "Trying twice at something this hard takes a brave heart. A rank can tell you "
            "about one exam, and nothing about what you can still become."
        ),
        "practise": "By Sunday, write one short reply for relatives who ask about your rank.",
    },
    {
        "thought": "My mother-in-law criticises my cooking in front of guests and everyone stays silent.",
        "expanded": (
            "The plates go around, and then that remark comes. Nobody at the table says a "
            "word. And you are left sitting with it. There is nothing wrong in wanting respect "
            "in your own home.\n\n"
            "Maybe your mother-in-law speaks without thinking. Maybe this is how they were "
            "spoken to once. You cannot change their habit. But your voice can be soft and "
            "firm together, and you can use it."
        ),
        "hook": (
            "A remark at the table cannot measure your worth. You can stay gentle with your "
            "family and still stand up for your own dignity."
        ),
        "practise": "Within 4 days, ask for any cooking comments to come to you privately.",
    },
    {
        "thought": "I run a small tailoring shop. Since the new mall opened, customers have reduced and I'm losing hope.",
        "expanded": (
            "The shutter goes up and you look at the road. The hours pass with fewer people "
            "stepping in. Watching that every day wears a person down. There is no shame in "
            "losing heart.\n\n"
            "But you have kept this shop running with your own skill. A mall cannot know a "
            "customer the way you do. Some people still want someone who remembers their "
            "measurements. Your work has a place."
        ),
        "hook": (
            "A big mall cannot copy the care in your stitching. Your own way of working has "
            "its own shine, and the people you serve can feel it."
        ),
        "practise": "Within 3 days, phone one regular customer to ask what they need stitched.",
    },
    {
        "thought": "Since I retired and my children moved abroad, the house is so quiet. I feel useless.",
        "expanded": (
            "The morning comes, and nothing is waiting for you. The rooms that were once full "
            "are silent now. There is nothing strange in missing being needed.\n\n"
            "All those years, people leaned on you. What you know did not retire with you. "
            "Somewhere close by, a person could use exactly that. And giving it may lift this "
            "heaviness a little, the way opening a window changes a room."
        ),
        "hook": (
            "A quiet house has not emptied what you carry inside. You have years of knowing "
            "how to do things, and someone near you could learn from them."
        ),
        "practise": "By Saturday, offer to teach a neighbour's child something you know well.",
    },
]


def _fill(text: str) -> str:
    """Put the card length limits from config into the Markdown guide."""
    values = {
        "{HOOK_MIN}": config.HOOK_MIN_WORDS,
        "{HOOK_MAX}": config.HOOK_MAX_WORDS,
        "{EXP_MIN}": config.EXPANDED_MIN_WORDS,
        "{EXP_MAX}": config.EXPANDED_MAX_WORDS,
    }
    for placeholder, value in values.items():
        text = text.replace(placeholder, str(value))
    return text


def language_guide() -> str:
    """The language guide for config.PROMPT_VERSION, with runtime placeholders filled."""
    version = config.PROMPT_VERSION
    if version not in LANGUAGE_FILES:
        raise ValueError(
            f"PROMPT_VERSION must be one of {', '.join(LANGUAGE_FILES)}, not {version!r}."
        )
    text = (PROMPT_DIR / LANGUAGE_FILES[version]).read_text(encoding="utf-8")
    text = text.replace("{{perspective}}", PERSPECTIVE)
    return text.replace(
        "{{user_context}}", "the person's message, sent as the next message"
    )


def _render_examples() -> str:
    blocks = []
    examples = EXAMPLES_V4 if config.PROMPT_VERSION == "v4" else EXAMPLES
    for number, example in enumerate(examples, start=1):
        blocks.append(
            f"### Example {number}\n"
            f'Person: "{example["thought"]}"\n'
            f"- expanded: {example['expanded']}\n"
            f"- hook: {example['hook']}\n"
            f"- practise: {example['practise']}"
        )
    return "\n\n".join(blocks)


def today_line(now: datetime) -> str:
    """e.g. 'Today is Friday, 20 November 2026.' Added per request so the date is current."""
    return f"Today is {now:%A}, {now.day} {now:%B %Y}."


def build_system_prompt() -> str:
    common = _fill((PROMPT_DIR / COMMON_FILE).read_text(encoding="utf-8"))
    perspective = _fill((PROMPT_DIR / f"{PERSPECTIVE}.md").read_text(encoding="utf-8"))
    return "\n\n".join(
        [
            common,
            perspective,
            "## Language guide",
            PRECEDENCE,
            language_guide(),
            "## Examples",
            _render_examples(),
        ]
    )
