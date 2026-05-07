# Modernization review notes

This document summarizes the current modernization work in a review-friendly way.

## Recommended commit plan

### 1. Add Pixi workspace and CI foundation
Scope:
- `pixi.toml`
- `pixi.lock`
- `.github/workflows/pixi.yml`
- `.gitignore`
- `PIXI.md`
- top-level `README.md`
- `MODERNIZATION.md`
- `docs/modernization/status.md`
- `docs/modernization/roadmap.md`
- `docs/modernization/testing.md`
- `docs/modernization/sample-sheets.md`
- `docs/modernization/review-notes.md`
- `tests/fixtures/**`

Suggested message:
- `Add Pixi environments, CI dry-runs, and modernization docs`

### 2. Modernize CATCH-UP metadata handling
Scope:
- `genetics/CATCH-UP/workflow_utils.py`
- `genetics/CATCH-UP/Snakefile`
- `genetics/CATCH-UP/rules/01_upstream.smk`
- `genetics/CATCH-UP/rules/02_qc.smk`
- `genetics/CATCH-UP/rules/03_trackDb.smk`
- `genetics/CATCH-UP/rules/04_folders.smk`
- `genetics/CATCH-UP/config/analysis.yaml`
- `genetics/CATCH-UP/config/DNase_example.yaml`
- `genetics/CATCH-UP/config/schema/config.schema.yaml`
- `genetics/CATCH-UP/config/DNase_example.samples.tsv`
- `genetics/CATCH-UP/README.md`
- `genetics/CATCH-UP/submit.pixi.sh`

Suggested message:
- `Modernize CATCH-UP with Pixi and explicit sample-sheet metadata`

### 3. Modernize calibrated ChIP-seq metadata handling
Scope:
- `genetics/ChIP-Seq-Calibrated/workflow_utils.py`
- `genetics/ChIP-Seq-Calibrated/Snakefile`
- `genetics/ChIP-Seq-Calibrated/rules/01_upstream.smk`
- `genetics/ChIP-Seq-Calibrated/rules/03_trackDb.smk`
- `genetics/ChIP-Seq-Calibrated/rules/04_folders.smk`
- `genetics/ChIP-Seq-Calibrated/config/analysis.yaml`
- `genetics/ChIP-Seq-Calibrated/config/schema/config.schema.yaml`
- `genetics/ChIP-Seq-Calibrated/config/example.samples.tsv`
- `genetics/ChIP-Seq-Calibrated/README.md`
- `genetics/ChIP-Seq-Calibrated/submit.pixi.sh`

Suggested message:
- `Modernize calibrated ChIP-seq inputs and harden DAG targets`

### 4. Modernize bulk RNA-seq metadata handling
Scope:
- `transcriptomics/Bulk-RNA-seq/workflow_utils.py`
- `transcriptomics/Bulk-RNA-seq/Snakefile`
- `transcriptomics/Bulk-RNA-seq/rules/01_upstream.smk`
- `transcriptomics/Bulk-RNA-seq/rules/02_qc.smk`
- `transcriptomics/Bulk-RNA-seq/rules/03_trackDb.smk`
- `transcriptomics/Bulk-RNA-seq/rules/04_folders.smk`
- `transcriptomics/Bulk-RNA-seq/config/analysis.yaml`
- `transcriptomics/Bulk-RNA-seq/config/schema/config.schema.yaml`
- `transcriptomics/Bulk-RNA-seq/config/example.samples.tsv`
- `transcriptomics/Bulk-RNA-seq/README.md`
- `transcriptomics/Bulk-RNA-seq/submit.pixi.sh`

Suggested message:
- `Modernize bulk RNA-seq inputs and harden metadata-driven DAG construction`

## High-level PR summary

This modernization keeps Snakemake as the workflow engine while adding Pixi-managed environments, reusable CI dry-run fixtures, and safer metadata-driven workflow input handling.

### Main changes
- added a root Pixi workspace with per-pipeline environments and tasks
- added CI that installs environments and runs Snakemake dry-runs
- introduced helper modules to normalize config values and prepare workflow inputs
- added modern TSV/CSV sample-sheet support to the target workflows
- preserved legacy text-file input formats for backward compatibility
- accepted both YAML booleans and legacy string booleans
- reduced broad wildcard expansion and filename-prefix globbing in several rules
- made more DAG edges explicit through helper-generated target lists and metadata maps
- documented current status, roadmap, testing, and sample-sheet conventions
- added reusable synthetic fixtures under `tests/fixtures/`

### Workflow-specific highlights

#### CATCH-UP
- supports explicit `sample_name` and `merge_group`
- still supports legacy `concat_sample` and `merge_sample`
- uses metadata-derived concat/merge maps
- includes a reusable merge-aware dry-run fixture

#### Calibrated ChIP-seq
- supports sample sheets via `chip_fastq_prefix` and optional/required `input_fastq_prefix`
- reduced broad DAG target generation
- made `trackDb` depend on explicit bigWig outputs
- fixed a pre-existing syntax issue in upstream rules during modernization

#### Bulk RNA-seq
- supports explicit `sample_name` and `merge_group`
- still supports legacy `concat_sample` and `merge_sample`
- uses metadata-derived concat/merge maps
- aligns duplicate/merge QC targets more closely with actual merged outputs
- includes a reusable merge-aware dry-run fixture

## Validation summary

Validated locally:
- `pixi install`
- `pixi run catch-up-example-dryrun`
- calibrated ChIP synthetic dry-run
- bulk RNA synthetic dry-run
- merge-aware CATCH-UP fixture dry-run
- merge-aware bulk RNA fixture dry-run
- reusable fixture-based dry-runs for calibrated ChIP and bulk RNA

CI currently checks:
- default Pixi environment installation
- bundled CATCH-UP example dry-run
- reusable CATCH-UP fixture dry-run
- reference-genomes environment installation
- reusable calibrated ChIP fixture dry-run
- reusable bulk RNA fixture dry-run

## Snakemake/Python uplift status

The Pixi workspace now targets:
- Python `3.11.*`
- Snakemake `>=8,<9`

The earlier solver mismatch is resolved in `pixi.lock` and the reusable CI dry-runs were revalidated after the upgrade.
Future Snakemake 9 or Python 3.12 work should be tracked separately.
