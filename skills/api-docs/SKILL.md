---
name: api-docs
description: Generate Swagger-style HTML API documentation from mono-memory observations
---

# API Docs Generator

## Steps

1. Detect project name from current directory name.

2. Search API-related memories in parallel:
   - `memory_search(query: "API endpoint route", project: "<project>")`
   - `memory_search(query: "request response schema", project: "<project>")`
   - `memory_search(query: "API change update", project: "<project>")`
   - `memory_context(project: "<project>", section: "api")`

3. `memory_timeline(project: "<project>", limit: 100)` — filter API-relevant ones.

4. Combine and deduplicate all results.

5. **Cache check**: Read `.api-docs-cache.json` if it exists.
   - Compare memory IDs and `created_at` with cache.
   - Determine **new**, **updated**, **removed** memories.
   - If **no changes**: print `No changes detected. api-docs.html is up to date.` and stop.

6. **Patch mode** (api-docs.html exists AND partial changes):
   - Read existing `api-docs.html`
   - Edit only changed endpoint sections (add/update/remove)
   - MUST NOT re-read template files
   - Skip to step 9

7. **Full mode** (first run OR too many changes):
   - Read template via Bash:
     ```bash
     cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/index.html
     cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/styles.css
     cat ~/.claude/plugins/mono-memory-mcp/api-docs-template/script.js
     ```
     MUST NOT search or explore — just read these 3 files directly.
   - Generate single self-contained HTML (inline CSS + JS)
   - Group endpoints by base path (e.g. `/api/v1/users/*` → **Users**)
   - Keep all template features: Try it panels, auth dropdown, param tables, Send/Copy curl

8. **Save cache** `.api-docs-cache.json`:
   ```json
   {
     "generated_at": "<ISO timestamp>",
     "memories": [{"id": "<uuid>", "created_at": "<timestamp>"}]
   }
   ```

9. If no API memories found:
   ```
   No API-related memories found for project "<project>".

   Save some first:
   - memory_save(project: "<project>", content: "GET /api/users - returns paginated user list", tags: "api,endpoint")
   - memory_init(project: "<project>", section: "api", content: "REST API base URL: /api/v1 ...")
   ```

10. On success:
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
