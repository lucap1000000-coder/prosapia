#!/bin/bash
#SBATCH --job-name=chainlen
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G

set -uo pipefail
source "/data/brussel/118/vsc11875/prosapia/src/prosapia/core/sbatch/sapia_task_prelude.sh"

set +u
source "${SAPIA_ACTIVATE_CHAINLEN:?set SAPIA_ACTIVATE_CHAINLEN in your .env to a tool activation script}"
set -u

name=$(echo "$SAPIA_LINE" | cut -f1)
src=$(echo "$SAPIA_LINE" | cut -f2)
mkdir -p "$OUT_DIR"

python3 - "$src" "$OUT_DIR/$name.json" << 'INNER'
import sys, gemmi, json

src = sys.argv[1]
out = sys.argv[2]

doc = gemmi.cif.read(src)
block = doc.sole_block()
loop = block.find(['_atom_site.label_seq_id',
                   '_atom_site.label_atom_id',
                   '_atom_site.is_motif_atom_with_fixed_seq'])

n_res = 0
fixed_res = 0
prev_seqid = None

for row in loop:
    if row[1] != 'CA':
        continue
    seqid = row[0]
    is_fixed = row[2] == 'True'
    if seqid != prev_seqid:
        n_res += 1
        if is_fixed:
            fixed_res += 1
        prev_seqid = seqid

linker_len = n_res - fixed_res
subunit_len = fixed_res // 2

json.dump({
    "n_res": n_res,
    "fixed_len": fixed_res,
    "linker_len": linker_len,
    "subunit_len": subunit_len
}, open(out, "w"))
INNER
