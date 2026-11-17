#!/bin/bash
#SBATCH --job-name=bbcheck
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

set -uo pipefail
source "/data/brussel/118/vsc11875/prosapia/src/prosapia/core/sbatch/sapia_task_prelude.sh"

set +u
source "${SAPIA_ACTIVATE_BBCHECK:?set SAPIA_ACTIVATE_BBCHECK in your .env to a tool activation script}"
set -u

name=$(echo "$SAPIA_LINE" | cut -f1)
src=$(echo "$SAPIA_LINE" | cut -f2)
mkdir -p "$OUT_DIR"

python - "$src" "$OUT_DIR/$name.json" <<'EOF'
import json, sys
import numpy as np
import gemmi

MIN_SEP = 3  # ignore residue pairs closer than this in sequence

model = gemmi.read_structure(sys.argv[1])[0]
coords, chain_ids, res_idx = [], [], []
max_step = 0.0
for c, chain in enumerate(model):
    prev = None
    for i, res in enumerate(chain):
        atom = res.find_atom("CA", "*")
        if atom is None:
            continue
        xyz = np.array([atom.pos.x, atom.pos.y, atom.pos.z])
        if prev is not None:
            max_step = max(max_step, float(np.linalg.norm(xyz - prev)))
        prev = xyz
        coords.append(xyz)
        chain_ids.append(c)
        res_idx.append(i)

coords = np.array(coords)
chain_ids = np.array(chain_ids)
res_idx = np.array(res_idx)
dist = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=2)
comparable = (chain_ids[:, None] != chain_ids[None, :]) | (
    np.abs(res_idx[:, None] - res_idx[None, :]) >= MIN_SEP
)
min_dist = float(dist[comparable].min())

out = {"max_ca_step": round(max_step, 3), "min_ca_dist": round(min_dist, 3)}
json.dump(out, open(sys.argv[2], "w"))
EOF
