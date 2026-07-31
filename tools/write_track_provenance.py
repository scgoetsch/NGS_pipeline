#!/usr/bin/env python3
"""Write a TRACK_PROVENANCE.tsv into every 08_bam_coverages/ directory (WS-8drn step 1).

THE PROBLEM THIS SOLVES. The CATCH-UP pipeline marks PCR duplicates but never filters
them, so its coverage tracks COUNT duplicates. WS-d3m7 (2026-07-21) regenerated the
NOVX125 K4me3/K27me3/K9me3 bigwigs from physically deduplicated BAMs and wrote them back
to the SAME paths under the SAME names. The repo therefore holds both kinds of track,
indistinguishable from the filename, and a cross-project comparison can silently mix them.

BASIS IS RECORDED, NOT JUST THE VERDICT. Three tiers, because they are not equally strong:
  documented       - a dated regeneration with the pre-dedup originals preserved
  empirical        - track_dedup_status.py discriminated it from the data
  pipeline-default - inferred from config with no per-directory confirmation
The empirical test is UNDERPOWERED and must not be over-trusted: run as a positive control
against the three known-deduplicated NOVX directories it recovered only h3k9me3, and leaned
the wrong way on h3k27me3. Its power depends on the SPREAD of duplicate rates across
sampled regions, not their level. That is why 'documented' outranks it here.
"""
import os, glob, sys, datetime

STAMP = "2026-07-31"
BEAD = "WS-8drn"

DEDUP_CMD = "samtools view -b -F 1028 <bam> | bamCoverage -bs 10 --normalizeUsing CPM --extendReads"
DEFAULT_CMD = "bamCoverage -b <bam> -bs 1 --normalizeUsing RPKM --extendReads   (no --ignoreDuplicates)"

# empirically discriminated as counting duplicates (track_dedup_status.py)
EMPIRICAL_COUNTS = {"chip_phf7_mm10", "ttf_gata4_chip_mm10", "ttf_h3k4me3_chip_mm10", "ttf_phf7_chip_mm10"}
# duplicate rate under 5% -> the distinction is immaterial either way
IMMATERIAL = {"atac_mock_phf7_day2_mm10", "atac_phf7_mm10", "chip_cardiac_mm10", "mef_h3k9me3_mm10"}
# regenerated deduplicated, originals preserved (WS-d3m7)
DEDUPED = {"mef_chip_071526_h3k4me3_mm10", "mef_chip_071526_h3k27me3_mm10", "mef_chip_071526_h3k9me3_mm10"}

HEADER = [
    "# TRACK_PROVENANCE — do the bigwigs in this directory count PCR duplicates?",
    f"# Written {STAMP} by UpStreamPipeline/tools/write_track_provenance.py ({BEAD}).",
    "# Regenerate with that script; do not hand-edit.",
    "#",
    "# WHY: CATCH-UP marks duplicates (picard --REMOVE_DUPLICATES False, which is picard's",
    "# own default) but no consumer ever filters on the mark — bamCoverage runs without",
    "# --ignoreDuplicates, MACS uses its --keep-dup default, csaw readParam() did not set",
    "# dedup=TRUE. So tracks count duplicates unless a directory was deliberately rebuilt.",
    "#",
    "# 'duplicates counted' is NOT by itself evidence a result is inflated. Judge a library",
    "# by STACK HEIGHT and TOP-10 START-POSITION SHARE, not duplicate percentage: at high",
    "# coverage most flagged duplicates are independent fragments sharing a start base.",
    "# Worked example: memory d2-k27ac-malat1-neat1-domain-and-duplicate-diagnosis.",
    "#",
    "# DO NOT 'fix' a track with bamCoverage --ignoreDuplicates --normalizeUsing CPM:",
    "# deeptools 3.5.6 deduplicates the coverage but normalises to the full",
    "# duplicate-inclusive total, deflating the track by its unique fraction.",
    "# Physical removal (-F 1028) then bamCoverage is correct.",
    "#",
    "field\tvalue",
]


def rows(proj):
    if proj in DEDUPED:
        return [("dedup_status", "DEDUPLICATED"),
                ("basis", "documented"),
                ("evidence", "WS-d3m7 2026-07-21 regeneration; pre-dedup originals preserved at "
                             "nucleus:/project/InternalMedicine/Bann_lab/sgoets/mef_chip_071526/"
                             "deposition_prestate/08_bw_withdups/; bigwig mtimes 2026-07-21"),
                ("build_command", DEDUP_CMD),
                ("caveat", "h3k9me3 additionally confirmed empirically; h3k4me3/h3k27me3 rest on the "
                           "documented regeneration because the empirical test is underpowered at "
                           "their duplicate-rate spread")]
    if proj in IMMATERIAL:
        return [("dedup_status", "COUNTS_DUPLICATES"),
                ("basis", "pipeline-default"),
                ("evidence", "CATCH-UP config analysis.yaml mark_duplicates_extra "
                             "'--REMOVE_DUPLICATES False' + bamCoverage without --ignoreDuplicates"),
                ("build_command", DEFAULT_CMD),
                ("caveat", "measured duplicate rate <5% in sampled regions, so deduplicating would "
                           "change coverage by <5% — the distinction is immaterial here")]
    if proj in EMPIRICAL_COUNTS:
        return [("dedup_status", "COUNTS_DUPLICATES"),
                ("basis", "empirical"),
                ("evidence", "track_dedup_status.py discriminated bw/all_reads as the stable ratio "
                             "across regions spanning a wide duplicate-rate range"),
                ("build_command", DEFAULT_CMD),
                ("caveat", "")]
    return [("dedup_status", "COUNTS_DUPLICATES"),
            ("basis", "pipeline-default"),
            ("evidence", "CATCH-UP config analysis.yaml mark_duplicates_extra "
                         "'--REMOVE_DUPLICATES False' + bamCoverage without --ignoreDuplicates; "
                         "no regeneration recorded for this directory"),
            ("build_command", DEFAULT_CMD),
            ("caveat", "NOT individually confirmed — the empirical test was underpowered here. "
                       "Treat as the pipeline default, and re-derive before it becomes load-bearing.")]


def main():
    dirs = sys.argv[1:] or sorted(glob.glob("/home/dev/workspace/PHF7_NGS/results/*/results/08_bam_coverages"))
    for d in dirs:
        parts = d.rstrip("/").split("/")
        proj = parts[-3]
        nbw = len(glob.glob(f"{d}/*.bw"))
        body = [("project", proj), ("n_bigwigs", str(nbw))] + rows(proj) + [
            ("bead", BEAD), ("written", STAMP)]
        with open(os.path.join(d, "TRACK_PROVENANCE.tsv"), "w") as fh:
            fh.write("\n".join(HEADER) + "\n")
            for k, v in body:
                fh.write(f"{k}\t{v}\n")
        print(f"{proj:<34} {dict(body)['dedup_status']:<20} basis={dict(body)['basis']:<17} n={nbw}")


if __name__ == "__main__":
    main()
