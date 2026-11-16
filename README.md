# Team time zone MCP server

An [MCP](https://modelcontextprotocol.io) demo server for a (fictional) distributed team. It answers
questions an AI agent can't answer on its own, because the team data only lives here:

- Who is on the team?
- Where is John based?
- What's Emma's time zone?
- How many hours ahead or behind is John compared with Smith?

The team is defined in [`src/world_time_mcp/team.json`](src/world_time_mcp/team.json) (ten members across
ten time zones); edit it to use your own team. Times are computed locally with Python's `zoneinfo`, so
differences account for daylight saving time on the day you ask. No API keys or external services.

## Tools

| Tool | Arguments | Description |
|---|---|---|
| `list_team_members` | | Everyone on the team, with role, city, country and time zone |
| `where_is` | `person` | The city and country a team member is based in |
| `get_timezone` | `person` | A member's time zone, current UTC offset and local time |
| `time_difference` | `person`, `other_person` | How many hours `person` is ahead of or behind `other_person` right now |

People can be named by full name, first name or last name, ignoring case and accents
(`John`, `carter`, `Lukas Muller`). An ambiguous or unknown name returns an error listing the matches
or the whole team.

Example `time_difference("John", "Smith")` result (in November):

```json
{
  "person": {"name": "John Carter", "timezone": "America/New_York", "local_time": "2026-11-15T23:47-05:00"},
  "other_person": {"name": "Emma Smith", "timezone": "Europe/London", "local_time": "2026-11-16T04:47+00:00"},
  "difference_hours": -5.0,
  "summary": "John Carter (New York) is 5 hours behind Emma Smith (London)."
}
```

## Install

See [INSTALL.md](INSTALL.md) for step-by-step setup of both versions: **stdio** (in Devin Cloud or any
MCP client) and **Streamable HTTP** (deployed to Render).

To run it locally (Python 3.10+):

```bash
git clone https://github.com/raditha-codev/mcp-demo.git
cd mcp-demo
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

Or run it straight from GitHub with [uv](https://docs.astral.sh/uv/):

```bash
uvx --from git+https://github.com/raditha-codev/mcp-demo world-time-mcp
```

## Use with an MCP client

The server speaks MCP over stdio. Add it to your client's config, e.g. Claude Desktop
(`claude_desktop_config.json`), Cursor (`.cursor/mcp.json`) or Windsurf:

```json
{
  "mcpServers": {
    "world-time": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/raditha-codev/mcp-demo", "world-time-mcp"]
    }
  }
}
```

If you installed it locally instead, point `command` at the virtualenv's executable,
e.g. `"/path/to/mcp-demo/.venv/bin/world-time-mcp"` with no `args`.

## Run over Streamable HTTP

By default the server uses **stdio** (the client launches it as a local process). To serve it over
[Streamable HTTP](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http)
instead, e.g. to host it once for many clients:

```bash
world-time-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

The MCP endpoint is `http://<host>:8000/mcp`, with a health check at `/health`. The server is stateless
(JSON responses, no sessions), so it can run behind a load balancer or on serverless platforms.
The same options can be set with the `MCP_TRANSPORT`, `HOST` and `PORT` environment variables.

With Docker:

```bash
docker build -t world-time-mcp .
docker run -p 8000:8000 world-time-mcp
```

Clients then connect by URL, e.g.:

```json
{
  "mcpServers": {
    "world-time": { "url": "https://your-host.example.com/mcp" }
  }
}
```

The HTTP endpoint has no authentication; put it behind your platform's auth or a private network if
it should not be public.

## Try it

To try it interactively, use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector .venv/bin/world-time-mcp
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check . && ruff format --check .
```
