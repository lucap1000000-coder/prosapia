#!/usr/bin/env python3
"""
Submit an RFdiffusion4 generation job.

Unlike rfd3 (one task per design), rfd4 runs all designs in one job.
The manifest has a single row: the spec yaml path and the output directory.

Usage:
    sapia run rfdiffusion4 . --spec specs_rfd4/l20_65_hot1.yaml --num-designs 400
"""

from argparse import ArgumentParser
from pathlib import Path

from prosapia.core import CommonArgs, ManifestCtx


class RFdiffusion4Args(CommonArgs):
    spec: str
    num_designs: int
    batch_size: int
    subunit_len: int | None


def add_rfdiffusion4_args(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--spec",
        type=str,
        required=True,
        help="Path to the rfd4 YAML condition spec.",
    )
    parser.add_argument(
        "--num-designs",
        type=int,
        default=400,
        help="Number of designs to generate (num_replicates). Default: 400.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for generation. Default: 8.",
    )
    parser.add_argument(
        "--subunit-len",
        type=int,
        default=None,
        help="Subunit length for linker extraction during collect. Read from protein_info.json if not set.",
    )


def build_rfdiffusion4_manifest(ctx: ManifestCtx[RFdiffusion4Args]) -> list[tuple[str, ...]]:
    spec = str(Path(ctx.args.spec).resolve())
    out_dir = str(ctx.out_dir.resolve())
    num_designs = ctx.args.num_designs
    batch_size = ctx.args.batch_size
    return [("rfd4", spec, out_dir, str(num_designs), str(batch_size))]
