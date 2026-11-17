from pathlib import Path

from prosapia.core import Tool

from .collect_linker_clash import collect_linker_clash
from .run_linker_clash_sbatch import build_linker_clash_manifest

TOOL = Tool(
    name="linker_clash",
    action="update",
    description="Minimum CA-CA distance between the designed linker and its symmetry neighbour in the SlyB C12 ring.",
    default_sbatch=str(Path(__file__).parent / "linker_clash.sbatch"),
    default_input_column="rfdiffusion3_path",
    build_manifest_fn=build_linker_clash_manifest,
    collect_fn=collect_linker_clash,
)
