---
name: api-docs
description: Generate API documentation as an HTML file from memories stored in mono-memory
---

# API Docs Generator

Generate a beautiful HTML API documentation page from memories stored in the mono-memory MCP server.
Uses caching — if `api-docs.html` already exists and nothing changed, patch only the diff instead of regenerating from scratch.

## Steps

1. Detect the project name automatically from the current directory name (`os.path.basename(os.getcwd())`).

2. Search for API-related memories using the MCP tools (call ALL of these in parallel):
   - `memory_search(query: "API endpoint route", project: "<project>")`
   - `memory_search(query: "request response schema", project: "<project>")`
   - `memory_search(query: "API change update", project: "<project>")`
   - `memory_context(project: "<project>", section: "api")` — may return not_found, that's OK

3. Also call `memory_timeline(project: "<project>", limit: 100)` to get all observations, then filter for API-relevant ones.

4. Combine and deduplicate all results.

5. **Cache check**: Read `.api-docs-cache.json` if it exists.
   - Compare the current memory IDs and `created_at` timestamps with the cache.
   - Determine which memories are **new**, **updated**, or **removed** since last generation.
   - If **no changes**: read existing `api-docs.html`, output it as-is, print `No changes detected. api-docs.html is up to date.` and stop.

6. **If `api-docs.html` already exists AND there are only partial changes**:
   - Read the existing `api-docs.html`
   - Only modify the endpoint sections that changed (add new, update modified, remove deleted)
   - Do NOT re-read the template files — just edit the existing HTML directly
   - Skip to step 9

7. **If `api-docs.html` does NOT exist (first run) OR too many changes to patch**:
   - Read the template files from the plugin's `api-docs-template/` folder using Bash:
     ```bash
     cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/index.html
     cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/styles.css
     cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/script.js
     ```
     Do NOT search for or explore these files. Just read the 3 files above directly.
   - Generate `api-docs.html` from scratch:
     - Use the template's HTML structure, CSS, and JS as-is
     - Inline all CSS and JS into a single self-contained HTML file
     - Group endpoints by base path (like Spring `@RequestMapping`)
     - Keep all template features: Try it panels, auth dropdown, param tables, Send/Copy curl buttons

8. Group endpoints by their **base path**:
   - Extract the common path prefix from each endpoint (e.g. `/api/v1/users/*` → group name **Users**, `/api/v1/auth/*` → group name **Auth**)
   - Each group becomes a separate section with the group name as heading and base path shown beside it
   - Table of contents lists each group with its base path

9. **Save cache**: Write `.api-docs-cache.json`:
   ```json
   {
     "generated_at": "<ISO timestamp>",
     "memories": [
       {"id": "<uuid>", "created_at": "<timestamp>"},
       ...
     ]
   }
   ```

10. If no API-related memories are found, inform the user:
    ```
    No API-related memories found for project "<project>".

    Save some API observations first:
    - memory_save(project: "<project>", content: "GET /api/users - returns paginated user list", tags: "api,endpoint")
    - memory_init(project: "<project>", section: "api", content: "REST API base URL: /api/v1 ...")
    ```

11. On success, print:
    ```
    API documentation generated!

    | Item     | Value                |
    |----------|----------------------|
    | Project  | `<project>`          |
    | File     | `./api-docs.html`    |
    | Entries  | <count> memories     |
    | Mode     | <full / patched>     |

    Open the file in a browser to view.
    ```
