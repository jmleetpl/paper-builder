---
name: paper-builder-orchestrator
description: Use when a user wants to launch a manuscript project from topic, dataset, and target journal, create a clean workspace, connect manuscript-harness-kit, generate pipeline runbooks, or prepare a final author handoff bundle.
---

# Paper Builder Orchestrator

Use this skill when the user wants to run a manuscript project through the engine layer rather than working directly in the harness.

## Workflow

1. Create or update the engine config.
2. Bootstrap the workspace.
3. Clone or connect the harness.
4. Create a journal intake packet.
5. Materialize the harness project.
6. Run preflight checks.
7. Assemble the final author handoff when the manuscript stabilizes.

## Commands

```bash
python3 scripts/bootstrap_workspace.py config/engine.example.yaml
python3 scripts/clone_harness.py
python3 scripts/create_journal_intake.py config/engine.example.yaml
python3 scripts/materialize_harness_project.py config/engine.example.yaml
python3 scripts/preflight_check.py config/engine.example.yaml
python3 scripts/assemble_author_handoff.py config/engine.example.yaml
```

## Notes

- This engine depends on `manuscript-harness-kit`.
- Journal auto-fetch from journal name alone is not yet implemented.
- Live Zotero fields inside Word are still a user-environment step.
