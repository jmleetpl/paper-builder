# Paper Builder

Reusable orchestration layer that sits on top of `manuscript-harness-kit`.

This repository is for people who want more than a static harness:

- start from a topic, dataset, and target journal
- create a workspace with fixed folders and runbooks
- link or clone the manuscript harness automatically
- materialize a harness-ready project config
- generate a stage-by-stage execution plan
- assemble a clean author handoff folder after the manuscript stabilizes

## What this repo is

`paper-builder` is not a replacement for `manuscript-harness-kit`.

Instead:

- `manuscript-harness-kit` is the reusable core
- `paper-builder` is the orchestration layer above it

Use this repo when you want a repeatable project launcher and conductor for manuscript work.

## Current scope

Implemented now:

- engine config model
- workspace bootstrap
- manuscript-harness clone/link workflow
- harness project materialization
- pipeline runbook generation through the harness
- journal intake scaffold
- final author handoff assembly through the harness
- preflight environment checks

Not fully implemented yet:

- automatic web retrieval and parsing of journal author instructions from journal name alone
- one-command full statistics pipeline for arbitrary data schemas
- automatic creation of a live Zotero-field DOCX
- fully autonomous agent orchestration without human review checkpoints

## Related repo

- harness core: [manuscript-harness-kit](https://github.com/jmleetpl/manuscript-harness-kit)

## Quick start

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Bootstrap a new engine workspace:

```bash
python3 scripts/bootstrap_workspace.py config/engine.example.yaml
```

Clone the harness into `vendor/`:

```bash
python3 scripts/clone_harness.py
```

Create a journal intake packet:

```bash
python3 scripts/create_journal_intake.py config/engine.example.yaml
```

Materialize a harness-ready project and generate the staged pipeline:

```bash
python3 scripts/materialize_harness_project.py config/engine.example.yaml
```

Run a preflight check:

```bash
python3 scripts/preflight_check.py config/engine.example.yaml
```

After the manuscript is finalized, assemble an author handoff folder:

```bash
python3 scripts/assemble_author_handoff.py config/engine.example.yaml
```

## Package structure

```text
paper-builder/
├── .agents/
├── plugins/
├── config/
├── examples/
├── scripts/
├── templates/
├── ARCHITECTURE.md
├── ROADMAP.md
├── TUTORIAL.md
└── TUTORIAL_KO.md
```

## Notes

- The engine expects a compatible `manuscript-harness-kit` checkout.
- By default it can clone the public harness repo into `vendor/`.
- Journal auto-fetch from web is a future feature. For now the engine scaffolds a journal intake file and supports an explicit guideline URL.
- RIS and Zotero-library workflows are supported through the harness, but live Zotero fields inside Word remain a user-environment step.
