# src/orchestrator/runners/opa.py
import json, re, shutil, subprocess as sp
from pathlib import Path
from typing import List, Dict, Any

# Resource types we disallow in Free-Tier mode
BAD_TYPES = ["aws_db_instance", "aws_lb", "aws_alb"]

def _scan_tf_resource_types(ws: str) -> List[Dict[str, Any]]:
    """
    Scans *.tf files in the workspace and returns a list like:
    [{"type": "aws_lambda_function"}, {"type": "aws_db_instance"}, ...]
    """
    pat = re.compile(r'^\s*resource\s+"([^"]+)"\s+"[^"]+"\s*{', re.MULTILINE)
    types: List[str] = []
    for p in Path(ws).glob("*.tf"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        types += pat.findall(txt)
    return [{"type": t} for t in types]

def _python_free_tier_check(ws: str) -> List[str]:
    """
    Simple built-in checker (works even if conftest/OPA aren't installed).
    """
    res = _scan_tf_resource_types(ws)
    violations: List[str] = []
    for r in res:
        t = r["type"]
        if t in BAD_TYPES or t.startswith("aws_ecs_"):
            violations.append(f"Free-tier mode: {t} not allowed")
    return violations

def free_tier_check(ws: str, policy_dir: str) -> Dict[str, Any]:
    """
    Try conftest if available; otherwise use Python fallback.
    Returns: {"violations": [...], "engine": "conftest"|"python"}
    """
    # Prefer conftest if installed
    if shutil.which("conftest"):
        input_obj = {"resources": _scan_tf_resource_types(ws)}
        tmp = Path(ws) / "_opa_input.json"
        tmp.write_text(json.dumps(input_obj), encoding="utf-8")
        proc = sp.run(
            ["conftest", "test", str(tmp), "--policy", policy_dir, "--input", "json"],
            cwd=ws, text=True, capture_output=True
        )
        if proc.returncode == 0:
            return {"violations": [], "engine": "conftest"}
        # Combine conftest output with clean Python messages
        pyv = _python_free_tier_check(ws)
        return {"violations": pyv if pyv else [(proc.stdout + "\n" + proc.stderr).strip()],
                "engine": "conftest"}

    # Fallback: pure Python
    return {"violations": _python_free_tier_check(ws), "engine": "python"}
