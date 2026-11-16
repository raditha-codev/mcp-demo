"""World Time MCP server."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from starlette.requests import Request
from starlette.responses import JSONResponse

from world_time_mcp import cities as city_lookup

mcp = MCPServer(
    name="world-time",
    instructions=(
        "Tells the current time in cities around the world and converts times between cities. "
        "Cities can be qualified with a country or US state, e.g. 'Paris, France' or 'Portland, OR'. "
        "IANA time zone names such as 'Asia/Colombo' are also accepted."
    ),
)

_READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=False)


def _resolve(query: str) -> tuple[str, city_lookup.City | None]:
    try:
        return city_lookup.resolve(query)
    except ValueError as exc:
        raise ToolError(str(exc)) from exc


def _describe(moment: datetime, query: str, tz_name: str, city: city_lookup.City | None) -> dict[str, Any]:
    offset = moment.utcoffset()
    total_minutes = int(offset.total_seconds() // 60) if offset is not None else 0
    sign = "+" if total_minutes >= 0 else "-"
    hours, minutes = divmod(abs(total_minutes), 60)
    return {
        "query": query,
        "city": city.label if city else None,
        "timezone": tz_name,
        "local_time": moment.isoformat(timespec="seconds"),
        "readable": moment.strftime("%A, %d %B %Y, %H:%M"),
        "utc_offset": f"{sign}{hours:02d}:{minutes:02d}",
        "abbreviation": moment.tzname(),
        "is_dst": bool(moment.dst()),
    }


def _parse_time(value: str, tz: ZoneInfo) -> datetime:
    value = value.strip()
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        parsed = None
    if parsed is None:
        for fmt in ("%H:%M", "%H:%M:%S", "%I:%M %p", "%I %p", "%I:%M%p", "%I%p"):
            try:
                clock = datetime.strptime(value.upper(), fmt).time()
            except ValueError:
                pass
            else:
                return datetime.combine(datetime.now(tz).date(), clock, tzinfo=tz)
            try:
                return datetime.strptime(value.upper(), f"%Y-%m-%d {fmt}").replace(tzinfo=tz)
            except ValueError:
                pass
        raise ToolError(
            f"Could not understand time {value!r}. "
            "Use 'HH:MM', '3:30 PM', or prefix a date: 'YYYY-MM-DD HH:MM'."
        )
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=tz)
    return parsed.astimezone(tz)


@mcp.tool(annotations=_READ_ONLY)
def get_time(city: str) -> dict[str, Any]:
    """Get the current local time in a city (or IANA time zone).

    Args:
        city: City name, optionally with a country or US state, e.g. "Colombo",
            "London, Canada", "Portland, OR", or an IANA zone like "Asia/Tokyo".
    """
    tz_name, match = _resolve(city)
    now = datetime.now(timezone.utc).astimezone(ZoneInfo(tz_name))
    return _describe(now, city, tz_name, match)


@mcp.tool(annotations=_READ_ONLY)
def compare_times(cities: list[str]) -> list[dict[str, Any]]:
    """Get the current local time in several cities at once.

    Args:
        cities: City names or IANA zones, e.g. ["Colombo", "London", "New York"].
    """
    if not cities:
        raise ToolError("Provide at least one city.")
    now = datetime.now(timezone.utc)
    results = []
    for query in cities:
        tz_name, match = _resolve(query)
        results.append(_describe(now.astimezone(ZoneInfo(tz_name)), query, tz_name, match))
    return results


@mcp.tool(annotations=_READ_ONLY)
def convert_time(time: str, from_city: str, to_city: str) -> dict[str, Any]:
    """Convert a time in one city to the local time in another city.

    Args:
        time: Time in the source city: "14:30", "2:30 PM", or "2026-03-29 14:30" /
            "2026-03-29 2:30 PM" for a specific date. Time-only values are taken as today in `from_city`.
        from_city: City (or IANA zone) the time belongs to.
        to_city: City (or IANA zone) to convert the time to.
    """
    from_tz, from_match = _resolve(from_city)
    to_tz, to_match = _resolve(to_city)
    source = _parse_time(time, ZoneInfo(from_tz))
    target = source.astimezone(ZoneInfo(to_tz))
    day_shift = (target.date() - source.date()).days
    return {
        "from": _describe(source, from_city, from_tz, from_match),
        "to": _describe(target, to_city, to_tz, to_match),
        "day_difference": day_shift,
    }


@mcp.tool(annotations=_READ_ONLY)
def find_cities(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """List cities matching a name, largest first, with their time zones.

    Useful when a name is ambiguous (e.g. "Paris" or "Springfield").

    Args:
        query: City name, optionally with a country or US state after a comma.
        limit: Maximum number of results (1-25).
    """
    limit = max(1, min(limit, 25))
    return [
        {
            "city": c.label,
            "timezone": c.timezone,
            "population": c.population,
            "latitude": c.latitude,
            "longitude": c.longitude,
        }
        for c in city_lookup.find_cities(query, limit=limit)
    ]


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
