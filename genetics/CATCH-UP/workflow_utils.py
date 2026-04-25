from __future__ import annotations

from pathlib import Path
import shutil
import pandas as pd


BOOL_KEYS = [
    "concatenate_fastq",
    "cutadapters_bool",
    "merge_bams",
    "move_output_files",
    "move_bw_public_folder",
    "delete_intermediate_files",
    "single_paired_folder_rm",
    "reads_rm",
    "trimming_rm",
    "aligner_rm",
    "filtering_rm",
    "sorted_rm",
    "duplicates_rm",
    "merge_rm",
    "bam_coverage_rm",
    "peaks_rm",
    "track_rm",
]

REQUIRED_SAMPLE_SHEET_COLUMNS = {"fastq_prefix"}
OPTIONAL_SAMPLE_SHEET_COLUMNS = {"sample_name", "concat_sample", "merge_group", "merge_sample"}


def normalize_bool(value, key: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "false"}:
            return normalized == "true"
    raise ValueError(
        f"config['{key}'] must be a boolean or one of: True/False/true/false"
    )


def normalize_config(config: dict) -> dict:
    config = dict(config)
    for key in BOOL_KEYS:
        config[key] = normalize_bool(config[key], key)

    config["single_paired_end"] = str(config["single_paired_end"]).strip().lower()
    config["aligner_algorithm"] = str(config["aligner_algorithm"]).strip().lower()
    config["peak_caller"] = str(config["peak_caller"]).strip().lower()
    config["sample_sheet"] = str(config.get("sample_sheet", "")).strip()
    return config


def _analysis_fastq_dir(config: dict) -> Path:
    return Path(config["analysis_name"]) / config["single_paired_folder"]


def _strip_fastq_suffix(name: str) -> str:
    return str(name).strip().replace(".fastq.gz", "")


def _write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for line in lines:
            handle.write(f"{line}\n")


def _build_samples_df(sample_names: list[str], single_paired_end: str, path: Path) -> pd.DataFrame:
    with path.open("w") as handle:
        if single_paired_end == "paired":
            handle.write("sample\tr1\tr2\n")
            for sample in sample_names:
                handle.write(f"{sample}\t{sample}_R1.fastq.gz\t{sample}_R2.fastq.gz\n")
        else:
            handle.write("sample\tr\n")
            for sample in sample_names:
                handle.write(f"{sample}\t{sample}.fastq.gz\n")
    return pd.read_csv(path, index_col="sample", sep="\t")


def _read_level_names(prefixes: list[str], single_paired_end: str) -> list[str]:
    if single_paired_end == "paired":
        return [f"{prefix}_R1" for prefix in prefixes] + [f"{prefix}_R2" for prefix in prefixes]
    return prefixes


def _load_legacy_sample_inputs(config: dict, workflow_dir: Path):
    analysis_fastq_dir = _analysis_fastq_dir(config)
    analysis_fastq_dir.mkdir(parents=True, exist_ok=True)

    raw_fastq_list = workflow_dir / "1_fastqfile_home_dir.txt"
    concat_list = workflow_dir / "2_fastqfile_concat.txt"
    merge_list = workflow_dir / "3_merge_bams.txt"

    raw_prefixes = pd.read_csv(raw_fastq_list, header=None)[0].astype(str).str.strip().tolist()

    if config["single_paired_end"] == "paired":
        fastq_entries = [f"{prefix}_R1.fastq.gz" for prefix in raw_prefixes] + [f"{prefix}_R2.fastq.gz" for prefix in raw_prefixes]
    else:
        fastq_entries = [f"{prefix}.fastq.gz" for prefix in raw_prefixes]
    _write_lines(analysis_fastq_dir / "1_fastqfile_home_dir.txt", sorted(fastq_entries))
    origin_fastq = [_strip_fastq_suffix(item) for item in sorted(fastq_entries)]

    if config["concatenate_fastq"]:
        concat_prefixes = pd.read_csv(concat_list, header=None)[0].astype(str).str.strip().tolist()
        if config["single_paired_end"] == "paired":
            concat_entries = [f"{prefix}_R1.fastq.gz" for prefix in concat_prefixes] + [f"{prefix}_R2.fastq.gz" for prefix in concat_prefixes]
        else:
            concat_entries = [f"{prefix}.fastq.gz" for prefix in concat_prefixes]
        _write_lines(analysis_fastq_dir / "2_fastqfile_concat.txt", sorted(concat_entries))
        origin_fastq_concat = [_strip_fastq_suffix(item) for item in sorted(concat_entries)]
        sample_names = concat_prefixes
        concat_map = {sample: [sample] for sample in sample_names}
    else:
        origin_fastq_concat = origin_fastq
        sample_names = raw_prefixes
        concat_map = {sample: [sample] for sample in sample_names}

    samples_r = _build_samples_df(sample_names, config["single_paired_end"], analysis_fastq_dir / "samples.csv")

    if config["merge_bams"]:
        shutil.copy(merge_list, analysis_fastq_dir / "3_merge_bams.txt")
        merge_sample = pd.read_csv(merge_list, header=None)[0].astype(str).str.strip().tolist()
    else:
        merge_sample = list(samples_r.index)

    merge_map = {group: [group] for group in merge_sample}
    return origin_fastq, origin_fastq_concat, samples_r, merge_sample, concat_map, merge_map


def _load_sample_sheet(config: dict, workflow_dir: Path):
    sample_sheet_path = Path(config["sample_sheet"])
    if not sample_sheet_path.is_absolute():
        sample_sheet_path = workflow_dir / sample_sheet_path
    if not sample_sheet_path.exists():
        raise FileNotFoundError(f"Sample sheet not found: {sample_sheet_path}")

    df = pd.read_csv(sample_sheet_path) if sample_sheet_path.suffix.lower() == ".csv" else pd.read_csv(sample_sheet_path, sep="\t")
    df.columns = [str(c).strip() for c in df.columns]

    missing = REQUIRED_SAMPLE_SHEET_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Sample sheet is missing required column(s): {', '.join(sorted(missing))}"
        )

    unexpected = set(df.columns) - REQUIRED_SAMPLE_SHEET_COLUMNS - OPTIONAL_SAMPLE_SHEET_COLUMNS
    if unexpected:
        raise ValueError(
            "Sample sheet contains unsupported column(s): "
            + ", ".join(sorted(unexpected))
            + ". Allowed columns: fastq_prefix, sample_name, concat_sample, merge_group, merge_sample"
        )

    for column in df.columns:
        df[column] = df[column].fillna("").astype(str).str.strip()

    if (df["fastq_prefix"] == "").any():
        raise ValueError("Sample sheet column 'fastq_prefix' cannot contain empty values")

    analysis_fastq_dir = _analysis_fastq_dir(config)
    analysis_fastq_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(sample_sheet_path, analysis_fastq_dir / sample_sheet_path.name)

    raw_prefixes = df["fastq_prefix"].drop_duplicates().tolist()

    if "sample_name" not in df.columns or (df["sample_name"] == "").all():
        if "concat_sample" in df.columns and not (df["concat_sample"] == "").all():
            df["sample_name"] = df["concat_sample"]
        else:
            df["sample_name"] = df["fastq_prefix"]

    if config["concatenate_fastq"] and (df["sample_name"] == "").any():
        raise ValueError("Sample sheet column 'sample_name' cannot contain empty values when concatenate_fastq is true")

    sample_names = df["sample_name"].drop_duplicates().tolist() if config["concatenate_fastq"] else raw_prefixes

    if config["single_paired_end"] == "paired":
        fastq_entries = [f"{prefix}_R1.fastq.gz" for prefix in raw_prefixes] + [f"{prefix}_R2.fastq.gz" for prefix in raw_prefixes]
    else:
        fastq_entries = [f"{prefix}.fastq.gz" for prefix in raw_prefixes]
    _write_lines(analysis_fastq_dir / "1_fastqfile_home_dir.txt", sorted(fastq_entries))
    origin_fastq = [_strip_fastq_suffix(item) for item in sorted(fastq_entries)]

    if config["concatenate_fastq"]:
        concat_map = {
            sample_name: group["fastq_prefix"].drop_duplicates().tolist()
            for sample_name, group in df.groupby("sample_name", sort=False)
        }
        if config["single_paired_end"] == "paired":
            concat_entries = [f"{sample}_R1.fastq.gz" for sample in sample_names] + [f"{sample}_R2.fastq.gz" for sample in sample_names]
        else:
            concat_entries = [f"{sample}.fastq.gz" for sample in sample_names]
        concat_entries = sorted(set(concat_entries))
        _write_lines(analysis_fastq_dir / "2_fastqfile_concat.txt", concat_entries)
        origin_fastq_concat = [_strip_fastq_suffix(item) for item in concat_entries]
    else:
        concat_map = {sample: [sample] for sample in sample_names}
        origin_fastq_concat = origin_fastq

    merge_column = "merge_group" if "merge_group" in df.columns else "merge_sample"
    if config["merge_bams"]:
        if merge_column not in df.columns:
            raise ValueError(
                "When merge_bams is true, the sample sheet must contain 'merge_group' or legacy 'merge_sample'"
            )
        if (df[merge_column] == "").any():
            raise ValueError(f"Sample sheet column '{merge_column}' cannot contain empty values when merge_bams is true")
        merge_sample = df[merge_column].drop_duplicates().tolist()
        merge_map = {
            merge_group: group["sample_name"].drop_duplicates().tolist()
            for merge_group, group in df.groupby(merge_column, sort=False)
        }
        _write_lines(analysis_fastq_dir / "3_merge_bams.txt", merge_sample)
    else:
        merge_sample = sample_names
        merge_map = {sample: [sample] for sample in sample_names}

    samples_r = _build_samples_df(sample_names, config["single_paired_end"], analysis_fastq_dir / "samples.csv")
    return origin_fastq, origin_fastq_concat, samples_r, merge_sample, concat_map, merge_map


def prepare_workflow_inputs(config: dict, workflow_dir: str | Path = ".") -> dict:
    workflow_dir = Path(workflow_dir)
    if config["sample_sheet"]:
        origin_fastq, origin_fastq_concat, samples_r, merge_sample, concat_map, merge_map = _load_sample_sheet(config, workflow_dir)
    else:
        origin_fastq, origin_fastq_concat, samples_r, merge_sample, concat_map, merge_map = _load_legacy_sample_inputs(config, workflow_dir)

    return {
        "origin_fastq": origin_fastq,
        "origin_fastq_concat": origin_fastq_concat,
        "samples_r": samples_r,
        "merge_sample": merge_sample,
        "concat_map": concat_map,
        "merge_map": merge_map,
    }
