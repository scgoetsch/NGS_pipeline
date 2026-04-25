# Modernization status

This document summarizes completed modernization work in this fork.

## Scope

Modernization has focused on:

- `genetics/CATCH-UP`
- `genetics/ChIP-Seq-Calibrated`
- `transcriptomics/Bulk-RNA-seq`
- root-level Pixi environment management
- CI dry-run validation

## Repository-level updates

Added:

- `pixi.toml`
- `pixi.lock`
- `PIXI.md`
- `.github/workflows/pixi.yml`
- `.gitignore`

### Pixi environments

The project now uses smaller environments:

- `default` / `catch-up`
- `reference-genomes`
- `build-calibration-genome`
- `ucsc-track-hub`
- `chip-calibrated`
- `bulk-rna`
- `all`

## CATCH-UP

### New files
- `genetics/CATCH-UP/workflow_utils.py`
- `genetics/CATCH-UP/config/DNase_example.samples.tsv`
- `genetics/CATCH-UP/submit.pixi.sh`

### Main updates
- centralized config normalization
- sample-sheet support
- YAML boolean support with backward compatibility
- Pixi SLURM launcher
- reduced repeated metadata re-loading
- cleaner merge / concat input construction
- standardized track URL generation
- started metadata hardening with explicit `sample_name` / `merge_group` support
- replaced several broad DAG target expansions and filename-prefix globs with explicit metadata-driven targets

### Sample-sheet columns
- `fastq_prefix` required
- `sample_name` preferred for explicit analysis-level grouping
- `merge_group` preferred for explicit merge grouping
- legacy aliases still supported: `concat_sample`, `merge_sample`

### Legacy mode preserved
- `1_fastqfile_home_dir.txt`
- `2_fastqfile_concat.txt`
- `3_merge_bams.txt`

## Calibrated ChIP-seq

### New files
- `genetics/ChIP-Seq-Calibrated/workflow_utils.py`
- `genetics/ChIP-Seq-Calibrated/config/example.samples.tsv`
- `genetics/ChIP-Seq-Calibrated/submit.pixi.sh`

### Main updates
- centralized config normalization
- sample-sheet support
- YAML boolean support with backward compatibility
- Pixi SLURM launcher
- fixed a pre-existing syntax error in `rules/01_upstream.smk`
- standardized track URL generation
- reduced repeated metadata re-loading
- replaced several broad DAG target expansions with explicit helper-generated targets
- narrowed some rule dependencies to per-sample metadata-driven inputs

### Sample-sheet columns
- `chip_fastq_prefix` required
- `input_fastq_prefix` required when `input_provided: true`

### Legacy mode preserved
- `fastqfile_home_dir.txt`

## Bulk RNA-seq

### New files
- `transcriptomics/Bulk-RNA-seq/workflow_utils.py`
- `transcriptomics/Bulk-RNA-seq/config/example.samples.tsv`
- `transcriptomics/Bulk-RNA-seq/submit.pixi.sh`

### Main updates
- centralized config normalization
- sample-sheet support
- YAML boolean support with backward compatibility
- Pixi SLURM launcher
- reduced repeated metadata re-loading
- tightened some broad DAG inputs
- standardized track URL generation
- started metadata hardening with explicit `sample_name` / `merge_group` support
- replaced several broad DAG target expansions and filename-prefix globs with explicit metadata-driven targets

### Sample-sheet columns
- `fastq_prefix` required
- `sample_name` preferred for explicit analysis-level grouping
- `merge_group` preferred for explicit merge grouping
- legacy aliases still supported: `concat_sample`, `merge_sample`

### Legacy mode preserved
- `1_fastqfile_home_dir.txt`
- `2_fastqfile_concat.txt`
- `3_merge_bams.txt`

## CI status

CI now checks:

- install default Pixi environment
- dry-run bundled `CATCH-UP` example
- dry-run reusable `tests/fixtures/catch-up-merge-aware` fixture
- install `reference-genomes` environment
- install and dry-run reusable `tests/fixtures/chip-calibrated-basic` fixture
- install and dry-run reusable `tests/fixtures/bulk-rna-merge-aware` fixture

## Validation completed locally

Validated locally:

- `pixi run catch-up-example-dryrun`
- synthetic merge-aware CATCH-UP dry-run using explicit `sample_name` / `merge_group`
- synthetic dry-run for calibrated ChIP-seq
- synthetic dry-run for bulk RNA-seq
- synthetic merge-aware bulk RNA-seq dry-run using explicit `sample_name` / `merge_group`
- refreshed synthetic calibrated ChIP-seq dry-run after DAG hardening changes
