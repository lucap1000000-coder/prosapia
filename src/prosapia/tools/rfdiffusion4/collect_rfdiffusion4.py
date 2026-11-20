#!/usr/bin/env python3
"""
Collect RFdiffusion4 outputs into a child table.

rfd4-generate writes:
  <out_dir>/inference_samples/<example_id>/<example_id>_generated.cif
  <out_dir>/inference_metrics/per_example_metrics.csv

Each design gets one row with:
  rfdiffusion4_path      path to the generated CIF
  rfdiffusion4_sequence  designed sequence (chain A only, linker included)
  rfdiffusion4_linker_len  length of linker region

Usage:
    sapia collect rfdiffusion4 . --table table0_rfd4
"""

from pathlib import Path

import json
import gemmi
import pandas as pd

from prosapia.core import CollectArgs, CollectCtx, CollectEach, Collected


def collect_rfdiffusion4(ctx: CollectCtx) -> CollectEach:
    out_dir = ctx.out_dir
    metrics_csv = out_dir / "inference_metrics" / "per_example_metrics.csv"

    if not metrics_csv.exists():
        raise FileNotFoundError(f"No per_example_metrics.csv found in {out_dir}")

    metrics = pd.read_csv(metrics_csv)
    # Read subunit_len from protein_info.json if available
    info_path = ctx.args.run_dir / "protein_info.json"
    subunit_len = None
    if info_path.exists():
        info = json.loads(info_path.read_text())
        subunit_len = info.get("subunit_len")

    for _, row in metrics.iterrows():
        example_id = row["example_id"]
        cif_path = Path(row["designed_structure_path"])

        if not cif_path.exists():
            yield Collected(
                name=example_id,
                status="missing",
                data={"rfdiffusion4_path": pd.NA,
                      "rfdiffusion4_sequence": pd.NA,
                      "rfdiffusion4_linker_len": pd.NA},
            )
            continue

        try:
            st = gemmi.read_structure(str(cif_path))
            chain_a = st[0]["A"]
            residues = [r for r in chain_a if r.find_atom("CA", "*")]
            seq = gemmi.one_letter_code([r.name for r in residues])
            linker_len = len(residues) - 2 * subunit_len if subunit_len else pd.NA

            yield Collected(
                name=example_id,
                status="OK",
                data={
                    "rfdiffusion4_path": str(cif_path),
                    "rfdiffusion4_sequence": seq,
                    "rfdiffusion4_linker_len": linker_len,
                    "parent_name": example_id,
                },
            )
        except Exception as e:
            yield Collected(
                name=example_id,
                status=f"error: {e}",
                data={"rfdiffusion4_path": pd.NA,
                      "rfdiffusion4_sequence": pd.NA,
                      "rfdiffusion4_linker_len": pd.NA},
            )
