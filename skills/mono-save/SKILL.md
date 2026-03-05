---
name: mono-save
description: Save the current conversation context to mono-memory
---

# Mono Save

Save the current work context to the shared team memory.

## Important

- Do NOT use AskUserQuestion tool. Just ask in plain text and wait for the user's reply.
- If the user provides content directly after `/mono-save`, use that as the content to save.

## Steps

1. Check if `CLAUDE.md` exists in the current project root. Read the `author` and `project` values from the "Recording Format" section.
   - If not found, ask the user for author and project name in plain text.

2. If the user provided content after the command (e.g. `/mono-save fixed the login bug`), use that as the content.
   Otherwise, ask in plain text:
   ```
   What would you like to save?
   ```

3. Ask for tags in plain text:
   ```
   Tags (comma-separated, or press Enter to skip):
   ```

4. Call `memory_save` with the gathered values:
   - `author`: from CLAUDE.md or user input
   - `project`: from CLAUDE.md or user input
   - `content`: always in English. If the user wrote in another language, translate to English.
   - `tags`: from user input (optional)

5. Print the result:
   ```
   Saved!

   | Field   | Value          |
   |---------|----------------|
   | ID      | `<id>`         |
   | Author  | `<author>`     |
   | Project | `<project>`    |
   | Tags    | `<tags>`       |
   ```
