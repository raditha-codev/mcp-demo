# Installing the Team Time MCP server

**Using Devin Cloud?** Use one of the Devin guides instead:

- [PLUGIN_INSTALL.md](PLUGIN_INSTALL.md): install the Devin plugin (MCP server plus the `team-time` skill).
- [MCP_INSTALL.md](MCP_INSTALL.md): add only the MCP server from Customize → MCPs → +.

There are two versions of the server. Pick one per client.

| | Stdio | Streamable HTTP |
|---|---|---|
| Where it runs | On the client machine, started on demand | Once, on a host (Render) |
| Client connects via | A command (`uvx ... team-time-mcp`) | A URL (`https://<service>.onrender.com/mcp`) |
| Needs | [uv](https://docs.astral.sh/uv/getting-started/installation/) on the machine | A deployed service |

## Stdio in other MCP clients (Claude Desktop, Cursor, Windsurf, ...)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then add to the client's MCP
config:

```json
{
  "mcpServers": {
    "team-time": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/raditha-codev/mcp-demo", "team-time-mcp"]
    }
  }
}
```

## Deploy to Render

The repo includes a [`render.yaml`](render.yaml) Blueprint: a free Docker web service in the
Singapore region, health-checked at `/health`, redeployed on every commit to `main`.

1. In the Render dashboard, choose **New → Blueprint** and connect `raditha-codev/mcp-demo`.
2. Render reads `render.yaml` and creates the `team-time-mcp` service. Approve it.
3. When the deploy finishes, note the service URL, e.g. `https://team-time-mcp.onrender.com`.
4. Check it:

   ```bash
   curl https://team-time-mcp.onrender.com/health    # {"status":"ok"}
   ```

The MCP endpoint is `https://<service>.onrender.com/mcp`.

The endpoint has **no authentication**: anyone with the URL can call it. The tools are read-only,
but put it behind auth if that matters to you.

To change the region or plan, edit `render.yaml` before creating the service (Render can't change
the region afterwards).

## Streamable HTTP in other MCP clients

```json
{
  "mcpServers": {
    "team-time": { "url": "https://<service>.onrender.com/mcp" }
  }
}
```
