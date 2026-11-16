# Setting up the Team Time MCP server in Devin Cloud

This guide adds the server to Devin by hand from **Customize → MCPs**. There are two versions; set up
**one** of them, not both, or Devin will load the same tools twice.

| | Stdio | Streamable HTTP |
|---|---|---|
| Runs | On each Devin session's machine, started on demand | Once, on Render |
| Needs first | `uv` installed via the org blueprint | The Render deploy (see [INSTALL.md](INSTALL.md#deploy-to-render)) |

The tools are the same in both: `list_team_members`, `where_is`, `get_timezone` and `time_difference`.

---

## Stdio

### 1. Make sure session machines have `uv`

The command below runs `uvx`, which Devin's machines don't include by default. Under
**Settings → Environment**, the organization blueprint needs:

```yaml
initialize:
  - name: install uv (needed by the team-time STDIO MCP server)
    run: pip install --user uv
```

This installs `uvx` at `/home/ubuntu/.local/bin/uvx`. Skip this step if it's already there.

### 2. Add the server

1. Open **Customize → MCPs** and click **+** (Add custom MCP).
2. Choose the scope: **Personal** (only you) or the organization (every member).
3. Fill in the form:

   | Field | Value |
   |---|---|
   | Name | `team-time` |
   | Description | `Team directory: where team members are, their time zones, and time differences` |
   | Transport | `STDIO` |
   | Command | `/home/ubuntu/.local/bin/uvx` |
   | Arguments | Three separate entries, in order: `--from`, `git+https://github.com/raditha-codev/mcp-demo`, `team-time-mcp` |
   | Environment variables | None |
   | Authentication | None |

   Add each argument as its own entry. Typed on one line, they reach `uvx` as a single argument and
   the server fails to start with `unexpected argument`.
4. Save and check the server is enabled.

The code is fetched from the repo's `main` branch when a session starts the server, so a change pushed
to the repo (for example to `team.json`) reaches new sessions without editing this entry.

---

## Streamable HTTP

### 1. Deploy to Render

Follow [Deploy to Render](INSTALL.md#deploy-to-render), then check
`https://<service>.onrender.com/health` returns `{"status":"ok"}`.

### 2. Add the server

1. Open **Customize → MCPs** and click **+** (Add custom MCP).
2. Choose the scope: **Personal** or the organization.
3. Fill in the form:

   | Field | Value |
   |---|---|
   | Name | `team-time` |
   | Description | `Team directory: where team members are, their time zones, and time differences` |
   | Transport | `Streamable HTTP` (not SSE) |
   | URL | `https://<service>.onrender.com/mcp`, e.g. `https://team-time-mcp.onrender.com/mcp` |
   | Authentication | None |

4. Save and check the server is enabled.

No `uv` is needed on session machines for this version. The endpoint has no authentication, so
anyone with the URL can call it; the tools are read-only.

---

## Check it works

Start a **new session** (running sessions keep the MCP servers they started with) and ask:

> List the team, then tell me how many hours ahead or behind John is compared with Smith.

Devin should call `list_team_members` and `time_difference`, and answer that John Carter (New York)
is 5 hours behind Emma Smith (London) (4 hours for a few weeks a year, when US and UK daylight saving
dates differ).

## Troubleshooting

- **Tools don't appear (stdio):** ask Devin to read `~/.devin-files/mcp-logs/team-time.log` in the
  session; the server's error output is saved there. Common causes: arguments entered on one line, or
  `uv` missing (`/home/ubuntu/.local/bin/uvx` doesn't exist).
- **Tools don't appear (HTTP):** open the `/health` URL. Render's free plan stops idle services, so the
  first request after a quiet period can be slow.
- **Changed the entry but nothing happened:** start a new session.

## Removing it

On **Customize → MCPs**, open `team-time` and delete it (or disable it to keep the settings).

## Alternative: install as a plugin

Instead of filling in the form, Devin can read the same settings from this repo: **Customize →
Plugins → Add plugin → From repository**, repository `raditha-codev/mcp-demo`, subdirectory
`devin-plugins/team-time-stdio` or `devin-plugins/team-time-http`. See [INSTALL.md](INSTALL.md).
