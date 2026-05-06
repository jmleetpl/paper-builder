# Tutorial: Paper Builder

This tutorial explains how to use `paper-builder` as the orchestration layer above `manuscript-harness-kit`.

## 1. What this repo does

Use this repo when you want to move from a loose manuscript process to a guided one.

It helps you:

- define a project once
- create a clean workspace
- link the harness core
- generate a harness-ready project
- discover likely journal profiles
- prepare journal intake and handoff packets

## 2. Install requirements

```bash
python3 -m pip install -r requirements.txt
```

## 3. Edit the engine config

Start from:

- `config/engine.example.yaml`

Edit:

- project slug and title
- topic and study question
- data paths
- target journal
- harness source mode

## 4. Create a workspace

```bash
python3 scripts/bootstrap_workspace.py config/engine.example.yaml
```

This creates:

- `workspaces/<slug>/inputs/`
- `workspaces/<slug>/journal/`
- `workspaces/<slug>/generated/`
- `workspaces/<slug>/pipeline/`
- `workspaces/<slug>/handoff/`
- `workspaces/<slug>/logs/`

## 5. Clone or link the harness

If you want the public harness:

```bash
python3 scripts/clone_harness.py
```

If you already have a local checkout, point `harness.local_path` in the engine config to that path.

## 6. Create a journal intake packet

```bash
python3 scripts/create_journal_intake.py config/engine.example.yaml
```

This does not fully parse journal author instructions yet.

It does:

- create a `journal_intake.md`
- save the journal name and optional guideline URL
- optionally snapshot a matching harness profile if one is already known

You can also generate a journal-discovery report from the journal name:

```bash
python3 scripts/discover_journal.py config/engine.example.yaml
```

This creates:

- `journal/discovery_report.json`
- `journal/discovery_report.md`

## 7. Download the journal guide

If `journal.guideline_url` is set:

```bash
python3 scripts/fetch_journal_guide.py config/engine.example.yaml
```

This saves the raw guide under `journal/`.

If the response is HTML, it also creates:

- `journal/guideline_notes.md`

## 8. Create and edit a profile mapping

Run:

```bash
python3 scripts/map_journal_profile.py config/engine.example.yaml
```

This creates:

- `journal/profile_mapping.yaml`

Review and edit that file so it matches the live journal guide.

Then install the generated profile into the harness:

```bash
python3 scripts/install_harness_profile.py config/engine.example.yaml
```

## 9. Materialize the harness project

```bash
python3 scripts/materialize_harness_project.py config/engine.example.yaml
```

This step:

- maps the engine config to a harness project config
- writes `generated/project.for_harness.yaml`
- runs the harness `init_project.py`
- runs the harness `run_pipeline.py`

After that, you have a harness project ready for staged work.

You can also generate a stage-session packet for the next Codex task:

```bash
python3 scripts/prepare_stage_session.py config/engine.example.yaml 01_literature_scout
```

## 10. Or run the setup sequence in one command

```bash
python3 scripts/run_setup.py config/engine.example.yaml
```

This runs:

- workspace bootstrap
- harness clone
- journal intake
- journal discovery
- guide fetch when URL is present
- profile mapping generation
- harness profile install
- harness project materialization
- first stage session packet
- preflight check

## 11. Run a preflight check

```bash
python3 scripts/preflight_check.py config/engine.example.yaml
```

This checks:

- Python availability
- Git availability
- GitHub CLI auth
- harness path availability
- Zotero availability

## 12. Record structured stage progress

As stages are completed, record them in a structured run log:

```bash
python3 scripts/record_stage_run.py \
  config/engine.example.yaml \
  01_literature_scout \
  completed \
  --summary "Completed literature map and search log"
```

Then build a compact pipeline summary:

```bash
python3 scripts/summarize_run.py config/engine.example.yaml
```

## 13. Final handoff

When the manuscript is stable and the harness project has final outputs:

```bash
python3 scripts/assemble_author_handoff.py config/engine.example.yaml
```

This wraps the harness submission assembly and creates a clean handoff bundle for the author.

Validate that handoff packet:

```bash
python3 scripts/validate_submission_packet.py config/engine.example.yaml
```

## 14. Current limitations

- journal-name discovery is local and profile-based, not full web discovery
- no universal statistical engine for arbitrary datasets
- no automatic live Zotero fields in Word
- no fully autonomous manuscript generation without review gates
