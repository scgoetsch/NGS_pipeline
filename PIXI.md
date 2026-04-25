# Using UpStreamPipeline with Pixi

This repository ships an `envs/upstream.yml` conda environment. For a Pixi-based workflow, use the root `pixi.toml` instead.

For broader project status and roadmap notes, see [`MODERNIZATION.md`](MODERNIZATION.md) and the files under [`docs/modernization/`](docs/modernization/).

## Why Pixi here?

Pixi can manage both Python packages and non-Python bioinformatics tools from `conda-forge` and `bioconda`, which makes it a good fit for this Snakemake-based repository.

## Environments

The Pixi project is split into smaller, per-pipeline environments:

- `default` / `catch-up` for `genetics/CATCH-UP`
- `reference-genomes`
- `build-calibration-genome`
- `ucsc-track-hub`
- `chip-calibrated`
- `bulk-rna`
- `all` if you want the broader tool stack in one solve

## Included tools

The Pixi environments cover the main tools required by the repository, including:

- Python 3.9
- Snakemake
- Bowtie2 / BWA / bwa-mem2
- samtools / sambamba / picard / bedtools
- FastQC / MultiQC
- deepTools / MACS2 / LanceOtron
- Trimmomatic
- STAR / Subread
- R plotting packages used elsewhere in the repo

## Quick start

From the repository root:

```bash
pixi install
```

Dry-run the bundled DNase example:

```bash
pixi run catch-up-example-dryrun
```

Run the bundled DNase example:

```bash
PIXI_CORES=2 pixi run catch-up-example
```

Dry-run the main CATCH-UP workflow after editing `genetics/CATCH-UP/config/analysis.yaml`:

```bash
pixi run catch-up-dryrun
```

Run the main CATCH-UP workflow:

```bash
PIXI_CORES=4 pixi run catch-up
```

## Other helper tasks

The helper workflows live in their own named environments. Install and run them like this:

```bash
pixi install -e reference-genomes
pixi run -e reference-genomes reference-genomes

pixi install -e build-calibration-genome
pixi run -e build-calibration-genome build-calibration-genome

pixi install -e ucsc-track-hub
pixi run -e ucsc-track-hub ucsc-track-hub

pixi install -e chip-calibrated
pixi run -e chip-calibrated chip-calibrated

pixi install -e bulk-rna
pixi run -e bulk-rna bulk-rna
```

## Notes

- The provided Pixi project is currently pinned to `linux-64` because this environment is the most realistic target for the repository's genomics tools and HPC usage.
- The Snakemake version is constrained to `>=7,<8` to stay close to the repository's current workflow assumptions (`min_version("7.0.0")`).
- You still need to edit each workflow's `config/analysis.yaml` before running it.
- `genetics/CATCH-UP` now supports a modern `sample_sheet` entry in the config file, while still supporting the legacy text files.

## Suggested migration path from the original conda instructions

Original:

```bash
conda env create --file=envs/upstream.yml
conda activate upstream
cd genetics/CATCH-UP
snakemake --configfile=config/analysis.yaml all --cores 4
```

Pixi:

```bash
pixi install
PIXI_CORES=4 pixi run catch-up
```
