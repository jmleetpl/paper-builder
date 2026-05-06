# Architecture

`paper-builder` is designed as an orchestration layer above `manuscript-harness-kit`.

## Layers

1. Core harness
   - project config model
   - journal profiles
   - staged skills
   - validation scripts
   - submission assembly

2. Paper builder engine
   - workspace bootstrap
   - harness acquisition or linking
   - config translation
   - pipeline materialization
   - handoff assembly

3. Future autonomous layer
   - journal-guide fetching
   - automatic task routing
   - idea generation
   - review simulation loops
   - richer docx and Zotero integration

## Data flow

```text
engine config
  -> workspace bootstrap
  -> journal intake
  -> harness config generation
  -> harness init_project
  -> harness run_pipeline
  -> manuscript work
  -> harness submission assembly
  -> author handoff bundle
```

## Separation of concerns

- `paper-builder` should not duplicate the harness internals.
- The engine should call the harness where possible.
- Journal-specific formatting logic should stay in the harness.
- Project orchestration and packaging convenience should live in the engine.
