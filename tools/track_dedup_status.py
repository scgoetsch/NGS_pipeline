#!/usr/bin/env python3
"""Determine empirically whether each 08_bam_coverages/*.bw counts PCR duplicates.

WHY THIS IS NEEDED. The CATCH-UP pipeline marks duplicates but never filters them, so
tracks normally COUNT duplicates. WS-d3m7 (2026-07-21) regenerated the NOVX125
K4me3/K27me3/K9me3 bigwigs from physically deduplicated BAMs -- but wrote them to the same
paths under the same names. Nothing on disk distinguishes the two kinds, so a reader
cannot tell what a given bigwig means. This script decides it from the data.

THE TEST. Bigwig coverage is proportional to the reads it was built from. Across regions
whose duplicate fractions differ, ratio bw/all_reads is near-constant if the track came
from the full BAM, and bw/unique_reads is near-constant if it came from a deduplicated
one. Whichever ratio has the lower coefficient of variation identifies the source. Regions
are chosen to span a range of duplicate rates, and the call is only made when the two CVs
are clearly separated -- otherwise it reports UNCERTAIN rather than guessing.
"""
import subprocess, sys, glob, os
import numpy as np
import pyBigWig

ST = os.environ.get("TRACK_SAMTOOLS", "/home/dev/workspace/PHF7_NGS/UpStreamPipeline/.pixi/envs/bulk-rna/bin/samtools")
RES = os.environ.get("TRACK_RES_ROOT", "/home/dev/workspace/PHF7_NGS/results")
NREG, MINREADS = 14, 300


def counts(bam, reg):
    a = subprocess.run(f"{ST} view -c {bam} {reg}", shell=True, capture_output=True, text=True).stdout.strip()
    u = subprocess.run(f"{ST} view -c -F 1024 {bam} {reg}", shell=True, capture_output=True, text=True).stdout.strip()
    try:
        return int(a), int(u)
    except ValueError:
        return 0, 0


def classify(bw_path, bam_path):
    bw = pyBigWig.open(bw_path)
    chroms = {c: l for c, l in bw.chroms().items() if c.startswith("chr") and l > 5_000_000}
    if not chroms:
        bw.close(); return "NO_CHROMS", {}
    rng = np.random.default_rng(0)
    names = sorted(chroms)
    rows = []
    tries = 0
    while len(rows) < NREG and tries < 400:
        tries += 1
        c = names[rng.integers(len(names))]
        s = int(rng.integers(3_000_000, chroms[c] - 100_000))
        e = s + 50_000
        reg = f"{c}:{s}-{e}"
        a, u = counts(bam_path, reg)
        if a < MINREADS or u == 0:
            continue
        v = bw.stats(c, s, e, type="mean")[0]
        if not v:
            continue
        rows.append((v, a, u, 1 - u / a))
    bw.close()
    if len(rows) < 5:
        return "INSUFFICIENT_COVERAGE", {}
    v = np.array([r[0] for r in rows]); a = np.array([r[1] for r in rows])
    u = np.array([r[2] for r in rows]); d = np.array([r[3] for r in rows])
    cv_all = (v / a).std() / (v / a).mean()
    cv_uniq = (v / u).std() / (v / u).mean()
    info = {"n_regions": len(rows), "dup_frac_range": f"{d.min():.3f}-{d.max():.3f}",
            "cv_vs_all": round(float(cv_all), 4), "cv_vs_unique": round(float(cv_uniq), 4)}
    # Below ~5% duplication the two hypotheses differ by less than the measurement noise,
    # AND the distinction is immaterial -- deduplicating changes coverage by <5%. Say so
    # rather than reporting a false UNCERTAIN that invites a pointless investigation.
    if d.max() < 0.05:
        return "IMMATERIAL_dup_under_5pct", info
    ratio = cv_all / (cv_uniq or 1e-9)
    if ratio < 0.7:
        return "COUNTS_DUPLICATES", info
    if ratio > 1.4:
        return "DEDUPLICATED", info
    return "UNCERTAIN_needs_manual_check", info


def main():
    targets = sys.argv[1:] or sorted(glob.glob(f"{RES}/*/results/08_bam_coverages"))
    print(f"{'project':<32}{'verdict':<26}{'nreg':>5}{'dup range':>14}{'cv_all':>9}{'cv_uniq':>9}")
    out = []
    for d in targets:
        parts = d.rstrip("/").split("/"); proj = parts[-3] if len(parts) >= 3 else d
        bws = sorted(glob.glob(f"{d}/*.bw"))
        merge = os.path.join(d.replace("08_bam_coverages", "07_merge"))
        if not bws:
            print(f"{proj:<32}{'NO_BIGWIGS':<26}"); continue
        picked = None
        for b in bws:
            cand = os.path.join(merge, os.path.basename(b).replace(".bw", ".bam"))
            if os.path.exists(cand) and os.path.exists(cand + ".bai"):
                picked = (b, cand); break
        if not picked:
            print(f"{proj:<32}{'NO_MATCHED_BAM':<26}")
            out.append((proj, "NOT_DETERMINED_no_bam", {}, len(bws))); continue
        verdict, info = classify(*picked)
        print(f"{proj:<32}{verdict:<26}{info.get('n_regions',0):>5}"
              f"{info.get('dup_frac_range',''):>14}{info.get('cv_vs_all',''):>9}"
              f"{info.get('cv_vs_unique',''):>9}")
        out.append((proj, verdict, info, len(bws)))
    import json
    json.dump([{"project": p, "verdict": v, "evidence": i, "n_bigwigs": n} for p, v, i, n in out],
              open(os.environ.get("TRACK_OUT_JSON", "/tmp/dedup_status.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
