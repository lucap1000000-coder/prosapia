#!/usr/bin/env python3
"""
Submit a SLURM array to compute minimum CA distance between the linker
and the TM helix of subunit B.

Manifest columns (tab-separated):
    name  src  subunit_len  tm_start  tm_end
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import cast

import pandas as pd

from prosapia.core import CommonArgs, ManifestCtx


class TmClashArgs(CommonArgs):
    tm_start: int | None
    tm_end: int | None


def add_tm_clash_args(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--tm-start",
        type=int,
        default=None,
        help="First TM helix residue in original numbering. Read from table if not set.",
    )
    parser.add_argument(
        "--tm-end",
        type=int,
        default=None,
        help="Last TM helix residue in original numbering. Read from table if not set.",
    )


def build_tm_clash_manifest(ctx: ManifestCtx[TmClashArgs]) -> list[tuple[str, ...]]:
    manifest_rows: list[tuple[str, ...]] = []
    for name in ctx.ready.index:
        name = cast(str, name)
        src = str(ctx.ready.at[name, ctx.args.input_column])
        subunit_len = int(ctx.ready.at[name, "subunit_len"]) if "subunit_len" in ctx.ready.columns else 135
        tm_start = ctx.args.tm_start or int(ctx.ready.at[name, "tm_start"]) if "tm_start" in ctx.ready.columns else 63
        tm_end = ctx.args.tm_end or int(ctx.ready.at[name, "tm_end"]) if "tm_end" in ctx.ready.columns else 100
        manifest_rows.append((name, src, str(subunit_len), str(tm_start), str(tm_end)))
    return manifest_rows
