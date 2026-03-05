---
name: mono-read
description: Search and read memories from mono-memory
---

# Mono Read

Search and display memories from the shared team memory.

## Important

- Do NOT use AskUserQuestion tool. Just ask in plain text and wait for the user's reply.
- If the user provides a query directly after `/mono-read`, use that as the search query.

## Steps

1. Check if `CLAUDE.md` exists in the current project root. Read the `project` value from the "Recording Format" section.
   - If not found, ask the user for project name in plain text.

2. If the user provided a query after the command (e.g. `/mono-read auth bug`), use that as the search query.
   Otherwise, ask in plain text:
   ```
   Search query (keywords):
   ```

3. Call these in parallel:
   - `memory_search(query: "<query>", project: "<project>")`
   - `memory_timeline(project: "<project>", limit: 10)`

4. Display the results in a clean format:
   ```
   ## Search Results for "<query>"

   ### 1. <title/summary>
   - **Author**: <author>
   - **Date**: <date>
   - **Tags**: <tags>
   - **Content**: <content>

   ---
   ### 2. ...
   ```

5. If no results found:
   ```
   No memories found for "<query>" in project "<project>".
   ```
