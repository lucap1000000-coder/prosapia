from pathlib import Path
from prosapia.core import Tool
from .collect_c12_clash import collect_c12_clash
from .run_c12_clash_sbatch import build_c12_clash_manifest

TOOL = Tool(
    name="c12_clash",
    action="update",
    description="Minimum CA-CA distance between the designed linker and neighbouring C12 subunits L and C.",
    default_sbatch=str(Path(__file__).parent / "c12_clash.sbatch"),
    default_input_column="rfdiffusion3_path",
    build_manifest_fn=build_c12_clash_manifest,
    collect_fn=collect_c12_clash,
)
