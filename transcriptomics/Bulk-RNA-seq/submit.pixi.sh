#!/bin/bash
#SBATCH --partition=<partition-name>
#SBATCH --job-name=bulk-rna
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --mail-user=<your-email>
#SBATCH --time=03-12:00:00
#SBATCH --output=%j_%x.out
#SBATCH --error=%j_%x.err

set -euo pipefail

cd /path/to/UpStreamPipeline
PIXI_CORES=${SLURM_CPUS_PER_TASK:-4} pixi run -e bulk-rna bulk-rna
