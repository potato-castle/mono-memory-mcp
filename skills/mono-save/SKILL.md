---
name: mono-save
description: Save a discovery, decision, or insight to the shared team memory
---

# Mono Save

## Constraints

- MUST NOT use AskUserQuestion tool. Use plain text output and wait for reply.
- MUST translate content to English before saving.

## Steps

1. Read `author` and `project` from CLAUDE.md "Recording Format" section.
   - If not found, ask in plain text.

2. If user provided content after the command (e.g. `/mono-save fixed login bug`), use it.
   Otherwise ask:
   ```
   What would you like to save?
   ```

3. Ask:
   ```
   Tags (comma-separated, or press Enter to skip):
   ```

4. Call `memory_save(author, project, content, tags)`.

5. Print:
   ```
   Saved!

   | Field   | Value          |
   |---------|----------------|
   | ID      | `<id>`         |
   | Author  | `<author>`     |
   | Project | `<project>`    |
   | Tags    | `<tags>`       |
   ```
