from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAYLOAD_PATHS = ("frappe_apps", "infrastructure", "ui/dist", "docs", "LICENSE")
EXCLUDED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "test-results",
    "playwright-report",
}
IMAGE_DIGESTS = {
    "python": "sha256:86f975aca15cf04a40b399eebede9aea7c82eae084d1f1a0a6ef6bcaae871a30",
    "node": "sha256:6f7b03f7c2c8e2e784dcf9295400527b9b1270fd37b7e9a7285cf83b6951452d",
    "mariadb": "sha256:78a5047d3ba33975f183f183c2464cc7f1eab13ec8667e57cc9a5821d6da7577",
    "redis": "sha256:f0707c78ea880b293ccdeb410c9c0a8ccae93fe7128799b751333a698b0a39a7",
    "nginx": "sha256:30f1c0d78e0ad60901648be663a710bdadf19e4c10ac6782c235200619158284",
    "postgres": "sha256:1961f96e6029a02c3812d7cb329a3b03a3ac2bb067058dec17b0f5596aca9296",
}


def project_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as pyproject:
        document = tomllib.load(pyproject)
    version = document.get("project", {}).get("version")
    if not isinstance(version, str) or not version:
        raise SystemExit("pyproject.toml does not declare project.version")
    return version


def files() -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for name in PAYLOAD_PATHS:
        source = ROOT / name
        candidates = [source] if source.is_file() else source.rglob("*")
        for candidate in candidates:
            if not candidate.is_file() or EXCLUDED_PARTS & set(candidate.parts):
                continue
            body = candidate.read_bytes()
            entries.append(
                {
                    "path": candidate.relative_to(ROOT).as_posix(),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "size": len(body),
                }
            )
    return sorted(entries, key=lambda item: str(item["path"]))


def main() -> None:
    manifest = {
        "schema_version": 1,
        "noxus_version": project_version(),
        "versions": {
            "python": "3.14.6",
            "frappe": "16.28.0",
            "erpnext": "16.29.0",
            "node": "24.18.0",
            "mariadb": "11.8.6",
            "redis": "7.2.14",
        },
        "files": files(),
        "image_digests": IMAGE_DIGESTS,
    }
    target = ROOT / "release-manifest.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(target)


if __name__ == "__main__":
    main()
