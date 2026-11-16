# Setting up Team Time in Devin Cloud

Team Time gives Devin a team directory: who is on the team, where each person is based, their time
zone, and how many hours ahead or behind one person is compared with another.

Set up **one** of the options below, not several, or Devin will load the same tools twice.

| Option | What you get | Runs | Needs first |
|---|---|---|---|
| **A. Plugin (recommended)** | MCP server + a `team-time` skill that tells Devin when and how to use it | On each session machine (stdio) | `uv` in the org blueprint |
| **B. Hosted plugin** | Same, but connects to the server on Render | On Render (Streamable HTTP) | The Render deploy |
| **C. Manual MCP** | MCP server only, no skill | Either | As for A or B |

## Before you start

- **Remove any earlier setup.** On **Customize → MCPs**, delete any `team-time`, `time` or
  `world-time` server you added by hand, at both personal and organization scope.
- **For the stdio options (A, and C with stdio), session machines need `uv`.** The organization's
  environment blueprint needs:

  ```yaml
  initialize:
    - name: install uv (needed by the team-time STDIO MCP server)
      run: pip install --user uv
  ```

  This installs `uvx` at `/home/ubuntu/.local/bin/uvx`. Skip this if it's already there.

---

## A. Install the plugin (stdio)

The repository root is the plugin:

```
mcp-demo/
├── .devin-plugin/plugin.json   # manifest: name "team-time"
├── .mcp.json                   # the team-time MCP server (stdio, via uvx)
└── skills/team-time/SKILL.md   # tells Devin when and how to use the tools
```

1. Open **Customize → Plugins → Add plugin → From repository**.
2. Choose who gets it: only you, or every member of the organization.
3. Enter repository `raditha-codev/mcp-demo`. Leave the subdirectory empty.
4. Confirm. The plugin adds the `team-time` MCP server and the `team-time` skill.
5. On **Customize → MCPs**, check `team-time` appears under **From plugins** and is enabled. It needs
   no credentials, so there is nothing to connect.

With the Devin CLI the equivalent is `devin plugins install raditha-codev/mcp-demo`.

---

## B. Install the hosted plugin (Streamable HTTP)

1. Deploy to Render as described in [INSTALL.md](INSTALL.md#deploy-to-render), and check
   `https://<service>.onrender.com/health` returns `{"status":"ok"}`.
2. Check the URL in [`devin-plugins/team-time-http/.mcp.json`](devin-plugins/team-time-http/.mcp.json).
   It is set to `https://team-time-mcp.onrender.com/mcp`. If Render gave your service a different
   address, update it and push.
3. Open **Customize → Plugins → Add plugin → From repository**, choose who gets it, and enter
   repository `raditha-codev/mcp-demo` with subdirectory `devin-plugins/team-time-http`.

No `uv` is needed on session machines for this option. The endpoint has no authentication, so
anyone with the URL can call it; the tools are read-only.

---

## C. Add the MCP server manually

This adds only the MCP server, without the skill.

1. Open **Customize → MCPs** and click **+** (Add custom MCP).
2. Choose who gets it: only you, or the organization.
3. Fill in the form.

   **Stdio:**

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

   **Streamable HTTP** (after the Render deploy):

   | Field | Value |
   |---|---|
   | Name | `team-time` |
   | Transport | `Streamable HTTP` (not SSE) |
   | URL | `https://<service>.onrender.com/mcp` |
   | Authentication | None |

4. Save and check the server is enabled.

---

## Check it works

Start a **new session** (running sessions keep the plugins and MCP servers they started with) and ask:

> List the team, then tell me how many hours ahead or behind John is compared with Smith.

Devin should call `list_team_members` and `time_difference`, and answer that John Carter (New York)
is 5 hours behind Emma Smith (London) (4 hours for a few weeks a year, when US and UK daylight saving
dates differ). With the plugin, Devin may also say it is using the `team-time` skill.

## Updating

- **Team data or server code:** edit [`src/team_time_mcp/team.json`](src/team_time_mcp/team.json)
  or the code and push to `main`. The stdio server fetches the code from `main` when a session
  starts it; the Render service redeploys on each push.
- **The plugin itself** (`.mcp.json`, the skill, the manifest): push the change and bump `version` in
  both `plugin.json` files. New sessions pick it up.

## Troubleshooting

- **Tools don't appear (stdio):** ask Devin to read `~/.devin-files/mcp-logs/team-time.log` in the
  session; the server's error output is saved there. Common causes: `uv` missing
  (`/home/ubuntu/.local/bin/uvx` doesn't exist), or for a manual entry, arguments on one line or an
  old command name such as `world-time-mcp`.
- **Tools don't appear (HTTP):** open the `/health` URL. Render's free plan stops idle services, so
  the first request after a quiet period can be slow.
- **Tools listed twice:** you have more than one option set up; remove the extras.
- **Changed something but nothing happened:** start a new session.

## Removing it

- **Plugin:** **Customize → Plugins**, open `team-time` (or `team-time-http`) and uninstall it.
- **Manual MCP:** **Customize → MCPs**, open `team-time` and delete it.
