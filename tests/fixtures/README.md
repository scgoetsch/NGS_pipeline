# Test fixtures

Reusable synthetic fixtures for Pixi/Snakemake dry-run validation live here.

Current fixtures:

- `catch-up-merge-aware/`
- `chip-calibrated-basic/`
- `bulk-rna-merge-aware/`

These fixtures are intentionally minimal:
- empty placeholder FASTQ files
- minimal sample sheets
- minimal config files for dry-run DAG construction
- placeholder annotation files where Snakemake requires an input path

They are used by `.github/workflows/pixi.yml`.
