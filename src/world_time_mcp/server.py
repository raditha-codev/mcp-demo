"""Team time zone MCP server."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

from world_time_mcp import team

mcp = MCPServer(
    name="world-time",
    instructions=(
        "Directory of the team: who is on it, where each person is based, their time zone, "
        "and how many hours ahead or behind one person is compared with another. "
        "People can be referred to by full name, first name or last name."
    ),
)

_READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)


def _member(person: str) -> team.Member:
    try:
        return team.find(person)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


def _format_offset(offset: timedelta) -> str:
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    hours, minutes = divmod(abs(total_minutes), 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def _format_hours(hours: float) -> str:
    whole, minutes = divmod(round(abs(hours) * 60), 60)
    text = f"{whole} hour{'s' if whole != 1 else ''}"
    return f"{text} {minutes} minutes" if minutes else text


def _local_now(member: team.Member) -> datetime:
    return datetime.now(timezone.utc).astimezone(ZoneInfo(member.timezone))


def _snapshot(member: team.Member, now: datetime) -> dict[str, str]:
    return {"name": member.name, "timezone": member.timezone, "local_time": now.isoformat(timespec="minutes")}


@mcp.tool(annotations=_READ_ONLY)
def list_team_members() -> list[dict[str, str]]:
    """List everyone on the team with their role, city, country and time zone."""
    return [
        {"name": m.name, "role": m.role, "city": m.city, "country": m.country, "timezone": m.timezone}
        for m in team.members()
    ]


@mcp.tool(annotations=_READ_ONLY)
def where_is(person: str) -> dict[str, str]:
    """Find out where a team member is based (city and country).

    Args:
        person: Full name, first name or last name, e.g. "John", "Smith" or "Emma Smith".
    """
    m = _member(person)
    return {"name": m.name, "role": m.role, "city": m.city, "country": m.country}


@mcp.tool(annotations=_READ_ONLY)
def get_timezone(person: str) -> dict[str, Any]:
    """Get a team member's time zone, current UTC offset and current local time.

    Args:
        person: Full name, first name or last name, e.g. "John", "Smith" or "Emma Smith".
    """
    m = _member(person)
    now = _local_now(m)
    return {
        "name": m.name,
        "city": m.city,
        "timezone": m.timezone,
        "utc_offset": _format_offset(now.utcoffset() or timedelta()),
        "abbreviation": now.tzname(),
        "is_dst": bool(now.dst()),
        "local_time": now.isoformat(timespec="seconds"),
    }


@mcp.tool(annotations=_READ_ONLY)
def time_difference(person: str, other_person: str) -> dict[str, Any]:
    """How many hours `person` is ahead of or behind `other_person` right now (DST-aware).

    Args:
        person: The team member to describe, e.g. "John".
        other_person: The team member to compare against, e.g. "Smith".
    """
    a, b = _member(person), _member(other_person)
    a_now, b_now = _local_now(a), _local_now(b)
    diff = ((a_now.utcoffset() or timedelta()) - (b_now.utcoffset() or timedelta())).total_seconds() / 3600
    if diff == 0:
        summary = f"{a.name} and {b.name} are in the same time zone right now."
    else:
        direction = "ahead of" if diff > 0 else "behind"
        summary = f"{a.name} ({a.city}) is {_format_hours(diff)} {direction} {b.name} ({b.city})."
    return {
        "person": _snapshot(a, a_now),
        "other_person": _snapshot(b, b_now),
        "difference_hours": diff,
        "summary": summary,
    }


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="world-time-mcp", description=__doc__)
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default=os.environ.get("MCP_TRANSPORT", "stdio"),
        help="stdio (default) for local clients, streamable-http to serve over HTTP at /mcp",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="HTTP bind address (default 127.0.0.1; use 0.0.0.0 in containers)",
    )
    parser.add_argument(
        "--port", type=int, default=int(os.environ.get("PORT", "8000")), help="HTTP port (default 8000)"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    if args.transport == "stdio":
        mcp.run()
    else:
        mcp.run("streamable-http", host=args.host, port=args.port, stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
