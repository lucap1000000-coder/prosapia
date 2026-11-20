from pathlib import Path

from prosapia.core import Tool

from .collect_tm_clash import collect_tm_clash
from .run_tm_clash_sbatch import build_tm_clash_manifest

TOOL = Tool(
    name="tm_clash",
    action="update",
    description="Minimum CA-CA distance between the designed linker and the TM helix residues of subunit B.",
    default_sbatch=str(Path(__file__).parent / "tm_clash.sbatch"),
    default_input_column="rfdiffusion3_path",
    build_manifest_fn=build_tm_clash_manifest,
    collect_fn=collect_tm_clash,
)
