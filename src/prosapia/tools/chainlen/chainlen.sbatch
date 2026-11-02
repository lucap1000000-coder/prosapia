#!/bin/bash
#SBATCH --job-name=chainlen
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

set -uo pipefail
source "${SAPIA_PRELUDE:?}"

set +u
source "${SAPIA_ACTIVATE_CHAINLEN:?set SAPIA_ACTIVATE_CHAINLEN in your .env to a tool activation script}"
set -u

name=$(echo "$SAPIA_LINE" | cut -f1)
src=$(echo "$SAPIA_LINE" | cut -f2)
mkdir -p "$OUT_DIR"

python - "$src" "$OUT_DIR/$name.len" <<'EOF'
import sys, gemmi
model = gemmi.read_structure(sys.argv[1])[0]
n_res = sum(len(chain) for chain in model)
open(sys.argv[2], "w").write(f"{n_res}\n")
EOF
