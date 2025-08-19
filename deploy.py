import os
import shutil
import subprocess
from pathlib import Path

def find_latest_workspace():
    temp_dir = Path(os.environ["TEMP"])
    candidates = [d for d in temp_dir.iterdir() if d.is_dir() and d.name.startswith("iac_ws_")]
    if not candidates:
        raise FileNotFoundError("No iac_ws_* workspace folders found in TEMP.")
    return max(candidates, key=lambda d: d.stat().st_mtime)

def copy_lambda_function(source, dest):
    os.makedirs(dest.parent, exist_ok=True)
    shutil.copy2(source, dest)
    print(f"✅ Copied lambda_function.py to: {dest}")

def run_terraform(path):
    print("🚀 Running Terraform...")
    subprocess.run(["terraform", "init"], cwd=path, check=True)
    subprocess.run(["terraform", "apply", "-auto-approve"], cwd=path, check=True)

if __name__ == "__main__":
    # Set source path
    project_root = Path.cwd()
    lambda_src = project_root / "src" / "templates" / "aws" / "lambda_function.py"

    if not lambda_src.exists():
        raise FileNotFoundError(f"{lambda_src} does not exist. Make sure the file is in place.")

    # Find the latest workspace
    workspace = find_latest_workspace()
    lambda_dest = workspace / "src" / "templates" / "aws" / "lambda_function.py"

    # Copy file and run Terraform
    copy_lambda_function(lambda_src, lambda_dest)
    run_terraform(workspace)
