---
name: mono-summary
description: Show a summary of the current project's memory context and recent activity
---

# Mono Summary

Display a full summary of the project's stored context and recent team activity.

## Important

- Do NOT use AskUserQuestion tool.
- Run all MCP calls in parallel for speed.

## Steps

1. Detect the project name from the current directory name.

2. Call these in parallel:
   - `memory_context(project: "<project>")` — get all stored sections
   - `memory_timeline(project: "<project>", limit: 20)` — get recent activity

3. Display the results:
   ```
   ## <project> — Project Summary

   ### Context
   (For each section from memory_context, display section name and content)

   **<section>**
   <content>

   ---

   ### Recent Activity (last 20)

   | Date | Author | Summary | Tags |
   |------|--------|---------|------|
   | <date> | <author> | <first line of content> | <tags> |
   | ... | ... | ... | ... |
   ```

4. If no context and no timeline entries:
   ```
   No memories found for project "<project>".

   Get started:
   - memory_init(project: "<project>", section: "overview", content: "Project description...")
   - memory_save(project: "<project>", content: "First observation", tags: "setup")
   ```
