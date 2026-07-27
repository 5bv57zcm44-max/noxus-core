from __future__ import annotations

import json
from pathlib import Path

from noxus_module_sdk.io import load_yaml
from noxus_module_sdk.manifest import ModuleManifest

from noxusai.context import RuntimeContext
from noxusai.services.module_generator import generate_module


def test_generated_module_contains_valid_manifest_and_sample(tmp_path: Path) -> None:
    result = generate_module(RuntimeContext(cwd=tmp_path), "repairs", tmp_path)
    target = Path(str(result["target"]))
    manifest = load_yaml(target / "noxus-module.yml", ModuleManifest)
    assert manifest.name == "noxus_repairs"
    doctype = (
        target / "noxus_repairs" / "repairs" / "doctype" / "sample_record" / "sample_record.json"
    )
    assert json.loads(doctype.read_text(encoding="utf-8"))["name"] == "Sample Record"
    assert (target / "noxus_repairs" / "tests" / "test_sample_record.py").is_file()
