---
name: team-time
description: "Answer questions about the team with the team-time MCP tools: who is on the team, where a person is based, their time zone or local time, how many hours ahead or behind one person is compared with another, who is likely online now, and good times to meet. Use whenever a question names a teammate or asks about the team's locations, time zones, working hours or meeting times. Requires the team-time MCP server."
---

# Team time

The team only exists in the `team-time` MCP server, so answer from its tools. Don't guess a person's
location or time zone, and don't work times out with `date` or from memory: the tools apply daylight
saving time for today.

## Tools

| Question | Tool |
|---|---|
| Who is on the team? Who works in <city/country/role>? | `list_team_members()` |
| Where is <person>? | `where_is(person)` |
| What's <person>'s time zone / local time right now? | `get_timezone(person)` |
| How many hours ahead or behind is <person> compared with <other>? | `time_difference(person, other_person)` |

`person` can be a full name, first name or last name, in any case and with or without accents
("John", "smith", "Lukas Muller").

## Answering

- **Time differences:** call `time_difference` and give its `summary`; it already says "ahead of" or
  "behind" the right way round. `difference_hours` is `person` minus `other_person` (negative means
  behind) and can be fractional (5.5 hours for Colombo vs London).
- **Questions about several people** (who is online now, when can A, B and C meet): call
  `list_team_members` once, then `get_timezone` for each person involved. Unless the user says
  otherwise, treat 09:00-17:00 local time on weekdays as working hours and say you assumed this; the
  directory doesn't store working hours.
- **A name matches nobody or several people:** the tool error lists the candidates or the whole team.
  Ask the user which person they meant instead of picking one.
- **Mention daylight saving** when the answer depends on today's date, for example a US-UK difference
  is 5 hours most of the year but 4 hours for a few weeks in spring and autumn.

## If the tools are missing

If no `team-time` tools are available, say the team-time MCP server isn't connected in this session
and point to the setup guide: https://github.com/raditha-codev/mcp-demo/blob/main/DEVIN_SETUP.md
