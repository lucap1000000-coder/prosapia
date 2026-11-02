from pathlib import Path

from prosapia.core import Tool

from .collect_bbcheck import collect_bbcheck
from .run_bbcheck_sbatch import build_bbcheck_manifest

TOOL = Tool(
    name="bbcheck",
    action="update",
    description="Backbone checks: largest CA-CA step and closest non-local CA-CA distance.",
    default_sbatch=str(Path(__file__).parent / "bbcheck.sbatch"),
    default_input_column="rfdiffusion3_path",
    build_manifest_fn=build_bbcheck_manifest,
    collect_fn=collect_bbcheck,
)
