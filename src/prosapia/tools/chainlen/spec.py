from pathlib import Path

from prosapia.core import Tool

from .collect_chainlen import collect_chainlen
from .run_chainlen_sbatch import build_chainlen_manifest

TOOL = Tool(
    name="chainlen",
    action="update",
    description="Number of residues in each design.",
    default_sbatch=str(Path(__file__).parent / "chainlen.sbatch"),
    default_input_column="rfdiffusion3_path",
    build_manifest_fn=build_chainlen_manifest,
    collect_fn=collect_chainlen,
)
