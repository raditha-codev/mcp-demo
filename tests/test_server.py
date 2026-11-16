from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pytest
from mcp import Client

from world_time_mcp.server import mcp

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def call(tool: str, args: dict):
    async with Client(mcp) as client:
        return await client.call_tool(tool, args)


def _offset_hours(tz: str) -> float:
    return datetime.now(timezone.utc).astimezone(ZoneInfo(tz)).utcoffset().total_seconds() / 3600


async def test_lists_tools():
    async with Client(mcp) as client:
        names = {t.name for t in (await client.list_tools()).tools}
    assert names == {"list_team_members", "where_is", "get_timezone", "time_difference"}


async def test_list_team_members():
    result = await call("list_team_members", {})
    assert not result.is_error
    members = result.structured_content["result"]
    assert len(members) == 10
    assert {"name", "role", "city", "country", "timezone"} <= set(members[0])
    for m in members:
        ZoneInfo(m["timezone"])


@pytest.mark.parametrize("query", ["John", "john", "Carter", "John Carter", "  JOHN   carter "])
async def test_where_is_by_any_name(query):
    result = await call("where_is", {"person": query})
    assert not result.is_error
    assert result.structured_content == {
        "name": "John Carter",
        "role": "Backend Engineer",
        "city": "New York",
        "country": "United States",
    }


async def test_name_matching_ignores_accents_and_partial_words():
    assert (await call("where_is", {"person": "muller"})).structured_content["name"] == "Lukas Müller"
    # "John" must not also match "Johnson"
    assert (await call("where_is", {"person": "Johnson"})).structured_content["name"] == "Mike Johnson"


async def test_unknown_person_is_tool_error():
    result = await call("where_is", {"person": "Gandalf"})
    assert result.is_error
    assert "No team member called 'Gandalf'" in result.content[0].text
    assert "Emma Smith" in result.content[0].text


async def test_get_timezone():
    result = await call("get_timezone", {"person": "Nimal"})
    assert not result.is_error
    data = result.structured_content
    assert data["timezone"] == "Asia/Colombo"
    assert data["utc_offset"] == "+05:30"
    assert data["is_dst"] is False
    datetime.fromisoformat(data["local_time"])


async def test_time_difference_john_vs_smith():
    result = await call("time_difference", {"person": "John", "other_person": "Smith"})
    assert not result.is_error
    data = result.structured_content
    expected = _offset_hours("America/New_York") - _offset_hours("Europe/London")
    assert data["difference_hours"] == expected
    assert data["summary"] == f"John Carter (New York) is {-int(expected)} hours behind Emma Smith (London)."


async def test_time_difference_half_hour_and_reversed():
    result = await call("time_difference", {"person": "Nimal", "other_person": "Emma"})
    data = result.structured_content
    assert data["difference_hours"] == _offset_hours("Asia/Colombo") - _offset_hours("Europe/London")
    assert "hours 30 minutes ahead of Emma Smith" in data["summary"]


async def test_time_difference_same_person():
    result = await call("time_difference", {"person": "Aiko", "other_person": "Tanaka"})
    assert result.structured_content["difference_hours"] == 0
    assert "same time zone" in result.structured_content["summary"]
