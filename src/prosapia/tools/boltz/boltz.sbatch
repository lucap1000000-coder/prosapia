#!/bin/bash
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=04:00:00
#SBATCH --job-name=boltz
#SBATCH --partition=ampere_gpu
# #SBATCH --clusters=anansi  disabled: run on hydra

set -euo pipefail

# Shared scaffolding: sets MANIFEST/OUT_DIR/SAPIA_LINE.
source "/data/brussel/118/vsc11875/prosapia/src/prosapia/core/sbatch/sapia_task_prelude.sh"

# Site-specific activation (required) — see docs/configuration.md.
# Must put `boltz` on PATH.
set +u
source "${SAPIA_ACTIVATE_BOLTZ:?set SAPIA_ACTIVATE_BOLTZ in your .env to a tool activation script}"
set -u

# Manifest columns (tab-separated):
#   shard_dir  extra
# $EXTRA holds every run-wide `boltz predict` option (--devices, --use_msa_server,
# ...) as space-separated tokens. It is intentionally left unquoted below so each
# token becomes its own argv entry.
SHARD_DIR=$(echo "$SAPIA_LINE" | cut -f1)
EXTRA=$(echo "$SAPIA_LINE" | cut -f2)

echo "[$(date +%T)] task $SLURM_ARRAY_TASK_ID: predicting shard $SHARD_DIR ($EXTRA)"
boltz predict "$SHARD_DIR" \
    --out_dir "$OUT_DIR" \
    --cache "${CACHE:-$VSC_DATA/.boltz}" \
    --no_kernels \
    --write_full_pae \
    $EXTRA
