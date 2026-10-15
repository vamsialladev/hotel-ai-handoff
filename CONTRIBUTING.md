# Contributing

- Commits follow [Conventional Commits](https://www.conventionalcommits.org/) (`docs:`, `feat:`, `fix:`, `ci:`).
- Change a runbook when an incident teaches something: add the step that was missing and the check that proves it.
- A new runbook needs: how you notice it, numbered steps, and "Check it worked".
- Numbers in these documents come from saved runs in the linked repos. Link the report; never round up.
- Before a pull request: `python -m pytest -q`, `ruff check .`, and a markdown lint (CI runs markdownlint and a link
  check on every push).
