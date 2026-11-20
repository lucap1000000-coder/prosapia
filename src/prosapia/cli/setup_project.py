"""
Set up a new project directory for a linker design campaign.

Reads the input PDB, extracts protein info (subunit length, chain count,
residue range), and scaffolds the project directory with:
  - protein_info.json
  - .env  
  - activation/ scripts
  - specs/ with suggested rfd3 yamls
  - tools/rfdiffusion3/ sbatch

Usage:
    sapia setup_project --pdb SlyB_trim.pdb --run-dir /path/to/project
    sapia setup_project --pdb SlyB_trim.pdb  # uses current directory
"""

import argparse
import json
import shutil
from pathlib import Path

import gemmi


ACTIVATION_TEMPLATES = {
    "rfdiffusion3.sh": """# Activation script for RFdiffusion3
module load Foundry/0.2.0-foss-2025a-CUDA-12.8.0
export FOUNDRY_CHECKPOINT_DIRS="$VSC_DATA_VO/foundry/foundry_checkpoints"
""",
    "python.sh": """# Activation script for CPU Python tools
source /data/brussel/118/vsc11875/prosapia-env/bin/activate
""",
    "boltz.sh": """# Activation script for Boltz on VUB HPC
module load Boltz-2/2.2.1-foss-2024a-CUDA-12.6.0
export BOLTZ_CACHE="/data/brussel/118/vsc11875/.boltz"
""",
    "proteinmpnn.sh": """# Activation script for ProteinMPNN on VUB HPC
module load ProteinMPNN/1.0.1-20230627-foss-2025a-CUDA-12.8.0
export PROTEIN_MPNN="/apps/brussel/RL9/zen2-ib/software/ProteinMPNN/1.0.1-20230627-foss-2025a-CUDA-12.8.0"
""",
    "usalign.sh": """# Activation script for USalign
export USALIGN_BIN="/data/brussel/118/vsc11875/bin/USalign"
""",
}

RFD3_SBATCH_SRC = Path("/data/brussel/118/vsc11875/prosapia/src/prosapia/tools/rfdiffusion3/rfdiffusion3.sbatch")

SPEC_TEMPLATE_NOHOT = """contig: "{chain_a}{start}-{end},{linker_min}-{linker_max},{chain_b}{start}-{end}"
is_non_loopy: true
"""

RFD4_SPEC_TEMPLATE = """slyb_linker:
  input: {input_cif}
  contig: "{chain_a}{start}-{end}, LINK:{linker_min}-{linker_max}, /0, {chain_b}{start}-{end}"
  conditions:
    C_CRD: {{true: [{{select: "sel(\'{chain_a}\') and is_protein_backbone"}}, {{select: "sel(\'{chain_b}\') and is_protein_backbone"}}]}}
    C_SEQ: {{true: [{{select: "sel(\'{chain_a}\')"}} , {{select: "sel(\'{chain_b}\')"}}]}}
"""

SPEC_TEMPLATE_HOT = """contig: "{chain_a}{start}-{end},{linker_min}-{linker_max},{chain_b}{start}-{end}"
is_non_loopy: true
select_hotspots:
{hotspots}
infer_ori_strategy: hotspots
"""


def get_protein_info(pdb_path: Path) -> dict:
    st = gemmi.read_structure(str(pdb_path))
    model = st[0]
    chains = list(model)
    
    chain_a = chains[0]
    residues = [r for r in chain_a if r.find_atom("CA", "*")]
    
    native_sequence = gemmi.one_letter_code([r.name for r in residues])

    return {
        "subunit_len": len(residues),
        "n_chains": len(chains),
        "contig_start": residues[0].seqid.num,
        "contig_end": residues[-1].seqid.num,
        "chain_a": chain_a.name,
        "chain_b": chains[1].name if len(chains) > 1 else "B",
        "native_sequence": native_sequence,
        "input_pdb": str(pdb_path.resolve()),
    }


def setup_project(pdb_path: Path, run_dir: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. protein_info.json
    info = get_protein_info(pdb_path)
    info_path = run_dir / "protein_info.json"
    info_path.write_text(json.dumps(info, indent=2))
    print(f"Written {info_path}")

    # 2. activation scripts
    act_dir = run_dir / "activation"
    act_dir.mkdir(exist_ok=True)
    for name, content in ACTIVATION_TEMPLATES.items():
        (act_dir / name).write_text(content)
    print(f"Written activation scripts to {act_dir}")

    # 3. .env
    scratch = str(run_dir.resolve()).replace("/vscmnt/brussel_pixiu_data/_data_brussel", "/data/brussel")
    rhea = str(run_dir.resolve())
    env_content = f"""# prosapia config for VUB HPC

SAPIA_ACTIVATE_RFDIFFUSION3="{rhea}/activation/rfdiffusion3.sh"
SAPIA_ACTIVATE_BBCHECK="{rhea}/activation/python.sh"
SAPIA_ACTIVATE_CHAINLEN="{rhea}/activation/python.sh"
SAPIA_ACTIVATE_LINKER_CLASH="{rhea}/activation/python.sh"
SAPIA_ACTIVATE_BOLTZ="{rhea}/activation/boltz.sh"
SAPIA_ACTIVATE_PROTEINMPNN="{rhea}/activation/proteinmpnn.sh"
SAPIA_ACTIVATE_USALIGN="{rhea}/activation/usalign.sh"
SAPIA_ACTIVATE_C12_CLASH="{rhea}/activation/python.sh"
PROSAPIA_TOOLS_DIR=/data/brussel/118/vsc11875/prosapia/src/prosapia/tools
"""
    (run_dir / ".env").write_text(env_content)
    print(f"Written .env")

    # 4. tools/rfdiffusion3 sbatch
    tools_rfd3 = run_dir / "tools" / "rfdiffusion3"
    tools_rfd3.mkdir(parents=True, exist_ok=True)
    if RFD3_SBATCH_SRC.exists():
        shutil.copy2(RFD3_SBATCH_SRC, tools_rfd3 / "rfdiffusion3.sbatch")
        print(f"Copied rfdiffusion3.sbatch to {tools_rfd3}")

    # 5. specs
    specs_dir = run_dir / "specs"
    specs_dir.mkdir(exist_ok=True)
    
    s = info["contig_start"]
    e = info["contig_end"]
    a = info["chain_a"]
    b = info["chain_b"]
    
    for name, lmin, lmax in [("l20_65", 20, 65), ("l65_104", 65, 104)]:
        spec = SPEC_TEMPLATE_NOHOT.format(
            chain_a=a, chain_b=b, start=s, end=e,
            linker_min=lmin, linker_max=lmax
        )
        (specs_dir / f"{name}_nohot.yaml").write_text(spec)
    
    # Write rfd4 specs (two-chain format, no hotspots)
    input_cif = str(pdb_path.with_suffix(".cif").resolve())
    for name, lmin, lmax in [("l20_65", 20, 65), ("l65_104", 65, 104)]:
        spec = RFD4_SPEC_TEMPLATE.format(
            input_cif=input_cif, chain_a=a, chain_b=b,
            start=s, end=e, linker_min=lmin, linker_max=lmax
        )
        (specs_dir / f"rfd4_{name}.yaml").write_text(spec)

    print(f"Written specs to {specs_dir}")
    print(f"\nProtein info:")
    for k, v in info.items():
        print(f"  {k}: {v}")
    print(f"\nProject ready at {run_dir}")


def build_setup_project_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--pdb", type=Path, required=True, help="Input PDB file.")
    parser.add_argument("--run-dir", type=Path, default=Path("."), help="Project directory to set up. Defaults to current directory.")
    return parser


def setup_project_from_args(args: argparse.Namespace) -> None:
    setup_project(pdb_path=args.pdb, run_dir=args.run_dir)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set up a new linker design project directory.",
        parents=[build_setup_project_parser()],
    )
    setup_project_from_args(parser.parse_args())


if __name__ == "__main__":
    main()
