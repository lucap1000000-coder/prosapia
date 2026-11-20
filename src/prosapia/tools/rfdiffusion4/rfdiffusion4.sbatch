#!/bin/bash
#SBATCH --job-name=rfdiffusion4
#SBATCH --partition=ampere_gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00

set -euo pipefail
source "/data/brussel/118/vsc11875/prosapia/src/prosapia/core/sbatch/sapia_task_prelude.sh"

set +u
source "${SAPIA_ACTIVATE_RFD4:?set SAPIA_ACTIVATE_RFD4 in your .env to a tool activation script}"
set -u

SPEC=$(echo "$SAPIA_LINE" | cut -f2)
OUT_DIR=$(echo "$SAPIA_LINE" | cut -f3)
NUM_DESIGNS=$(echo "$SAPIA_LINE" | cut -f4)
BATCH_SIZE=$(echo "$SAPIA_LINE" | cut -f5)

test -f "$SPEC" || { echo "spec not found: $SPEC"; exit 1; }
test -d "$OUT_DIR" && { echo "out_dir already exists -- refusing to reuse: $OUT_DIR"; exit 1; }

echo "[$(date +%T)] Running RFdiffusion4: $NUM_DESIGNS designs from $SPEC"

rfd4-generate \
    inputs="$SPEC" \
    num_replicates="$NUM_DESIGNS" \
    batch_size="$BATCH_SIZE" \
    ckpt_name=rfd4_proteina_flow-ema.ckpt \
    autoencoder_ckpt_path="${DATA_PATH}/ae_checkpoints/rfd4_proteina_ae-ema.ckpt" \
    out_dir="$OUT_DIR" \
    '~metrics' \
    compile_lengths=null
