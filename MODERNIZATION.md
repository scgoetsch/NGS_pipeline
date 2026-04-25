# UpStreamPipeline modernization

This page is now an index for the modernization docs.

## Documents

- [`docs/modernization/status.md`](docs/modernization/status.md) — completed updates
- [`docs/modernization/roadmap.md`](docs/modernization/roadmap.md) — proposed next steps
- [`docs/modernization/testing.md`](docs/modernization/testing.md) — CI and validation notes
- [`docs/modernization/sample-sheets.md`](docs/modernization/sample-sheets.md) — current sample-sheet formats
- [`docs/modernization/review-notes.md`](docs/modernization/review-notes.md) — suggested commit plan and PR summary

## Summary

The repository has been modernized around these principles:

- keep **Snakemake** as the workflow engine
- use **Pixi** as the primary environment manager
- support **modern sample sheets** while preserving legacy inputs
- centralize config normalization and workflow input preparation
- validate changes with lightweight CI dry-runs
