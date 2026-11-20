from pathlib import Path

from prosapia.core import Tool

from .collect_rfdiffusion4 import collect_rfdiffusion4
from .run_rfdiffusion4_sbatch import add_rfdiffusion4_args, build_rfdiffusion4_manifest

TOOL = Tool(
    name="rfdiffusion4",
    action="new",
    description="Run RFdiffusion4 sequence-structure co-design for linker design.",
    default_sbatch=str(Path(__file__).parent / "rfdiffusion4.sbatch"),
    default_input_column="rfdiffusion4_path",
    add_run_args_fn=add_rfdiffusion4_args,
    build_manifest_fn=build_rfdiffusion4_manifest,
    collect_fn=collect_rfdiffusion4,
)
