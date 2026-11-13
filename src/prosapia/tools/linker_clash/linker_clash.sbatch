#!/bin/bash
#SBATCH --job-name=linker_clash
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

set -uo pipefail
source "/data/brussel/118/vsc11875/prosapia/src/prosapia/core/sbatch/sapia_task_prelude.sh"

set +u
source "${SAPIA_ACTIVATE_LINKER_CLASH:?set SAPIA_ACTIVATE_LINKER_CLASH in your .env to a tool activation script}"
set -u

name=$(echo "$SAPIA_LINE" | cut -f1)
src=$(echo "$SAPIA_LINE" | cut -f2)
subunit_len=$(echo "$SAPIA_LINE" | cut -f3)
mkdir -p "$OUT_DIR"

python - "$src" "$OUT_DIR/$name.json" "$subunit_len" <<'PYEOF'
import json, sys
import numpy as np
import gemmi

SLYB_LEN = int(sys.argv[3]) if len(sys.argv) > 3 else 135  # residues per subunit

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

# Load all CA coords
all_cas = get_ca_coords(sys.argv[1])
if not all_cas:
    json.dump({"min_linker_clash_dist": None}, open(sys.argv[2], "w"))
    sys.exit(0)

total = all_cas[-1][0]
linker_start = SLYB_LEN + 1       # 136
linker_end = total - SLYB_LEN     # total - 135

# Extract three regions
a_coords = np.array([xyz for resid, xyz in all_cas
                     if resid <= SLYB_LEN])
linker_coords = np.array([xyz for resid, xyz in all_cas
                           if linker_start <= resid <= linker_end])
b_coords = np.array([xyz for resid, xyz in all_cas
                     if resid > linker_end])

if any(len(x) == 0 for x in [a_coords, linker_coords, b_coords]):
    json.dump({"min_linker_clash_dist": None, "error": "empty region"}, 
              open(sys.argv[2], "w"))
    sys.exit(0)

if len(a_coords) != len(b_coords):
    json.dump({"min_linker_clash_dist": None, 
               "error": f"length mismatch: A={len(a_coords)} B={len(b_coords)}"},
              open(sys.argv[2], "w"))
    sys.exit(0)

# Superpose A region onto B region
# This gives the transform from A's frame to B's frame
# i.e. the transform that maps linker1 position to linker2 position
pos_a = [gemmi.Position(x, y, z) for x, y, z in a_coords]
pos_b = [gemmi.Position(x, y, z) for x, y, z in b_coords]

result = gemmi.superpose_positions(pos_b, pos_a)
t = result.transform

# Apply transform to linker coords to get linker 2 position
linker2_coords = []
for xyz in linker_coords:
    p = gemmi.Position(xyz[0], xyz[1], xyz[2])
    p2 = t.apply(p)
    linker2_coords.append(np.array([p2.x, p2.y, p2.z]))
linker2_coords = np.array(linker2_coords)

# Minimum CA-CA distance between linker 1 and linker 2
diffs = linker_coords[:, None, :] - linker2_coords[None, :, :]
dists = np.sqrt((diffs ** 2).sum(axis=-1))
min_dist = float(dists.min())

json.dump({
    "min_linker_clash_dist": round(min_dist, 3),
    "linker_length": len(linker_coords),
    "superpose_rmsd": round(result.rmsd, 4),
}, open(sys.argv[2], "w"))
PYEOF
