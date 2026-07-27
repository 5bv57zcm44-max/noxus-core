import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PAYLOAD_PATHS = ("frappe_apps", "infrastructure", "ui/dist", "docs", "LICENSE")
EXCLUDED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "test-results",
    "playwright-report",
}


def payload_paths() -> set[str]:
    result: set[str] = set()
    for name in PAYLOAD_PATHS:
        source = ROOT / name
        candidates = [source] if source.is_file() else source.rglob("*")
        for candidate in candidates:
            if candidate.is_file() and not EXCLUDED_PARTS.intersection(candidate.parts):
                result.add(candidate.relative_to(ROOT).as_posix())
    return result


def test_release_manifest_matches_every_payload_file() -> None:
    manifest = json.loads((ROOT / "release-manifest.json").read_text(encoding="utf-8"))
    assert manifest["files"]
    assert {entry["path"] for entry in manifest["files"]} == payload_paths()
    for entry in manifest["files"]:
        path = (ROOT / entry["path"]).resolve()
        assert ROOT.resolve() in path.parents
        assert path.stat().st_size == entry["size"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]


def test_production_container_sources_use_digests_and_never_latest() -> None:
    files = [
        ROOT / "infrastructure" / "docker" / "compose.yaml",
        ROOT / "infrastructure" / "docker" / "images" / "backend.Dockerfile",
        ROOT / "infrastructure" / "docker" / "images" / "proxy.Dockerfile",
        ROOT / "cli" / "noxusai" / "templates" / "website" / "docker" / "Dockerfile.j2",
        ROOT / "cli" / "noxusai" / "templates" / "website" / "docker" / "compose.yaml.j2",
    ]
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert ":latest" not in content
        for line in content.splitlines():
            stripped = line.strip()
            if (
                stripped.startswith(("FROM ", "image:"))
                and "noxus-runtime:" not in stripped
                and "noxus-proxy:" not in stripped
            ):
                assert "@sha256:" in stripped, f"mutable image in {path}: {line}"


def test_original_packages_declare_gpl() -> None:
    assert 'license = "GPL-3.0-or-later"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for pyproject in (ROOT / "frappe_apps").glob("*/pyproject.toml"):
        assert 'license = "GPL-3.0-or-later"' in pyproject.read_text(encoding="utf-8")


def test_github_actions_are_pinned_to_immutable_commits() -> None:
    action = re.compile(r"^\s*- uses: [^@\s]+@([0-9a-f]{40})(?:\s+#.*)?$")
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        uses = [
            line for line in workflow.read_text(encoding="utf-8").splitlines() if "uses:" in line
        ]
        assert uses, f"workflow contains no actions: {workflow}"
        for line in uses:
            assert action.match(line), f"mutable action reference in {workflow}: {line}"
