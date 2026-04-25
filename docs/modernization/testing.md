# Modernization testing notes

## Current CI checks

Defined in `.github/workflows/pixi.yml`.
Reusable synthetic fixtures now live under `tests/fixtures/`.

### CATCH-UP
- install default Pixi environment
- run `pixi run catch-up-example-dryrun`
- run a Snakemake dry-run against `tests/fixtures/catch-up-merge-aware/config.yaml`
- this fixture validates explicit `sample_name` and `merge_group` handling for concatenation plus BAM merging

### Reference genomes
- install `reference-genomes` environment

### Calibrated ChIP-seq
- install `chip-calibrated` environment
- run a Snakemake dry-run against `tests/fixtures/chip-calibrated-basic/config.yaml`
- revalidated after DAG hardening to ensure track generation depends on explicit bigWig outputs

### Bulk RNA-seq
- install `bulk-rna` environment
- run a Snakemake dry-run against `tests/fixtures/bulk-rna-merge-aware/config.yaml`
- this fixture validates explicit `sample_name` and `merge_group` handling

## Local validation commands

### CATCH-UP
```bash
cd UpStreamPipeline
pixi run catch-up-example-dryrun
```

### Calibrated ChIP-seq
```bash
cd UpStreamPipeline
pixi install -e chip-calibrated
PIXI_CORES=4 pixi run -e chip-calibrated chip-calibrated
```

### Bulk RNA-seq
```bash
cd UpStreamPipeline
pixi install -e bulk-rna
PIXI_CORES=4 pixi run -e bulk-rna bulk-rna
```

## Current limitation

CI currently validates:
- environment solving
- workflow parsing
- DAG construction
- sample-sheet handling
- explicit metadata-driven grouping in reusable local/CI fixtures

CI does **not** yet validate:
- full end-to-end execution
- biological correctness of outputs
- track hub rendering in a browser
