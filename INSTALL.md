# Installing the Team Time MCP server

There are two independent ways to use this server. Pick either one (or both).

To add it to Devin Cloud by hand from **Customize → MCPs** instead of as a plugin, see
[DEVIN_SETUP.md](DEVIN_SETUP.md).

| | Stdio | Streamable HTTP |
|---|---|---|
| Where it runs | On each client machine / Devin session, started on demand | Once, on a host (Render) |
| Client connects via | A command (`uvx ... team-time-mcp`) | A URL (`https://<service>.onrender.com/mcp`) |
| Needs | `uv` on the machine | A deployed service |
| Devin plugin | [`devin-plugins/team-time-stdio`](devin-plugins/team-time-stdio) | [`devin-plugins/team-time-http`](devin-plugins/team-time-http) |

---

## Option 1: Stdio

### In Devin Cloud

1. **Make sure `uv` is installed in session machines.** The organization blueprint
   (Settings → Environment) needs:

   ```yaml
   initialize:
     - name: install uv (needed by the team-time STDIO MCP server)
       run: pip install --user uv
   ```

   This puts `uvx` at `/home/ubuntu/.local/bin/uvx`, which is the path the plugin uses.
2. Open **Customize → Plugins → Add plugin → From repository**, choose the scope
   (**Myself** or the organization), and enter repository `raditha-codev/mcp-demo` with
   subdirectory `devin-plugins/team-time-stdio`.
3. Start a new session. The `team-time` MCP server and its tools (`list_team_members`, `where_is`,
   `get_timezone`, `time_difference`) are available. Running sessions keep what they loaded at start.

With the Devin CLI, the equivalent of step 2 is:

```bash
devin plugins install raditha-codev/mcp-demo#devin-plugins/team-time-stdio
```

On a laptop, `uvx` is usually not at `/home/ubuntu/.local/bin/uvx`; use the generic config below instead.

### In other MCP clients (Claude Desktop, Cursor, Windsurf, ...)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then add:

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

---

## Option 2: Streamable HTTP (hosted on Render)

### Deploy to Render

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

### In Devin Cloud

1. Check the URL in [`devin-plugins/team-time-http/.mcp.json`](devin-plugins/team-time-http/.mcp.json).
   It is set to `https://team-time-mcp.onrender.com/mcp`. If Render gave your service a different
   subdomain, update it and push.
2. Open **Customize → Plugins → Add plugin → From repository**, choose the scope, and enter
   repository `raditha-codev/mcp-demo` with subdirectory `devin-plugins/team-time-http`.
3. Start a new session. No credentials are needed, so there's nothing to connect.

No `uv` is needed on session machines for this option.

### In other MCP clients

```json
{
  "mcpServers": {
    "team-time": { "url": "https://<service>.onrender.com/mcp" }
  }
}
```
