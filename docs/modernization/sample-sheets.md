# Sample-sheet formats

This document summarizes the current modern sample-sheet formats.

## CATCH-UP

Config key:

```yaml
sample_sheet: "path/to/samples.tsv"
```

Supported columns:
- `fastq_prefix` required
- `sample_name` preferred for explicit analysis-level grouping
- `merge_group` preferred for explicit merge grouping
- legacy aliases still supported: `concat_sample`, `merge_sample`

If `concatenate_fastq: true`, provide `sample_name` (or legacy `concat_sample`).
If `merge_bams: true`, provide `merge_group` (or legacy `merge_sample`).

Example:

```tsv
fastq_prefix	sample_name	merge_group
sample1_lane1	sample1	sample_group1
sample1_lane2	sample1	sample_group1
sample2_lane1	sample2	sample_group2
```

Reusable dry-run fixture:
- `tests/fixtures/catch-up-merge-aware/`

## Calibrated ChIP-seq

Config key:

```yaml
sample_sheet: "path/to/samples.tsv"
```

Supported columns:
- `chip_fastq_prefix` required
- `input_fastq_prefix` required when `input_provided: true`

Example:

```tsv
chip_fastq_prefix	input_fastq_prefix
chip_rep1	input_rep1
chip_rep2	input_rep2
```

Reusable dry-run fixture:
- `tests/fixtures/chip-calibrated-basic/`

## Bulk RNA-seq

Config key:

```yaml
sample_sheet: "path/to/samples.tsv"
```

Supported columns:
- `fastq_prefix` required
- `sample_name` preferred for explicit analysis-level grouping
- `merge_group` preferred for explicit merge grouping
- legacy aliases still supported: `concat_sample`, `merge_sample`

If `concatenate_fastq: true`, provide `sample_name` (or legacy `concat_sample`).
If `merge_bams: true`, provide `merge_group` (or legacy `merge_sample`).

Example:

```tsv
fastq_prefix	sample_name	merge_group
rna_rep1_lane1	rna_rep1	rna_group1
rna_rep1_lane2	rna_rep1	rna_group1
```

Reusable dry-run fixture:
- `tests/fixtures/bulk-rna-merge-aware/`

## Legacy compatibility

All three modernized pipelines still support their original text-file inputs.
Use sample sheets for new analyses; keep legacy files only for backward compatibility.
