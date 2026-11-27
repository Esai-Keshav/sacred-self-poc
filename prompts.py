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
    "v5": "language_v5.md",
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



# Assuring, encouraging v5 cards, rewritten from client feedback in feedback.md. Practise is one
# action through the five checkpoints: context, change, instruction, continuation, capability.
EXAMPLES_V5: list[dict] = [
    {
        "thought": (
            "My daughter never shows passion in solving. She is always stuck with the problem "
            "and busy blaming. When we want to help she resists. She is 13 years old."
        ),
        "expanded": (
            "You have tried again and again, and it is tiring to watch your daughter stay "
            "stuck. But do not give up on your daughter yet. At thirteen, every child wants "
            "to feel capable, and help that is pushed can feel like control.\n\n"
            "So change your role. Stop being the one who solves, and become the one who "
            "believes. Your calm trust can do more than any advice. When your daughter feels "
            "trusted, the will to act grows from inside. You have the patience for this."
        ),
        "hook": (
            "Your daughter needs your belief more than your solutions. Step back with "
            "confidence, and let your daughter discover the strength to solve problems on "
            "their own."
        ),
        "practise": (
            "The next time your daughter complains about a problem, hold back the urge to "
            "offer solutions straight away.\n\n"
            'You can say: "I believe you can handle this. Choose one thing you can do about'
            ' it today. I am here if you need me."\n\n'
            "Then give your daughter space to act, without reminding or persuading. Your "
            "trust is what builds their confidence."
        ),
    },
    {
        "thought": (
            "Whenever I join a workout class, I feel like quitting in a couple of months. "
            "I tell myself I can do it on my own, but soon I end up doing nothing."
        ),
        "expanded": (
            "Joining a class proves you are willing to invest in your health. Then the early "
            "excitement fades, and working out alone starts to sound easier. But you have "
            "already noticed that alone, it does not happen. That honest awareness is a "
            "strength.\n\n"
            "So stop waiting to feel excited. Feelings come and go, but a promise can hold you "
            "steady. You do not have to enjoy every session to enjoy what consistency builds. "
            "Keep your word to yourself and discover how good that feels."
        ),
        "hook": (
            "Enthusiasm got you started, and commitment can carry you forward. Choose a rhythm "
            "you can keep, and discover the pride of showing up again and again!"
        ),
        "practise": (
            "Within 3 days, instead of planning to train alone, sign up for one class you "
            "can attend twice a week for the next 8 weeks. Put every session in your "
            "calendar like a meeting you cannot miss.\n\n"
            "On low days, go anyway and give just 20 minutes, without bargaining with "
            "yourself. Keeping this promise to yourself builds a self-respect no mood can "
            "shake."
        ),
    },
    {
        "thought": "I often get distracted while I work. Everything else looks interesting other than my work.",
        "expanded": (
            "It is easy for something new to grab your attention, especially when work feels "
            "repetitive. That does not mean you cannot focus. Interest rarely comes first. It "
            "grows once you get involved and see things moving.\n\n"
            "So be willing to give your work your full presence for a short stretch. Every time "
            "you drift and come back, you are training your focus. You are building the very "
            "strength you think you lack. The more attention you give your work, the more alive "
            "it becomes."
        ),
        "hook": (
            "Your mind loves novelty, but it can love progress too. Stay with one task long "
            "enough, and finishing it becomes your new kind of excitement."
        ),
        "practise": (
            "Today, instead of starting work with your phone nearby, choose one clearly "
            "defined piece of work, put your phone in another room, then start a 20-minute "
            "timer.\n\n"
            "Whenever your mind wanders, bring it back to that piece without scolding "
            "yourself, and stop only when the timer rings. Get involved, finish strong, and"
            " enjoy the progress you create."
        ),
    },
    {
        "thought": (
            "I feel nobody respects my suggestions. I always adjust, even when all know I am "
            "logically right. I don't feel like adjusting anymore. I feel like dumping my anger on all."
        ),
        "expanded": (
            "Showing up and being passed over, again and again, lets anger build. But pouring "
            "it out on everyone will not get your idea heard. It will only make the room "
            "harder.\n\n"
            "When others do not respect your contribution, that is your moment to respect "
            "yourself. You do not need to prove you are right. Stay willing to work together "
            "and open to better ideas, even from others. You can be flexible and still keep "
            "your dignity. That takes real strength, and you have it."
        ),
        "hook": (
            "You keep showing up because you truly care about solutions. The goal is to solve "
            "the problem, not win the argument, and your dignity stays whole."
        ),
        "practise": (
            "Before your next discussion, instead of arguing to be proven right, write down"
            " the real problem and one workable solution that is fair to everyone.\n\n"
            "You can say: \"I want us to find the best solution, whoever's idea it is. Here "
            'is what I think could work. I am open to other ideas too."\n\n'
            "Then listen fully before replying. Your calm self-respect will carry further "
            "than anger ever could."
        ),
    },
    {
        "thought": "My group members don't contribute anything, but I get blamed for everything.",
        "expanded": (
            "Carrying the work and then carrying the blame too is exhausting. But complaining "
            "later only gives others a reason to brush you off. Strength begins with what you "
            "are willing to do.\n\n"
            "So lead with your contribution, not with blame. Say plainly what you will do and "
            "what you need from them. When both are clear, nobody can twist the story later. "
            "You cannot control their response, but you can face it with a steady heart."
        ),
        "hook": (
            "Blame cannot stick when your own work is clear. Do your share fully, ask for "
            "theirs plainly, and stand ready for whatever that honesty brings."
        ),
        "practise": (
            "Within 2 days, instead of carrying the extra work, call a group meeting before"
            " the next deadline.\n\n"
            'You can say: "I want this to work, so I will finish my share on time. For this'
            " to succeed, I need each of you to finish yours. Let us agree on who does what"
            ' now."\n\n'
            "Then write the agreed tasks in the group chat. Starting with your own part "
            "shows self-respect."
        ),
    },
    {
        "thought": "My business has failed. I put in so much effort. I don't know what to do now.",
        "expanded": (
            "You feel drained because you poured so much effort into this. Maybe you were one "
            "attempt short. No one has seen only success. The people we admire most often "
            "failed the most, and kept going with fire.\n\n"
            "You still have that fire. The skill, the courage and the hard lessons are all with "
            "you now. Take a breath, then pump that enthusiasm back in. Go ahead, my friend. "
            "Keep attempting until you see what is possible."
        ),
        "hook": (
            "This failure is not the end of your story. Carry eighty percent of its lessons "
            "into your next attempt, add something new, and go again!"
        ),
        "practise": (
            "Within 5 days, instead of replaying what went wrong, sit with a notebook, then"
            " write down the three biggest lessons this business taught you.\n\n"
            "Then keep that page where you will see it, and read it before you plan "
            "anything new. Every lesson you carry forward makes whatever you build next "
            "wiser and stronger. Go again with that fire."
        ),
    },
    {
        "thought": "I failed an exam even after studying so hard.",
        "expanded": (
            "Studying hard proves your commitment, and that is already a strength. Now become a "
            "curious student of your own attempt. Was it understanding, memory, time or exam "
            "pressure that held you back?\n\n"
            "Each gap is something you can work on. Look at what this has built in you, the "
            "discipline and the knowledge. None of that disappears because of one result. You "
            "have more experience today than yesterday. Carry it forward with enthusiasm, "
            "because so many possibilities are still waiting."
        ),
        "hook": (
            "You did not waste your effort on this exam. You gained knowledge and discipline, "
            "so learn what went wrong and come back stronger!"
        ),
        "practise": (
            "Within 24 hours, instead of only feeling the result, go through your paper and"
            " mark the three questions that cost you the most marks.\n\n"
            "Then choose one of those gaps and plan exactly how you will practise it this "
            "week, before anything else. Every gap you face makes you a sharper student. "
            "Carry that courage into your next attempt."
        ),
    },
    {
        "thought": "My crush likes someone else. I can't stop thinking about it.",
        "expanded": (
            "Your heart had a hope, and now it has turned another way. That hurts. But affection "
            "cannot be earned through effort or won through comparison. Their choice tells you "
            "what they feel, not what you are worth.\n\n"
            "You are still someone who can love deeply, enjoy friends and build a full life. You "
            "do not need to fight every thought. Just stop giving it the whole day. There is so "
            "much more of life waiting for you."
        ),
        "hook": (
            "Respect their choice, and choose to enjoy your life too. Your feelings are real, "
            "but a whole beautiful life is still waiting for your attention."
        ),
        "practise": (
            "For the next 7 days, instead of letting each thought about your crush run for "
            "hours, pause the moment it starts.\n\n"
            'Say to yourself: "I wish them well, and I am choosing my own life." Then bring'
            " your attention back to what you were doing, without scolding yourself. Each "
            "time you return, you choose self-respect and a fuller life."
        ),
    },
    {
        "thought": "Sometimes I feel I'm just not good enough.",
        "expanded": (
            "That thought gets loud when you notice your mistakes or compare yourself with "
            "someone else. But your worth is not set by one skill, one result or one person's "
            "opinion.\n\n"
            "Look at what is already in you, your effort, your experience and your ability to "
            "learn. You do not need to be perfect before you take part. There is so much room "
            "for you to join in, improve and enjoy finding out what you are capable of."
        ),
        "hook": (
            "You are not starting from zero at all. You are building on who you already are, "
            "and there is so much left to discover."
        ),
        "practise": (
            "Today, instead of listing what you lack, write down five things you are "
            "already good at, from skills to qualities.\n\n"
            "Then keep the list where you see it each morning for the next 7 days, and add "
            "one new strength whenever you notice it. Your strengths are real, and they are"
            " ready to be used."
        ),
    },
    {
        "thought": "I lied to my parents about my exam results. Now I feel guilty.",
        "expanded": (
            "You feared letting your parents down, and hiding the result felt easier in that "
            "moment. But look closely. Is it their reaction you are really afraid of facing?\n\n"
            "Be willing to face their disappointment or anger, as long as you are safe. An "
            "uncomfortable talk is something you can handle. One mistake is not your whole "
            "character. Your willingness to tell the truth and set things right is what counts now. "
            "That takes courage, and you have it."
        ),
        "hook": (
            "Taking responsibility for a mistake takes real courage. One lie cannot sum you up, "
            "and honesty now can begin to make things right."
        ),
        "practise": (
            "Within 48 hours, instead of carrying the secret, choose a calm moment to tell "
            "your parents the truth, if you feel safe doing so.\n\n"
            'You can say: "I was afraid of disappointing you, so I hid my real marks. That '
            'was not right, and I am sorry."\n\n'
            "Then listen to their reaction without defending yourself. Owning a mistake is "
            "the bravest kind of honesty."
        ),
    },
    {
        "thought": "My junior got a better internship than me. I feel jealous.",
        "expanded": (
            "It is natural to feel jealous when someone junior gets the chance you "
            "wanted. But their win takes nothing from your ability or your potential.\n\n"
            "Instead of comparing paths, let their success show you what is possible for you "
            "too. Be curious about the openings around you and eager to explore them. You "
            "already have your own strengths and experiences to offer. Keep learning, keep "
            "showing up and stay ready for the chances ahead."
        ),
        "hook": (
            "Their success does not make you any less capable. Celebrate their opportunity, stay "
            "excited about yours, and keep growing toward what you want!"
        ),
        "practise": (
            "Within 3 days, rather than comparing yourself with your junior, ask them how "
            "they prepared for the internship and which skills helped most.\n\n"
            "Then practise one of those skills for 20 minutes each day this week. Learning "
            "from someone else's success takes humility and courage. Let it widen your "
            "possibilities, not your comparisons."
        ),
    },
]


def _fill(text: str) -> str:
    """Put the card length limits from config into the Markdown guide."""
    values = {
        "{HOOK_MIN}": config.HOOK_MIN_WORDS,
        "{HOOK_MAX}": config.HOOK_MAX_WORDS,
        "{EXP_MIN}": config.EXPANDED_MIN_WORDS,
        "{EXP_MAX}": config.EXPANDED_MAX_WORDS,
        "{PRACTISE_MIN}": config.PRACTISE_MIN_WORDS,
        "{PRACTISE_MAX}": config.PRACTISE_MAX_WORDS,
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
    examples = {"v4": EXAMPLES_V4, "v5": EXAMPLES_V5}.get(config.PROMPT_VERSION, EXAMPLES)
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


def build_system_prompt(perspective: str = PERSPECTIVE) -> str:
    """Common rules plus the perspective file. The language guide and examples are
    the Willingness voice, so only that perspective gets them."""
    common = _fill((PROMPT_DIR / COMMON_FILE).read_text(encoding="utf-8"))
    parts = [common, _fill((PROMPT_DIR / f"{perspective}.md").read_text(encoding="utf-8"))]
    if perspective == PERSPECTIVE:
        parts += ["## Language guide", PRECEDENCE, language_guide(), "## Examples", _render_examples()]
    return "\n\n".join(parts)
