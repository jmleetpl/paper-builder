---
name: paper-builder-pipeline
description: Use when the user wants to create a new manuscript workspace, link the harness, generate runbooks, or prepare an author handoff from a paper-builder project.
---

# Paper Builder Pipeline

This plugin skill wraps the high-level engine workflow.

## Main commands

```bash
python3 scripts/bootstrap_workspace.py config/engine.example.yaml
python3 scripts/clone_harness.py
python3 scripts/create_journal_intake.py config/engine.example.yaml
python3 scripts/materialize_harness_project.py config/engine.example.yaml
python3 scripts/assemble_author_handoff.py config/engine.example.yaml
```
