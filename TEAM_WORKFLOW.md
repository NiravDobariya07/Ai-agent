# AI Agent Team Workflow

This file turns the team definition into a repeatable working model.

## Team Members

- `Dhruv Patel` (`orchestrator_agent`): planning, delegation, review, delivery tracking
- `Meet Shah` (`backend_laravel_agent`): Laravel backend, database, APIs, business logic
- `Krunal Desai` (`frontend_ui_agent`): UI, API integration, responsiveness, user flows
- `Jignesh Parmar` (`qa_testing_agent`): testing, defect reporting, regression checks

## Standard Delivery Flow

1. `orchestrator_agent` receives a feature request or bug report.
2. The orchestrator writes a short brief containing:
   - objective
   - scope
   - acceptance criteria
   - dependencies
   - owner
3. `backend_laravel_agent` completes backend work if the task needs APIs, validation, database changes, or server-side logic.
4. `frontend_ui_agent` completes UI work and integrates required backend endpoints.
5. `qa_testing_agent` validates the feature against the acceptance criteria.
6. If QA finds defects, the task returns to the responsible developer and then comes back to QA for retesting.
7. The orchestrator marks the task complete only after QA approval.

## Handoff Rules

- Every task must have one owner at a time.
- The orchestrator must define acceptance criteria before implementation starts.
- Backend and frontend agents should document anything the next agent needs to continue without guesswork.
- QA should report defects with reproduction steps, expected result, and actual result.
- Urgent fixes can skip unrelated stages, but QA review should still happen before final closure.

## Definition Of Done

A task is `Done` only when:

- scope is implemented
- acceptance criteria are met
- affected user flow is tested
- defects are resolved or explicitly accepted
- the orchestrator records the final status

## Suggested Task Template

```md
Task Title:
Owner:
Status:

Objective:

Acceptance Criteria:
- ...

Dependencies:
- ...

Implementation Notes:
- ...

QA Result:
- Pass / Fail
- Notes:
```
