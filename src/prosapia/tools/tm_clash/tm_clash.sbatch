#!/bin/bash
#SBATCH --job-name=tm_clash
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

set -uo pipefail
source "/data/brussel/118/vsc11875/prosapia/src/prosapia/core/sbatch/sapia_task_prelude.sh"

set +u
source "${SAPIA_ACTIVATE_TM_CLASH:?set SAPIA_ACTIVATE_TM_CLASH in your .env to a tool activation script}"
set -u

name=$(echo "$SAPIA_LINE" | cut -f1)
src=$(echo "$SAPIA_LINE" | cut -f2)
subunit_len=$(echo "$SAPIA_LINE" | cut -f3)
tm_start=$(echo "$SAPIA_LINE" | cut -f4)
tm_end=$(echo "$SAPIA_LINE" | cut -f5)
mkdir -p "$OUT_DIR"

python - "$src" "$OUT_DIR/$name.json" "$subunit_len" "$tm_start" "$tm_end" <<'PYEOF'
import json, sys
import numpy as np
import gemmi

src = sys.argv[1]
out = sys.argv[2]
subunit_len = int(sys.argv[3])
tm_start = int(sys.argv[4])
tm_end = int(sys.argv[5])

st = gemmi.read_structure(src)
chain = st[0][st[0].sole_residue("CA").chain_name] if False else list(st[0])[0]
residues = [r for r in chain if r.find_atom("CA", "*")]

if len(residues) < 2 * subunit_len:
    json.dump({"tm_clash_min": None, "error": "too short"}, open(out, "w"))
    sys.exit(0)

# Linker residues: between position subunit_len and len-subunit_len
linker_res = residues[subunit_len:len(residues)-subunit_len]

# TM residues in subunit B: position subunit_len + (tm_start - contig_start) to subunit_len + (tm_end - contig_start)
# In absolute residue numbering, subunit B starts at subunit_len+1
# TM helix in B: offset by subunit_len from original numbering
b_offset = subunit_len
tm_b_res = [r for r in residues if b_offset + tm_start <= residues.index(r) + 1 <= b_offset + tm_end]

if not linker_res or not tm_b_res:
    json.dump({"tm_clash_min": None, "error": "empty region"}, open(out, "w"))
    sys.exit(0)

linker_cas = [r.find_atom("CA", "*").pos for r in linker_res]
tm_cas = [r.find_atom("CA", "*").pos for r in tm_b_res]

min_dist = min(
    linker_ca.dist(tm_ca)
    for linker_ca in linker_cas
    for tm_ca in tm_cas
)

json.dump({
    "tm_clash_min": round(min_dist, 3),
    "linker_length": len(linker_res),
    "tm_residues_checked": len(tm_b_res),
}, open(out, "w"))
PYEOF
