"""
Annotate a sapia table with values from protein_info.json.

Appends subunit_len, contig_start, contig_end, n_chains as constant columns
to every row in the table. Run once after sapia collect rfdiffusion3.

Usage:
    sapia annotate . --table table0_l20_65 --from protein_info.json
"""

import argparse
import json
import pandas as pd
from pathlib import Path


def annotate(run_dir: Path, table: str, info_path: Path) -> None:
    info = json.loads(info_path.read_text())
    keys = ["subunit_len", "contig_start", "contig_end", "n_chains"]
    
    tsv = run_dir / f"{table}.tsv"
    df = pd.read_csv(tsv, sep="\t", index_col=0)
    
    for k in keys:
        df[k] = info[k]
    
    df.to_csv(tsv, sep="\t")
    print(f"Annotated {len(df)} rows in {tsv} with {keys}")


def build_annotate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("-t", "--table", required=True)
    parser.add_argument("--from", dest="info_path", type=Path, default=Path("protein_info.json"))
    return parser


def annotate_from_args(args: argparse.Namespace) -> None:
    annotate(run_dir=args.run_dir, table=args.table, info_path=args.info_path)
