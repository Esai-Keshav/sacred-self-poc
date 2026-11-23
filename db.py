from functools import lru_cache

from supabase import Client, create_client

import config


@lru_cache
def client() -> Client:
    return create_client(config.settings.supabase_url, config.settings.supabase_key)


def build_card_row(
    thought: str,
    card: dict,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
    cost_usd: float | None,
) -> dict:
    return {
        "thought": thought,
        "model": model,
        "hook": card["hook"],
        "expanded": card["expanded"],
        "practise": card["practise"],
        # The column is still NOT NULL in Supabase; new cards have no say_it.
        "say_it": "",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost_usd,
    }


def build_feedback_row(
    card_id: int,
    overall: int | None,
    hook: int | None,
    expanded: int | None,
    practise: int | None,
    comment: str | None,
) -> dict:
    return {
        "card_id": card_id,
        "overall": overall,
        "hook": hook,
        "expanded": expanded,
        "practise": practise,
        "comment": comment or None,
    }


def save_card(
    thought: str,
    card: dict,
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
    cost_usd: float | None,
) -> int:
    row = build_card_row(thought, card, model, input_tokens, output_tokens, cost_usd)
    return client().table("cards").insert(row).execute().data[0]["id"]


def list_cards() -> list[dict]:
    response = (
        client()
        .table("cards")
        .select("*")
        .order("id", desc=True)
        .limit(config.HISTORY_LIMIT)
        .execute()
    )
    return response.data


def save_feedback(row: dict) -> None:
    client().table("feedback").insert(row).execute()


def list_feedback(card_ids: list[int]) -> list[dict]:
    if not card_ids:
        return []
    response = (
        client()
        .table("feedback")
        .select("*")
        .in_("card_id", card_ids)
        .order("id")
        .execute()
    )
    return response.data


