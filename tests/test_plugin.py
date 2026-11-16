import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = {"stdio": ROOT, "http": ROOT / "devin-plugins" / "team-time-http"}
NAME_RE = re.compile(r"^[a-z0-9]+([.-][a-z0-9]+)*$")


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("variant", PLUGINS)
def test_manifest(variant):
    manifest = _json(PLUGINS[variant] / ".devin-plugin" / "plugin.json")
    assert NAME_RE.match(manifest["name"])
    assert manifest["version"] == _json(PLUGINS["stdio"] / ".devin-plugin" / "plugin.json")["version"]


def test_stdio_mcp_runs_the_console_script():
    server = _json(ROOT / ".mcp.json")["mcpServers"]["team-time"]
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    scripts = re.findall(r"^\[project\.scripts\]\n(\S+) =", pyproject, re.M)
    assert server["command"] == "/home/ubuntu/.local/bin/uvx"
    assert server["args"] == ["--from", "git+https://github.com/raditha-codev/mcp-demo", *scripts]
    assert all(" " not in arg for arg in server["args"])


def test_http_mcp_points_at_mcp_endpoint():
    server = _json(PLUGINS["http"] / ".mcp.json")["mcpServers"]["team-time"]
    assert server["url"].startswith("https://") and server["url"].endswith("/mcp")


@pytest.mark.parametrize("variant", PLUGINS)
def test_skill(variant):
    text = (PLUGINS[variant] / "skills" / "team-time" / "SKILL.md").read_text(encoding="utf-8")
    assert text == (ROOT / "skills" / "team-time" / "SKILL.md").read_text(encoding="utf-8")
    frontmatter = text.split("---")[1]
    assert re.search(r"^name: team-time$", frontmatter, re.M)
    assert re.search(r"^description: .+", frontmatter, re.M)
    for tool in ("list_team_members", "where_is", "get_timezone", "time_difference"):
        assert f"`{tool}" in text
