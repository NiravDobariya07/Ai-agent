# Repository Guidelines

## Project Structure & Module Organization
This repository currently defines an AI-assisted software team rather than an application codebase. The primary source of truth is [ai_agent_team_gujarat_names.md](/var/www/html/development-agent-team/ai_agent_team_gujarat_names.md), which names the four core agents and their responsibilities. The `.zencoder/workflows/` and `.zenflow/workflows/` directories exist as placeholders for future workflow automation, but they do not contain runnable definitions yet. Add new team-process documents at the repository root until a real product codebase is introduced.

## Agent Instructions
Work through the team in the documented order: orchestrator first, implementation agents next, QA last. Keep role boundaries clear. The orchestrator should convert requirements into scoped tasks with acceptance criteria. Backend work should own APIs, validation, business logic, and persistence concerns. Frontend work should own UI, API consumption, and user flow quality. QA should verify completed behavior and return defects to the correct owner instead of silently redefining scope.

## Build, Test, and Development Commands
There is no app build system yet, but the repository now includes local agent definitions in `agents/team.json` and a small CLI helper in `scripts/run_agent.py`. Use `python3 scripts/run_agent.py list` to see available agents, `python3 scripts/run_agent.py show orchestrator_agent` to inspect one definition, `python3 scripts/run_agent.py run orchestrator_agent "Create login feature plan"` to generate a ready-to-use prompt, and `python3 scripts/run_agent.py brief backend_laravel_agent "Build login API"` to create a task brief template.

## Coding Style & Naming Conventions
Use Markdown for operational documentation and keep headings descriptive and stable. Preserve the established agent IDs in snake_case, for example `orchestrator_agent` and `qa_testing_agent`, because those identifiers are the most likely integration points for future workflow tooling. Prefer concise responsibility lists and explicit task-flow wording over broad or generic process language.
