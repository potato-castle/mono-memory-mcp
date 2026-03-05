---
name: mono-read
description: Search the shared team memory by keywords
---

# Mono Read

## Constraints

- MUST NOT use AskUserQuestion tool. Use plain text output and wait for reply.

## Steps

1. Read `project` from CLAUDE.md "Recording Format" section.
   - If not found, ask in plain text.

2. If user provided a query (e.g. `/mono-read auth bug`), use it.
   Otherwise ask:
   ```
   Search query (keywords):
   ```

3. Call in parallel:
   - `memory_search(query: "<query>", project: "<project>")`
   - `memory_timeline(project: "<project>", limit: 10)`

4. Display:
   ```
   ## Search Results for "<query>"

   ### 1. <summary>
   - **Author**: <author>
   - **Date**: <date>
   - **Tags**: <tags>
   - **Content**: <content>

   ---
   ### 2. ...
   ```

5. If no results:
   ```
   No memories found for "<query>" in project "<project>".
   ```
