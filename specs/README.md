# Specs: how to ask for changes

This folder is where the project is decided. **Partners change the specs. The coding agent changes the code.**
If a result is wrong, fix the spec. Don't fix the code.

## The loop

1. Edit a spec (or copy `_template.md` to start a new one).
2. Write or change **acceptance criteria**, one checkable statement per line, each with an ID.
3. Set `**Status:** ready`.
4. Ask the agent to "implement ready specs". It updates code, tests and evals, then sets the status to `implemented` and logs the change in `CHANGELOG.md`.
5. Review the pull request and the eval report it links to. If the agent left questions under **Open questions**, answer them and set the status back to `ready`.

## Status values

| Status | Meaning |
|--------|---------|
| `draft` | Still being written. The agent ignores it. |
| `ready` | Please implement. |
| `implemented` | Code, tests and evals match this spec. CI checks every criterion is covered. |
| `needs-review` | The agent found a problem or question. See **Open questions**. |

## Writing good acceptance criteria

A good criterion is something a test or an evaluation can check, and that someone could disagree with.

| Vague (avoid) | Checkable (use) |
|---------------|-----------------|
| Dates should be clean. | **DATA-001**: Every record has a date in YYYY-MM-DD format. |
| Protect sensitive records. | **DATA-002**: Records marked restricted never appear in `data/processed/`. |
| Labels should be accurate. | **EVAL-001**: The topic label is exactly one of: family, supplies, combat, health, other. |
| The model shouldn't be squeamish. | **EVAL-003**: Excerpts describing violence are summarized, not refused. |

Rules for IDs:
- Use the spec's prefix plus a number: `DATA-004`.
- Never reuse or renumber an ID. Tests and evals point at them.
- To retire a criterion, strike it through: `~~**DATA-002**: ...~~`.

## Editing from anywhere

Specs are plain Markdown on purpose, so any editor works.

- **GitHub website:** open the file, click the pencil, edit, then choose "Create a new branch… and start a pull request".
- **VS Code / Zed / any text editor:** edit and save. Commit the change, or ask the agent to.
- **Google Docs / Word:** write there if you prefer, then *File → Download → Markdown* (or copy and paste) into the spec file. Keep the bold `**Status:**` lines at the top and the `**ID**:` at the start of each criterion. Small formatting changes from your editor (bullets, quotes, blank lines) are fine.
