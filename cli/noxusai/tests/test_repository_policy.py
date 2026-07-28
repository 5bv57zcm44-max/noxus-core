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


def test_runtime_image_installs_only_declared_local_apps() -> None:
    dockerfile = (ROOT / "infrastructure" / "docker" / "images" / "backend.Dockerfile").read_text(
        encoding="utf-8"
    )
    assert "/opt/noxus/apps/noxus_*" in dockerfile
    assert "printf 'frappe\\n' > sites/apps.txt" in dockerfile
    assert 'pip install --no-cache-dir --editable "apps/$app_name"' in dockerfile
    assert "yarn --cwd apps/erpnext install --frozen-lockfile --non-interactive" in dockerfile
    assert 'bench get-app "$app"' not in dockerfile


def test_container_acceptance_captures_partial_start_failures() -> None:
    acceptance = (ROOT / "infrastructure" / "scripts" / "docker_acceptance.py").read_text(
        encoding="utf-8"
    )
    marked = acceptance.index("compose_started = True")
    startup = acceptance.index('compose(project, ["up", "--build", "--detach"])')
    assert marked < startup
    assert 'compose(project, ["logs", "--no-color", "--tail", "500"], check=False)' in acceptance
    assert 'compose(project, ["down", "--volumes", "--remove-orphans"], check=False)' in acceptance


def test_frappe_site_creator_drops_secret_reader_privileges() -> None:
    compose = (ROOT / "infrastructure" / "docker" / "compose.yaml").read_text(encoding="utf-8")
    entrypoint = (ROOT / "infrastructure" / "scripts" / "create-site-entrypoint.sh").read_text(
        encoding="utf-8"
    )
    dockerfile = (ROOT / "infrastructure" / "docker" / "images" / "backend.Dockerfile").read_text(
        encoding="utf-8"
    )
    site_creator = compose.split("  site-creator:", maxsplit=1)[1].split(
        "\n  backend:", maxsplit=1
    )[0]
    assert 'user: "0:0"' in site_creator
    assert "create-site-entrypoint.sh" in site_creator
    assert " gosu " in dockerfile
    assert "exec gosu frappe bash /opt/noxus/scripts/create-site.sh" in entrypoint
    assert "unset NOXUS_ADMIN_PASSWORD_FILE MARIADB_ROOT_PASSWORD_FILE" in entrypoint


def test_frappe_site_creator_uses_the_bench_sites_directory() -> None:
    creator = (ROOT / "infrastructure" / "scripts" / "create_site.py").read_text(encoding="utf-8")
    assert 'os.environ.get("FRAPPE_BENCH_ROOT", "/home/frappe/frappe-bench")' in creator
    assert 'sites_path = bench_root / "sites"' in creator
    assert "os.chdir(sites_path)" in creator
    assert "frappe.init(site, new_site=True)" in creator


def test_github_actions_are_pinned_to_immutable_commits() -> None:
    action = re.compile(r"^\s*- uses: [^@\s]+@([0-9a-f]{40})(?:\s+#.*)?$")
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        uses = [
            line for line in workflow.read_text(encoding="utf-8").splitlines() if "uses:" in line
        ]
        assert uses, f"workflow contains no actions: {workflow}"
        for line in uses:
            assert action.match(line), f"mutable action reference in {workflow}: {line}"
