---
name: mono-summary
description: Display project context and recent team activity from mono-memory
---

# Mono Summary

## Constraints

- MUST NOT use AskUserQuestion tool.
- MUST run all MCP calls in parallel.

## Steps

1. Detect project name from current directory name.

2. Call in parallel:
   - `memory_context(project: "<project>")`
   - `memory_timeline(project: "<project>", limit: 20)`

3. Display:
   ```
   ## <project> — Project Summary

   ### Context

   **<section>**
   <content>

   ---

   ### Recent Activity (last 20)

   | Date | Author | Summary | Tags |
   |------|--------|---------|------|
   | <date> | <author> | <first line of content> | <tags> |
   ```

4. If nothing found:
   ```
   No memories found for project "<project>".

   Get started:
   - memory_init(project: "<project>", section: "overview", content: "Project description...")
   - memory_save(project: "<project>", content: "First observation", tags: "setup")
   ```
