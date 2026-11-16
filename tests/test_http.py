import socket
import subprocess
import sys
import time
import urllib.request

import pytest
from mcp import Client

from team_time_mcp.server import _parse_args

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def http_server():
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, "-m", "team_time_mcp", "--transport", "streamable-http", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(f"{base}/health", timeout=1)
                break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("HTTP server did not start")
        yield base
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_defaults_to_stdio(monkeypatch):
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    args = _parse_args([])
    assert (args.transport, args.host, args.port) == ("stdio", "127.0.0.1", 8000)


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
    monkeypatch.setenv("HOST", "0.0.0.0")
    monkeypatch.setenv("PORT", "9000")
    args = _parse_args([])
    assert (args.transport, args.host, args.port) == ("streamable-http", "0.0.0.0", 9000)


def test_health(http_server):
    with urllib.request.urlopen(f"{http_server}/health", timeout=5) as resp:
        assert resp.status == 200


async def test_streamable_http_tool_call(http_server):
    async with Client(f"{http_server}/mcp") as client:
        names = {t.name for t in (await client.list_tools()).tools}
        assert "time_difference" in names
        result = await client.call_tool("get_timezone", {"person": "Nimal"})
        assert not result.is_error
        assert result.structured_content["timezone"] == "Asia/Colombo"
