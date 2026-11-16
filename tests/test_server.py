from datetime import datetime

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


async def test_lists_tools():
    async with Client(mcp) as client:
        names = {t.name for t in (await client.list_tools()).tools}
    assert names == {"get_time", "compare_times", "convert_time", "find_cities"}


async def test_get_time():
    result = await call("get_time", {"city": "Colombo"})
    assert not result.is_error
    data = result.structured_content
    assert data["timezone"] == "Asia/Colombo"
    assert data["utc_offset"] == "+05:30"
    assert data["city"] == "Colombo, Sri Lanka"
    datetime.fromisoformat(data["local_time"])


async def test_get_time_unknown_city_is_tool_error():
    result = await call("get_time", {"city": "Notarealcityxyz"})
    assert result.is_error
    assert "Unknown city" in result.content[0].text


async def test_compare_times():
    result = await call("compare_times", {"cities": ["Colombo", "Tokyo", "UTC"]})
    assert not result.is_error
    zones = [r["timezone"] for r in result.structured_content["result"]]
    assert zones == ["Asia/Colombo", "Asia/Tokyo", "UTC"]


@pytest.mark.parametrize(
    ("time", "from_city", "to_city", "expected", "day_diff"),
    [
        ("2026-01-15 09:00", "Colombo", "London", "2026-01-15T03:30:00+00:00", 0),
        ("2026-07-15 09:00", "Colombo", "London", "2026-07-15T04:30:00+01:00", 0),
        ("2026-01-15 23:00", "New York", "Tokyo", "2026-01-16T13:00:00+09:00", 1),
        ("2026-01-15 3:30 PM", "UTC", "Colombo", "2026-01-15T21:00:00+05:30", 0),
        ("half past three", "UTC", "Colombo", None, None),
    ],
)
async def test_convert_time(time, from_city, to_city, expected, day_diff):
    result = await call("convert_time", {"time": time, "from_city": from_city, "to_city": to_city})
    if expected is None:
        assert result.is_error
        return
    assert not result.is_error
    data = result.structured_content
    assert data["to"]["local_time"] == expected
    assert data["day_difference"] == day_diff


async def test_convert_time_only():
    result = await call(
        "convert_time", {"time": "2:30 PM", "from_city": "Colombo", "to_city": "Asia/Kolkata"}
    )
    assert not result.is_error
    assert result.structured_content["to"]["local_time"].endswith("T14:30:00+05:30")


async def test_find_cities():
    result = await call("find_cities", {"query": "Springfield, US", "limit": 3})
    assert not result.is_error
    rows = result.structured_content["result"]
    assert len(rows) == 3
    assert all(", US" not in r["city"] or "United States" in r["city"] for r in rows)
