#!/bin/bash
#SBATCH --job-name=c12_clash
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G

set -uo pipefail
source "/data/brussel/118/vsc11875/prosapia/src/prosapia/core/sbatch/sapia_task_prelude.sh"

set +u
source "${SAPIA_ACTIVATE_C12_CLASH:?set SAPIA_ACTIVATE_C12_CLASH in your .env to a tool activation script}"
set -u

name=$(echo "$SAPIA_LINE" | cut -f1)
src=$(echo "$SAPIA_LINE" | cut -f2)
mkdir -p "$OUT_DIR"

python - "$src" "$OUT_DIR/$name.json" <<'PYEOF'
import json, sys
import numpy as np
import gemmi

C12_PDB = "/data/brussel/118/vsc11875/SlyBprosapia/inputs/slyB_C12_boltz_relaxed_aligned.pdb"
SLYB_LEN = 135
NEIGHBOUR_CHAINS = ["L", "C"]

def get_ca_coords(pdb_path, res_range=None):
    cas = []
    with open(pdb_path) as f:
        for line in f:
            if not line.startswith("ATOM"):
                continue
            if line[12:16].strip() != "CA":
                continue
            resid = int(line[22:26].strip())
            if res_range and not (res_range[0] <= resid <= res_range[1]):
                continue
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            cas.append((resid, np.array([x, y, z])))
    return cas

def get_chain_ca(chain_name):
    coords = []
    with open(C12_PDB) as f:
        for line in f:
            if not line.startswith("ATOM"):
                continue
            if line[12:16].strip() != "CA":
                continue
            if line[21].strip() != chain_name:
                continue
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
            coords.append(np.array([x, y, z]))
    return np.array(coords)

def min_dist(coords1, coords2):
    diffs = coords1[:, None, :] - coords2[None, :, :]
    return float(np.sqrt((diffs**2).sum(axis=-1)).min())

# Load design
all_cas = get_ca_coords(sys.argv[1])
if not all_cas:
    json.dump({"min_dist_to_L": None, "min_dist_to_C": None, "min_dist_to_neighbours": None},
              open(sys.argv[2], "w"))
    sys.exit(0)

total = all_cas[-1][0]
linker_start = SLYB_LEN + 1
linker_end = total - SLYB_LEN

linker_coords = np.array([xyz for resid, xyz in all_cas
                           if linker_start <= resid <= linker_end])
b_region_coords = np.array([xyz for resid, xyz in all_cas
                             if resid > linker_end])

if len(linker_coords) == 0 or len(b_region_coords) == 0:
    json.dump({"min_dist_to_L": None, "min_dist_to_C": None, "min_dist_to_neighbours": None},
              open(sys.argv[2], "w"))
    sys.exit(0)

# Superpose design B region onto C12 chain B to get transform
c12_chainB = get_chain_ca("B")
c12_chainB_trimmed = c12_chainB[3:]  # residues 4-138

if len(b_region_coords) != len(c12_chainB_trimmed):
    json.dump({"min_dist_to_L": None, "min_dist_to_C": None,
               "min_dist_to_neighbours": None, "error": "length mismatch"},
              open(sys.argv[2], "w"))
    sys.exit(0)

pos_design = [gemmi.Position(x, y, z) for x, y, z in b_region_coords]
pos_c12b = [gemmi.Position(x, y, z) for x, y, z in c12_chainB_trimmed]
result = gemmi.superpose_positions(pos_design, pos_c12b)
t = result.transform

# Apply transform to linker coords to place in C12 frame
linker_in_c12 = []
for xyz in linker_coords:
    p = gemmi.Position(xyz[0], xyz[1], xyz[2])
    p2 = t.apply(p)
    linker_in_c12.append(np.array([p2.x, p2.y, p2.z]))
linker_in_c12 = np.array(linker_in_c12)

# Check against L and C
dist_L = min_dist(linker_in_c12, get_chain_ca("L"))
dist_C = min_dist(linker_in_c12, get_chain_ca("C"))

json.dump({
    "min_dist_to_L": round(dist_L, 3),
    "min_dist_to_C": round(dist_C, 3),
    "min_dist_to_neighbours": round(min(dist_L, dist_C), 3),
    "superpose_rmsd": round(result.rmsd, 4),
}, open(sys.argv[2], "w"))
PYEOF
