from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prosapia.core import CollectCtx

NA = float("nan")


def collect_tm_clash(ctx: CollectCtx):
    out_dir = ctx.out_dir
    for name in ctx.df.index:
        result_path = out_dir / f"{name}.json"
        if not result_path.exists():
            yield ctx.missing(name)
            continue
        try:
            data = json.loads(result_path.read_text())
            yield ctx.ok(name, {
                "tm_clash_min": data.get("tm_clash_min", NA),
                "tm_clash_linker_len": data.get("linker_length", NA),
            })
        except Exception as e:
            yield ctx.error(name, str(e))
