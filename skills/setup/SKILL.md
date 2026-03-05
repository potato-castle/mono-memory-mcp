---
name: setup
description: Configure mono-memory MCP server connection and CLAUDE.md for a project
---

# Setup

## Constraints

- MUST NOT use AskUserQuestion tool. Output plain text questions and wait for reply.
- MUST use Bash tool with `python3 -c` to write files (avoids Read/Write permission prompts).
- MUST write `.mcp.json` in the current project root (not `~/.mcp.json`).

## Steps

1. Print and wait for reply:
   ```
   ## Mono Memory Setup

   ---

   **Step 1/2** — Server URL

   Enter the full URL of your Mono Memory server:
   ```

2. Print and wait for reply:
   ```
   **Step 2/2** — Author

   Enter your name (used to tag memories you save):
   ```

3. Validate URL starts with `http://` or `https://`. If not, ask to re-enter.

4. Detect project name from current directory name.

5. Run setup via Bash. MUST pass inputs as environment variables (not string interpolation):
   ```bash
   SERVER_URL='<URL>' AUTHOR_NAME='<author>' python3 -c "
   import json, os, sys

   url = os.environ['SERVER_URL']
   author = os.environ['AUTHOR_NAME']
   project = os.path.basename(os.getcwd())

   if not url.startswith(('http://', 'https://')):
       print('Error: URL must start with http:// or https://')
       sys.exit(1)

   # 1. Write .mcp.json
   mcp_path = os.path.join(os.getcwd(), '.mcp.json')
   config = {}
   if os.path.exists(mcp_path):
       with open(mcp_path) as f:
           config = json.load(f)
   config.setdefault('mcpServers', {})
   config['mcpServers']['mono-memory'] = {
       'type': 'http',
       'url': url
   }
   with open(mcp_path, 'w') as f:
       json.dump(config, f, indent=2)

   # 2. Append to CLAUDE.md
   claude_path = os.path.join(os.getcwd(), 'CLAUDE.md')
   template = '''

   ## Team Shared Memory (mono-memory MCP)

   ### Auto-Recording Rules
   When any of the following occur during work, **always** record them with \`memory_save\`:

   1. **Bug found & resolved**: root cause, fix, related files
   2. **Architecture/design decision**: why this approach, what alternatives were considered
   3. **New pattern/convention**: project-specific patterns discovered while coding
   4. **API changes**: endpoint additions/modifications, request/response format changes
   5. **DB/schema changes**: tables, columns, migrations
   6. **Dependency changes**: packages added/updated/removed and why
   7. **Environment/deployment changes**: env vars, build config, deployment pipeline
   8. **Performance issues**: bottleneck causes and improvements
   9. **Hard-won lessons**: problems that took significant time to solve (help others avoid the same)

   ### Recording Format
   When calling memory_save:
   - author: \"{author}\"
   - project: \"{project}\"
   - content: Always write in English, regardless of the conversation language. Describe specifically what was discovered/decided/resolved.
   - tags: relevant,comma,separated

   ### At Session Start
   Search for related records at the beginning of each session:
   - memory_search(query: \"keywords for your task\", project: \"{project}\")

   ### Check Project Context
   To review project structure or conventions:
   - memory_context(project: \"{project}\")

   ### Shortcut Commands
   When the user types \"/api-docs\", run the /mono-memory-mcp:api-docs skill.
   '''.format(author=author, project=project)

   existing = ''
   if os.path.exists(claude_path):
       with open(claude_path) as f:
           existing = f.read()

   if 'Team Shared Memory' in existing:
       print('CLAUDE.md already has memory config — skipped.')
   else:
       with open(claude_path, 'a') as f:
           f.write(template)
       print('CLAUDE.md updated.')

   print('Done!')
   "
   ```

6. Print completion (fill in actual values):
   ```
   ---

   **Setup complete!**

   | Setting  | Value              |
   |----------|--------------------|
   | Server   | `<server URL>`     |
   | Author   | `<author name>`    |
   | Project  | `<project name>`   |
   | Config   | `./.mcp.json`      |
   | Memory   | `./CLAUDE.md`      |

   > Restart Claude Code to connect.
   ```
