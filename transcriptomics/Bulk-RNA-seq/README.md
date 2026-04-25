# RNA-Seq

### Overview
This user-friendly pipeline is built using [Snakemake](https://snakemake.readthedocs.io/en/stable/).   

It takes raw RNA-seq data in fastq format and uses the Spliced Transcripts Alignment to a Reference([STAR](https://github.com/alexdobin/STAR)) RNA-seq read mapper to align reads to a reference genome, and outputs analysed bigwigs for visualisation in the [UCSC genome browser](https://genome.ucsc.edu/index.html). 

### Preliminary requirements 

#### 1. UpStreamPipeline set-up :hammer_and_wrench:

Follow the instructions on [UpStreamPipeline](https://github.com/Genome-Function-Initiative-Oxford/UpStreamPipeline) to set up the correct environment. 

#### 2. Modify the config.yaml file :computer:

Detailed instructions are provided in the [config.yaml](./config/analysis.yaml) file for editing the necessary parameters.

This pipeline now supports two input metadata formats:

1. **Modern sample sheet** via `sample_sheet` in the config file
2. **Legacy text files**: `1_fastqfile_home_dir.txt`, `2_fastqfile_concat.txt`, `3_merge_bams.txt`

The recommended modern sample sheet is TSV or CSV with these columns:

- `fastq_prefix` (required)
- `sample_name` (preferred for explicit analysis-level grouping)
- `merge_group` (preferred for explicit merge grouping)
- legacy aliases still supported: `concat_sample`, `merge_sample`

Recommended examples:
- bundled example sample sheet: [`config/example.samples.tsv`](./config/example.samples.tsv)
- reusable dry-run fixture: [`../../tests/fixtures/bulk-rna-merge-aware/`](../../tests/fixtures/bulk-rna-merge-aware)

If `concatenate_fastq: true`, provide `sample_name` (or legacy `concat_sample`).
If `merge_bams: true`, provide `merge_group` (or legacy `merge_sample`).

Key points:
- Specify whether your FASTQ files are single- or paired-end
- Provide the genome build you want to align to
- Boolean values may be written as YAML booleans (`true` / `false`) or legacy strings (`"True"` / `"False"`)

***

### Additional info:
This pipeline will run all the analyses in the RNA-Seq snakemake folder, within the [config.yaml](./config/analysis.yaml) you can specify where to move all the final analysis files to within your directory and if you would like to delete any intermediate files.

#### Output folders:
When running the pipeline, results, QCs, and logs folders will be automatically generated with all related outputs inside the output folder specified in the config.yaml file.


***
### How to run the bulk RNA-seq pipeline
Option #1: run locally with Pixi from the repository root
```bash
pixi install -e bulk-rna
PIXI_CORES=4 pixi run -e bulk-rna bulk-rna
```

Option #1a: reusable fixture dry-run from the repository root
```bash
pixi run -e bulk-rna bash -lc 'cd transcriptomics/Bulk-RNA-seq && snakemake --configfile=../../tests/fixtures/bulk-rna-merge-aware/config.yaml -n all --cores 1'
```

Option #2: run locally with Snakemake
```bash
snakemake --configfile=config/analysis.yaml all --cores 4
```

Option #3: SLURM
Modify parameters of `submit.sh` (conda-based) or `submit.pixi.sh` (Pixi-based), then submit:
```bash
sbatch submit.pixi.sh
```
