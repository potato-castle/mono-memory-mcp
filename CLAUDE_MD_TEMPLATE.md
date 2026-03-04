# ============================================
# Team Shared Memory MCP — CLAUDE.md Template
#
# Usage:
#   1. Append the content below to your project's CLAUDE.md
#   2. Replace {PROJECT_NAME} with your actual project name
#   3. Replace {AUTHOR_NAME} with your name
#
# Example project names:
#   - my-app          (frontend)
#   - my-backend      (backend server)
#   - my-mobile       (mobile app)
#   - my-tool         (CLI / desktop tool)
# ============================================

## Team Shared Memory (mono-memory MCP)

### Auto-Recording Rules
When any of the following occur during work, **always** record them with `memory_save`:

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
- author: "{AUTHOR_NAME}"
- project: "{PROJECT_NAME}"
- content: Always write in English, regardless of the conversation language. Describe specifically what was discovered/decided/resolved.
- tags: relevant,comma,separated

### Tag Guide

**Common**
| Tag | Use for |
|-----|---------|
| `bug`, `fix` | Bug-related |
| `architecture`, `design` | Design decisions |
| `api` | API changes |
| `config`, `env` | Configuration, environment variables |
| `db`, `schema`, `migration` | Database/schema changes |
| `deploy`, `ci` | Deployment, CI/CD |
| `dependency` | Dependency changes |
| `performance` | Performance |
| `security` | Security |
| `tip`, `gotcha` | Pitfall-prevention tips |

**Project-specific (use as applicable)**
| Tag | Use for |
|-----|---------|
| `frontend`, `react`, `vue`, `css` | Web frontend |
| `backend`, `node`, `express`, `django` | Backend server |
| `mobile`, `flutter`, `swift`, `kotlin` | Mobile apps |
| `infra`, `docker`, `k8s`, `aws` | Infrastructure |

### At Session Start
Search for related records at the beginning of each session:
- memory_search(query: "keywords for your task", project: "{PROJECT_NAME}")

To also see records from other projects, omit the project filter:
- memory_search(query: "keywords")

### Check Project Context
To review project structure or conventions:
- memory_context(project: "{PROJECT_NAME}")
