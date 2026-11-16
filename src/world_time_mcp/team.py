"""Team directory loaded from the bundled team.json."""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from functools import cache
from importlib import resources


@dataclass(frozen=True)
class Member:
    name: str
    role: str
    city: str
    country: str
    timezone: str


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).casefold().split())


@cache
def members() -> tuple[Member, ...]:
    data = json.loads(resources.files("world_time_mcp").joinpath("team.json").read_text(encoding="utf-8"))
    return tuple(Member(**item) for item in data)


def find(query: str) -> Member:
    """Find a member by full name, first name or last name (case- and accent-insensitive)."""
    wanted = _normalize(query)
    if not wanted:
        raise ValueError("Provide a team member's name.")
    exact = [m for m in members() if _normalize(m.name) == wanted]
    if exact:
        return exact[0]
    matches = [m for m in members() if wanted in _normalize(m.name).split()]
    if len(matches) == 1:
        return matches[0]
    names = ", ".join(m.name for m in (matches or members()))
    if matches:
        raise ValueError(f"{query!r} matches several team members: {names}. Use the full name.")
    raise ValueError(f"No team member called {query!r}. Team members: {names}.")
