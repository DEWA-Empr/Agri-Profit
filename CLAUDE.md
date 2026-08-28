## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: one `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Agent Working Rules

### Token Efficiency

* Do not explain code, files, or decisions unless I explicitly ask for an explanation.
* Inspect the repository and existing documentation before asking me for information that can be determined from the project.
* Do not repeat context, requirements, or decisions already established in the conversation.
* Do not reread files or documentation that you have already inspected unless they may have changed or the task requires verification.
* Read only the files relevant to the current task. Do not scan the entire repository by default.
* Do not read every project documentation file for every task.
* Prefer targeted searches and specific file reads over broad repository exploration.
* When you need project context, consult only the relevant documentation:

  * `CONTEXT.md` — project context and decisions
  * `PRD.md` — product requirements
  * `PROGRESS.md` — current implementation status
  * `STRUCTURE.md` — repository structure
* Before reading a documentation file, determine whether its information is actually needed for the current task.
* Do not quote large sections of files in your response. Summarize only what is necessary.
* Keep tool calls focused. Avoid redundant searches, duplicate file reads, and unnecessary repository scans.
* If the task is straightforward and the required context is already available, act immediately rather than performing additional discovery.
* After making changes, inspect only the relevant changed files or sections to verify the work.
* Do not provide a long summary after completing a task. Report only what changed, important issues, and anything requiring my attention.

### Communication

* Return concise results unless there is a failure, ambiguity, or an important decision that requires explanation.
* Do not narrate your internal process or every tool call.
* Do not explain obvious implementation details.
* Do not provide unsolicited suggestions or refactoring ideas unless they are relevant to the current task.
* If there is ambiguity that materially affects the implementation, ask before proceeding. Otherwise, make the reasonable choice and continue.
* When reporting changes, use a short bullet list with file paths and a brief description.

## Project Documentation

Before making architectural or scope decisions, consult the relevant project documentation:

* `CONTEXT.md` — project context and decisions
* `PRD.md` — product requirements
* `PROGRESS.md` — current implementation status
* `STRUCTURE.md` — repository structure

Read only the documents relevant to the current task. Do not read every project document by default.

### Documentation Priority

When information overlaps or conflicts, use this priority:

1. Current task requirements
2. `PRD.md` for product requirements
3. `CONTEXT.md` for project decisions and constraints
4. `PROGRESS.md` for implementation status
5. `STRUCTURE.md` for repository organization
6. Existing code and tests as the source of truth for current implementation behavior

### Repository Exploration

* Start with the smallest amount of information needed to understand the task.
* Locate the relevant files first, then inspect their contents.
* Follow imports, references, and dependencies only when necessary.
* Avoid opening unrelated files merely to gain general familiarity with the project.
* Do not inspect generated files, dependencies, build output, or `.git` history unless the task specifically requires them.

### Execution

* Prefer making the requested change directly when the requirements are clear.
* Preserve existing patterns and architecture unless the task requires changing them.
* Avoid unrelated refactoring.
* Keep changes minimal and focused.
* Run the smallest relevant test or verification needed to confirm the change.
* If verification fails, report the failure and the relevant cause rather than dumping the full output.

