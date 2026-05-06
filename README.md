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
- journal-guide downloader from explicit URL
- profile-mapping template and harness-profile installer
- one-command setup entrypoint
- journal-name-based discovery report
- stage-session packet generation
- structured run logging and summary
- submission packet validation
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

Discover likely harness journal profiles from the journal name:

```bash
python3 scripts/discover_journal.py config/engine.example.yaml
```

Download the journal guide into the workspace:

```bash
python3 scripts/fetch_journal_guide.py config/engine.example.yaml
```

Create a profile mapping template and then install the generated harness profile:

```bash
python3 scripts/map_journal_profile.py config/engine.example.yaml
python3 scripts/install_harness_profile.py config/engine.example.yaml
```

Materialize a harness-ready project and generate the staged pipeline:

```bash
python3 scripts/materialize_harness_project.py config/engine.example.yaml
```

Or run the initial setup sequence in one command:

```bash
python3 scripts/run_setup.py config/engine.example.yaml
```

Prepare a focused stage session packet:

```bash
python3 scripts/prepare_stage_session.py config/engine.example.yaml 01_literature_scout
```

Record stage progress and build a structured pipeline summary:

```bash
python3 scripts/record_stage_run.py config/engine.example.yaml 01_literature_scout completed --summary "Completed search log and evidence table"
python3 scripts/summarize_run.py config/engine.example.yaml
```

Run a preflight check:

```bash
python3 scripts/preflight_check.py config/engine.example.yaml
```

After the manuscript is finalized, assemble an author handoff folder:

```bash
python3 scripts/assemble_author_handoff.py config/engine.example.yaml
```

Validate the final submission packet:

```bash
python3 scripts/validate_submission_packet.py config/engine.example.yaml
```

## Package structure

```text
paper-builder/
├── .agents/
├── plugins/
├── config/
├── data/
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
- The engine supports local journal-name discovery against known harness profiles and aliases, but full web-based discovery is still a future feature.
- RIS and Zotero-library workflows are supported through the harness, but live Zotero fields inside Word remain a user-environment step.
