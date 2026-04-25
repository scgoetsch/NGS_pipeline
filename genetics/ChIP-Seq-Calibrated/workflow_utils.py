from __future__ import annotations

from pathlib import Path
import shutil
import pandas as pd


BOOL_KEYS = [
    "cutadapters_bool",
    "input_provided",
    "move_output_files",
    "move_bw_public_folder",
    "delete_intermediate_files",
    "single_paired_folder_rm",
    "reads_rm",
    "trimming_rm",
    "bowtie2_rm",
    "sorted_rm",
    "duplicates_rm",
    "splitgenome_rm",
    "readcounts_rm",
    "downsampling_factor_rm",
    "downsampling_rm",
    "bam_coverage_rm",
    "peaks_rm",
    "track_rm",
]


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
    config["sample_sheet"] = str(config.get("sample_sheet", "")).strip()
    return config


def _analysis_fastq_dir(config: dict) -> Path:
    return Path(config["analysis_name"]) / config["single_paired_folder"]


def _write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as handle:
        for line in lines:
            handle.write(f"{line}\n")


def _prepare_legacy_inputs(config: dict, workflow_dir: Path):
    analysis_fastq_dir = _analysis_fastq_dir(config)
    analysis_fastq_dir.mkdir(parents=True, exist_ok=True)

    legacy_path = workflow_dir / "fastqfile_home_dir.txt"
    df = pd.read_csv(legacy_path, header=None, sep="\t")

    if config["input_provided"]:
        if df.shape[1] < 2:
            raise ValueError(
                "Legacy fastqfile_home_dir.txt must contain at least 2 tab-separated columns when input_provided is true"
            )
        chip_prefixes = df[0].astype(str).str.strip().tolist()
        input_prefixes = df[1].astype(str).str.strip().tolist()
    else:
        chip_prefixes = df[0].astype(str).str.strip().tolist()
        input_prefixes = []

    if config["single_paired_end"] == "paired":
        fastq_entries = []
        for prefix in chip_prefixes + input_prefixes:
            fastq_entries.extend([f"{prefix}_R1.fastq.gz", f"{prefix}_R2.fastq.gz"])
    else:
        fastq_entries = [f"{prefix}.fastq.gz" for prefix in chip_prefixes + input_prefixes]

    _write_lines(analysis_fastq_dir / "fastqfile_home_dir.txt", fastq_entries)

    pairing_path = analysis_fastq_dir / "samples_pairing.csv"
    with pairing_path.open("w") as handle:
        if config["input_provided"]:
            for chip, inp in zip(chip_prefixes, input_prefixes):
                handle.write(f"{inp}\t{chip}\n")
                handle.write(f"{chip}\t{chip}\n")
        else:
            for chip in chip_prefixes:
                handle.write(f"{chip}\t{chip}\n")


def _prepare_sample_sheet_inputs(config: dict, workflow_dir: Path):
    analysis_fastq_dir = _analysis_fastq_dir(config)
    analysis_fastq_dir.mkdir(parents=True, exist_ok=True)

    sample_sheet_path = Path(config["sample_sheet"])
    if not sample_sheet_path.is_absolute():
        sample_sheet_path = workflow_dir / sample_sheet_path
    if not sample_sheet_path.exists():
        raise FileNotFoundError(f"Sample sheet not found: {sample_sheet_path}")

    if sample_sheet_path.suffix.lower() == ".csv":
        df = pd.read_csv(sample_sheet_path)
    else:
        df = pd.read_csv(sample_sheet_path, sep="\t")

    df.columns = [str(c).strip() for c in df.columns]
    required = {"chip_fastq_prefix"}
    if config["input_provided"]:
        required.add("input_fastq_prefix")
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Sample sheet is missing required column(s): {', '.join(sorted(missing))}"
        )

    for column in df.columns:
        df[column] = df[column].fillna("").astype(str).str.strip()

    if (df["chip_fastq_prefix"] == "").any():
        raise ValueError("Sample sheet column 'chip_fastq_prefix' cannot contain empty values")
    if config["input_provided"] and (df["input_fastq_prefix"] == "").any():
        raise ValueError("Sample sheet column 'input_fastq_prefix' cannot contain empty values when input_provided is true")

    shutil.copy(sample_sheet_path, analysis_fastq_dir / sample_sheet_path.name)

    chip_prefixes = df["chip_fastq_prefix"].tolist()
    input_prefixes = df["input_fastq_prefix"].tolist() if config["input_provided"] else []

    if config["single_paired_end"] == "paired":
        fastq_entries = []
        for prefix in chip_prefixes + input_prefixes:
            fastq_entries.extend([f"{prefix}_R1.fastq.gz", f"{prefix}_R2.fastq.gz"])
    else:
        fastq_entries = [f"{prefix}.fastq.gz" for prefix in chip_prefixes + input_prefixes]

    _write_lines(analysis_fastq_dir / "fastqfile_home_dir.txt", fastq_entries)

    pairing_path = analysis_fastq_dir / "samples_pairing.csv"
    with pairing_path.open("w") as handle:
        if config["input_provided"]:
            for chip, inp in zip(chip_prefixes, input_prefixes):
                handle.write(f"{inp}\t{chip}\n")
                handle.write(f"{chip}\t{chip}\n")
        else:
            for chip in chip_prefixes:
                handle.write(f"{chip}\t{chip}\n")


def prepare_workflow_inputs(config: dict, workflow_dir: str | Path = ".") -> dict:
    workflow_dir = Path(workflow_dir)
    if config["sample_sheet"]:
        _prepare_sample_sheet_inputs(config, workflow_dir)
    else:
        _prepare_legacy_inputs(config, workflow_dir)

    fastqfile_path = _analysis_fastq_dir(config) / "fastqfile_home_dir.txt"
    origin_fastq_raw = pd.read_csv(fastqfile_path, header=None)[0]
    origin_fastq = [of.split(".fastq.gz")[0] for of in list(origin_fastq_raw)]

    samples_r = origin_fastq.copy()
    if config["single_paired_end"] == "paired":
        samples_r = list(dict.fromkeys([s.rsplit("_R", 1)[0] for s in samples_r]))

    return {
        "origin_fastq": origin_fastq,
        "samples_r": samples_r,
    }
