# World Time MCP server

An [MCP](https://modelcontextprotocol.io) server that tells the current time in cities around the world
and converts times between cities.

It works fully offline: city names are resolved to IANA time zones using the bundled
[GeoNames](https://www.geonames.org/) dataset (~34,000 cities with population > 15,000, via
`geonamescache`), and times are computed locally with Python's `zoneinfo` (DST included).
No API keys, no rate limits, no external service to go down.

## Tools

| Tool | Arguments | Description |
|---|---|---|
| `get_time` | `city` | Current local time in a city or IANA zone |
| `compare_times` | `cities` (list) | Current time in several cities at once |
| `convert_time` | `time`, `from_city`, `to_city` | Convert a time from one city to another |
| `find_cities` | `query`, `limit` | List matching cities and their zones (for ambiguous names) |

City inputs accept:

- Plain names, case- and accent-insensitive: `Colombo`, `sao paulo`, `Bombay`
- A country or US state qualifier: `London, Canada`, `Paris, TX`, `Portland, Oregon`
- IANA time zones: `Asia/Tokyo`, `UTC`

Ambiguous names resolve to the most populous match (`Paris` → Paris, France).

`time` accepts `14:30`, `2:30 PM`, or a dated value such as `2026-03-29 14:30` / `2026-03-29 2:30 PM`.
Time-only values are taken as today in `from_city`.

Example `get_time("Colombo")` result:

```json
{
  "query": "Colombo",
  "city": "Colombo, Sri Lanka",
  "timezone": "Asia/Colombo",
  "local_time": "2026-11-16T08:36:42+05:30",
  "readable": "Monday, 16 November 2026, 08:36",
  "utc_offset": "+05:30",
  "abbreviation": "+0530",
  "is_dst": false
}
```

## Install

Requires Python 3.10+.

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
