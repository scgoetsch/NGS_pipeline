# Modernization roadmap

This document outlines the recommended next steps.

## Priority 1: metadata hardening

### Goal
Reduce ambiguity from filename-prefix grouping.

### Proposed changes
- define one canonical manifest format per pipeline
- reduce reliance on `startswith` grouping behavior
- make grouping explicit via columns such as:
  - `sample_name`
  - `read1_fastq`
  - `read2_fastq`
  - `concat_group`
  - `merge_group`
- for calibrated ChIP-seq, consider explicit:
  - `sample_name`
  - `chip_fastq_prefix`
  - `input_fastq_prefix`
  - `condition`

### Benefit
Clearer semantics, fewer accidental prefix collisions, easier reproducibility.

## Priority 2: workflow hardening

### Goal
Make rule dependencies more local and less historical.

### Proposed changes
- replace more broad `expand(...)` inputs with helper functions
- simplify wildcard usage across rules
- remove remaining cartesian-product style expansions in `rule all`
- add small tests around helper modules

### Benefit
Smaller DAGs, clearer reruns, fewer surprising rebuild chains.

## Priority 3: CI improvement

### Goal
Move from inline CI scripts to reusable fixtures.

### Proposed changes
- move synthetic fixture configs into versioned test directories
- add reusable dry-run scripts
- add config/sample-sheet validation checks
- optionally validate generated `trackDb.txt`

### Benefit
Cleaner CI and easier maintenance.

## Priority 4: execution portability

### Goal
Improve portability across systems.

### Proposed changes
- document cluster usage more formally
- consider optional containers later
- define a lockfile refresh policy

### Benefit
More reproducible use across clusters and users.

## Priority 5: version uplift branch

### Goal
Test a future Snakemake / Python upgrade in isolation.

### Proposed changes
- create a dedicated migration branch
- re-solve Pixi environments against newer Python where possible
- test wrappers and workflow behavior with newer Snakemake
- expect incremental fixes, not a drop-in bump

### Benefit
Long-term maintainability without destabilizing current users.
