#!/bin/bash
#SBATCH --partition=<partition-name>
#SBATCH --job-name=catch-up
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --mail-user=<your-email>
#SBATCH --time=03-12:00:00
#SBATCH --output=%j_%x.out
#SBATCH --error=%j_%x.err

set -euo pipefail

# Change this to the repository root on your cluster
cd /path/to/UpStreamPipeline

# Optional: use a local Pixi cache on shared HPC systems
# export PIXI_CACHE_DIR="$PWD/.pixi-cache"

pixi run catch-up-dryrun
PIXI_CORES=${SLURM_CPUS_PER_TASK:-4} pixi run catch-up
