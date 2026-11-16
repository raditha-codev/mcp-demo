# Installing Team Time as an MCP server in Devin

This adds the `team-time` MCP server by hand from **Customize → MCPs → +**. Devin gets the tools
`list_team_members`, `where_is`, `get_timezone` and `time_difference`, but not the `team-time` skill,
so it relies on the tool descriptions alone to decide when to use them.

To get the server and the skill together, install the plugin instead: see
[PLUGIN_INSTALL.md](PLUGIN_INSTALL.md). Don't do both, or Devin loads the same tools twice.

For other MCP clients (Claude Desktop, Cursor, ...), see [INSTALL.md](INSTALL.md).

There are two versions. Add one.

| | Stdio (recommended) | Streamable HTTP |
|---|---|---|
| Server runs | On each session machine, started by `uvx` | Once, on Render |
| Needs first | `uv` in the org blueprint | The Render deploy |

## Before you start

- **Remove any earlier setup.** On **Customize → MCPs**, delete any old `team-time`, `time` or
  `world-time` server, and uninstall the `team-time` plugin if you installed it.

## Stdio

1. **Check `uv` is installed on session machines.** The organization's environment blueprint needs
   this step (it's already in raditha-org's blueprint):

   ```yaml
   initialize:
     - name: install uv (needed by the team-time STDIO MCP server)
       run: pip install --user uv
   ```

   It puts `uvx` at `/home/ubuntu/.local/bin/uvx`.
2. Open **Customize → MCPs** and click **+** (Add custom MCP).
3. Choose who gets it: only you, or the organization.
4. Fill in the form:

   | Field | Value |
   |---|---|
   | Name | `team-time` |
   | Description | `Team directory: where team members are, their time zones, and time differences` |
   | Transport | `STDIO` |
   | Command | `/home/ubuntu/.local/bin/uvx` |
   | Arguments | Three separate entries, in this order: |
   | | 1. `--from` |
   | | 2. `git+https://github.com/raditha-codev/mcp-demo` |
   | | 3. `team-time-mcp` |
   | Environment variables | None |
   | Authentication | None |

   Add each argument as its own entry. Typed on one line, they reach `uvx` as a single argument and
   the server fails to start with `unexpected argument`.
5. Save and check the server is enabled.

## Streamable HTTP

1. Deploy the server to Render as described in [INSTALL.md](INSTALL.md#deploy-to-render), and check
   `https://<service>.onrender.com/health` returns `{"status":"ok"}`.
2. Open **Customize → MCPs** and click **+** (Add custom MCP).
3. Choose who gets it: only you, or the organization.
4. Fill in the form:

   | Field | Value |
   |---|---|
   | Name | `team-time` |
   | Description | `Team directory: where team members are, their time zones, and time differences` |
   | Transport | `Streamable HTTP` (not SSE) |
   | URL | `https://<service>.onrender.com/mcp` |
   | Authentication | None |

5. Save and check the server is enabled.

The endpoint has no authentication, so anyone with the URL can call it; the tools are read-only.

## Check it works

Start a **new session** (running sessions keep the MCP servers they started with) and ask:

> List the team, then tell me how many hours ahead or behind John is compared with Smith.

Devin should call `list_team_members` and `time_difference`, and answer that John Carter (New York)
is 5 hours behind Emma Smith (London). It's 4 hours for a few weeks a year, when US and UK daylight
saving dates differ.

Without the skill, Devin may answer some time zone questions with `date` instead of the tools. Name
the team in the prompt ("ask team-time…") if that happens, or install the plugin.

## Troubleshooting

- **Tools don't appear (stdio):** ask Devin to read `~/.devin-files/mcp-logs/team-time.log` in the
  session; the server's error output is saved there. Common causes:
  - `uv` is missing: `/home/ubuntu/.local/bin/uvx` doesn't exist.
  - All three arguments were typed as one entry.
  - The third argument is an old command name such as `world-time-mcp`. It must be `team-time-mcp`.
- **Tools don't appear (HTTP):** open the `/health` URL. Render's free plan stops idle services, so
  the first request after a quiet period can be slow.
- **Changed the entry but nothing happened:** start a new session.

## Removing it

Open **Customize → MCPs**, select `team-time` and delete it. Devin stores servers added with **+** in
a plugin named `default` (personal or organization); if `team-time` was the only server in it, you
can uninstall that plugin from **Customize → Plugins** instead.
