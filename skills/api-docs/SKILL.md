---
name: api-docs
description: Generate API documentation as an HTML file from memories stored in mono-memory
---

# API Docs Generator

Generate a beautiful HTML API documentation page from memories stored in the mono-memory MCP server.

## Steps

1. Detect the project name automatically from the current directory name (`os.path.basename(os.getcwd())`).

2. Search for API-related memories using the MCP tools (call ALL of these in parallel):
   - `memory_search(query: "API endpoint route", project: "<project>")`
   - `memory_search(query: "request response schema", project: "<project>")`
   - `memory_search(query: "API change update", project: "<project>")`
   - `memory_context(project: "<project>", section: "api")` — may return not_found, that's OK

3. Also call `memory_timeline(project: "<project>", limit: 100)` to get all observations, then filter for API-relevant ones.

4. Combine and deduplicate all results. Group endpoints by their **base path** (like Spring `@RequestMapping`):
   - Extract the common path prefix from each endpoint (e.g. `/api/v1/users/*` → group name **Users**, `/api/v1/auth/*` → group name **Auth**)
   - Each group becomes a separate section with the group name as heading and base path shown beside it
   - Table of contents lists each group with its base path

5. Read the template files from the plugin's `api-docs-template/` folder using Bash:
   ```bash
   cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/index.html
   cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/styles.css
   cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/script.js
   ```
   Do NOT search for or explore these files. Just read the 3 files above directly.

6. Generate `api-docs.html` in the current project root based on the template:
   - Use the template's HTML structure, CSS, and JS as-is
   - Inline all CSS and JS into a single self-contained HTML file
   - Replace the sample endpoint data with the actual memories gathered in steps 2-4
   - Group endpoints by base path (like Spring `@RequestMapping`)
   - Keep all template features: Try it panels, auth dropdown, param tables, Send/Copy curl buttons

7. If no API-related memories are found, inform the user:
   ```
   No API-related memories found for project "<project>".

   Save some API observations first:
   - memory_save(project: "<project>", content: "GET /api/users - returns paginated user list", tags: "api,endpoint")
   - memory_init(project: "<project>", section: "api", content: "REST API base URL: /api/v1 ...")
   ```

8. On success, print:
   ```
   API documentation generated!

   | Item     | Value                |
   |----------|----------------------|
   | Project  | `<project>`          |
   | File     | `./api-docs.html`    |
   | Entries  | <count> memories     |

   Open the file in a browser to view.
   ```
