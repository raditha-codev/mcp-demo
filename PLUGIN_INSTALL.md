# Installing Team Time as a Devin plugin

The plugin gives Devin a team directory: who is on the team, where each person is based, their time
zone, and how many hours ahead or behind one person is compared with another. It contains:

- the `team-time` **MCP server**, with the tools `list_team_members`, `where_is`, `get_timezone` and
  `time_difference`;
- the `team-time` **skill**, which tells Devin to use those tools for questions about teammates
  instead of guessing or running `date`.

To add only the MCP server, without the skill, see [MCP_INSTALL.md](MCP_INSTALL.md) instead. Don't
do both, or Devin loads the same tools twice.

There are two versions of the plugin. Install one.

| | Stdio plugin (recommended) | Hosted plugin |
|---|---|---|
| Repository | `raditha-codev/mcp-demo` | `raditha-codev/mcp-demo` |
| Subdirectory | none (the repo root) | `devin-plugins/team-time-http` |
| Server runs | On each session machine, started by `uvx` | Once, on Render (Streamable HTTP) |
| Needs first | `uv` in the org blueprint | The Render deploy |

Plugin layout:

```
mcp-demo/
├── .devin-plugin/plugin.json          # stdio plugin manifest: name "team-time"
├── .mcp.json                          # stdio MCP server (uvx ... team-time-mcp)
├── skills/team-time/SKILL.md          # the skill
└── devin-plugins/team-time-http/
    ├── .devin-plugin/plugin.json      # hosted plugin manifest: name "team-time-http"
    ├── .mcp.json                      # MCP server URL on Render
    └── skills/team-time/SKILL.md      # same skill
```

## Before you start

- **Remove any earlier setup.** On **Customize → MCPs**, delete any `team-time`, `time` or
  `world-time` server added with the **+** button, at both personal and organization scope.

## Stdio plugin

1. **Check `uv` is installed on session machines.** The organization's environment blueprint needs
   this step (it's already in raditha-org's blueprint):

   ```yaml
   initialize:
     - name: install uv (needed by the team-time STDIO MCP server)
       run: pip install --user uv
   ```

   It puts `uvx` at `/home/ubuntu/.local/bin/uvx`, the command in [`.mcp.json`](.mcp.json).
2. Open **Customize → Plugins → Add plugin → From repository**.
3. Choose who gets it: only you, or every member of the organization.
4. Enter repository `raditha-codev/mcp-demo`. Leave the subdirectory empty.
5. Confirm.
6. On **Customize → MCPs**, check `team-time` appears under **From plugins** and is enabled. It needs
   no credentials.

With the Devin CLI: `devin plugins install raditha-codev/mcp-demo`.

## Hosted plugin

1. Deploy the server to Render as described in [INSTALL.md](INSTALL.md#deploy-to-render), and check
   `https://<service>.onrender.com/health` returns `{"status":"ok"}`.
2. Check the URL in [`devin-plugins/team-time-http/.mcp.json`](devin-plugins/team-time-http/.mcp.json).
   It is `https://team-time-mcp.onrender.com/mcp`. If Render gave your service a different address,
   update it and push.
3. Open **Customize → Plugins → Add plugin → From repository** and choose who gets it.
4. Enter repository `raditha-codev/mcp-demo` and subdirectory `devin-plugins/team-time-http`.
5. Confirm, and check `team-time` is enabled on **Customize → MCPs**.

The Render endpoint has no authentication, so anyone with the URL can call it; the tools are
read-only.

With the Devin CLI: `devin plugins install raditha-codev/mcp-demo#devin-plugins/team-time-http`.

## Check it works

Start a **new session** (running sessions keep the plugins they started with) and ask:

> List the team, then tell me how many hours ahead or behind John is compared with Smith.

Devin should use the `team-time` skill, call `list_team_members` and `time_difference`, and answer
that John Carter (New York) is 5 hours behind Emma Smith (London). It's 4 hours for a few weeks a
year, when US and UK daylight saving dates differ.

## Updating

- **Team data or server code:** edit [`src/team_time_mcp/team.json`](src/team_time_mcp/team.json) or
  the code and push to `main`. The stdio server fetches the code from `main` when a session starts
  it; the Render service redeploys on each push.
- **The plugin** (`.mcp.json`, the skill, the manifest): push the change and bump `version` in both
  `plugin.json` files. Keep the two copies of `SKILL.md` identical (a test checks this).

Changes reach new sessions only.

## Troubleshooting

- **Tools don't appear (stdio):** ask Devin to read `~/.devin-files/mcp-logs/team-time.log` in the
  session; the server's error output is saved there. Check `/home/ubuntu/.local/bin/uvx` exists.
- **Tools don't appear (hosted):** open the `/health` URL. Render's free plan stops idle services,
  so the first request after a quiet period can be slow.
- **Tools listed twice:** both plugins are installed, or a manual MCP entry is left over. Remove the
  extras.

## Removing it

Open **Customize → Plugins**, select `team-time` (or `team-time-http`) and uninstall it. This removes
the MCP server and the skill.
