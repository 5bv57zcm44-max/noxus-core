import ast
import hashlib
import json
import re
import tomllib
from pathlib import Path

import yaml

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
                and not stripped.startswith("FROM scratch")
                and "noxus-runtime:" not in stripped
                and "noxus-proxy:" not in stripped
            ):
                assert "@sha256:" in stripped, f"mutable image in {path}: {line}"


def test_original_packages_declare_gpl() -> None:
    assert 'license = "GPL-3.0-or-later"' in (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    for pyproject in (ROOT / "frappe_apps").glob("*/pyproject.toml"):
        assert 'license = "GPL-3.0-or-later"' in pyproject.read_text(encoding="utf-8")


def test_stable_version_is_synchronized_across_public_artifacts() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    assert version == "1.0.0"
    assert "Development Status :: 5 - Production/Stable" in project["classifiers"]
    assert project["urls"]["Repository"] == "https://github.com/5bv57zcm44-max/noxus-core"
    assert f'__version__ = "{version}"' in (ROOT / "cli" / "noxusai" / "__init__.py").read_text(
        encoding="utf-8"
    )
    assert (
        json.loads((ROOT / "ui" / "package.json").read_text(encoding="utf-8"))["version"] == version
    )
    assert (ROOT / "docs" / f"release-notes-{version}.md").is_file()
    for app_project in (ROOT / "frappe_apps").glob("noxus_*/pyproject.toml"):
        assert (
            tomllib.loads(app_project.read_text(encoding="utf-8"))["project"]["version"] == version
        )
        manifest = yaml.safe_load(
            (app_project.parent / "noxus-module.yml").read_text(encoding="utf-8")
        )
        assert manifest["version"] == version


def test_runtime_image_installs_only_declared_local_apps() -> None:
    dockerfile = (ROOT / "infrastructure" / "docker" / "images" / "backend.Dockerfile").read_text(
        encoding="utf-8"
    )
    assert "/opt/noxus/apps/noxus_*" in dockerfile
    assert "printf 'frappe\\n' > sites/apps.txt" in dockerfile
    assert 'pip install --no-cache-dir --editable "apps/$app_name"' in dockerfile
    assert "yarn --cwd apps/erpnext install --frozen-lockfile --non-interactive" in dockerfile
    assert 'bench get-app "$app"' not in dockerfile


def test_runtime_image_includes_frappe_restore_file_detector() -> None:
    dockerfile = (ROOT / "infrastructure" / "docker" / "images" / "backend.Dockerfile").read_text(
        encoding="utf-8"
    )
    install_block = dockerfile.split("apt-get install", maxsplit=1)[1].split(
        "&& rm -rf /var/lib/apt/lists/*", maxsplit=1
    )[0]
    assert "file" in install_block.split()


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


def test_frappe_restore_uses_the_bench_sites_directory() -> None:
    restore = (ROOT / "infrastructure" / "scripts" / "restore_site.py").read_text(encoding="utf-8")
    assert 'os.environ.get("FRAPPE_BENCH_ROOT", "/home/frappe/frappe-bench")' in restore
    assert 'sites_path = bench_root / "sites"' in restore
    assert "os.chdir(sites_path)" in restore
    assert "frappe.init(site)" in restore


def test_frappe_restore_drops_secret_reader_privileges() -> None:
    entrypoint = (ROOT / "infrastructure" / "scripts" / "restore-site-entrypoint.sh").read_text(
        encoding="utf-8"
    )
    lifecycle = (ROOT / "cli" / "noxusai" / "services" / "lifecycle.py").read_text(encoding="utf-8")
    assert "read_protected_secret MARIADB_ROOT_PASSWORD MARIADB_ROOT_PASSWORD_FILE" in entrypoint
    assert "unset MARIADB_ROOT_PASSWORD_FILE" in entrypoint
    assert 'install --owner=frappe --group=frappe --mode=600 "$backup_path"' in entrypoint
    assert 'gosu frappe "$@"' in entrypoint
    assert '"/opt/noxus/scripts/restore-site-entrypoint.sh"' in lifecycle


def test_frappe_runtime_image_minimizes_and_patches_runtime_dependencies() -> None:
    dockerfile = (ROOT / "infrastructure" / "docker" / "images" / "backend.Dockerfile").read_text(
        encoding="utf-8"
    )
    system_environment = dockerfile.split("USER frappe", maxsplit=1)[0]
    build_cleanup = dockerfile.split("bench build --production", maxsplit=1)[1]
    final_cleanup = dockerfile.split("USER root", maxsplit=1)[1].split("FROM scratch", maxsplit=1)[
        0
    ]
    initialization_layer = dockerfile.split("USER frappe", maxsplit=1)[1].split(
        "COPY --chown", maxsplit=1
    )[0]
    assert "NODE_PATH=/opt/noxus/socketio-runtime/node_modules" in dockerfile
    assert "cryptography==48.0.1" in dockerfile
    assert "msgpack==1.2.1" in dockerfile
    assert "Pillow==12.3.0" in dockerfile
    assert "pypdf==6.14.2" in dockerfile
    assert "setuptools==83.0.0" in dockerfile
    assert "msgpack==1.2.1" in system_environment
    assert "setuptools==83.0.0" in system_environment
    assert "msgpack==1.2.1" in initialization_layer
    assert "setuptools==83.0.0" in initialization_layer
    assert "rm -rf /home/frappe/.cache/pip" in initialization_layer
    assert "npm ci --prefix /opt/noxus/socketio-runtime" in build_cleanup
    assert "apps/frappe/node_modules" in build_cleanup
    assert "apps/erpnext/banking/node_modules" in build_cleanup
    assert "/usr/local/lib/node_modules/npm" in build_cleanup
    assert "/home/frappe/.cache/pip" in build_cleanup
    assert "/home/frappe/.cache/yarn" in build_cleanup
    assert "USER root" in build_cleanup
    assert "/home/frappe/.cache" in final_cleanup
    assert "/root/.cache" in final_cleanup
    assert "/tmp/*" in final_cleanup  # noqa: S108 - validates image cleanup policy
    assert "FROM scratch AS runtime" in dockerfile
    assert "COPY --from=build / /" in dockerfile
    assert build_cleanup.rfind("USER frappe") < build_cleanup.rfind("EXPOSE 8000 9000")

    lock = json.loads(
        (ROOT / "infrastructure" / "docker" / "socketio-runtime" / "package-lock.json").read_text(
            encoding="utf-8"
        )
    )
    assert lock["packages"]["node_modules/socket.io-parser"]["version"] == "4.2.7"
    assert lock["packages"]["node_modules/engine.io"]["version"] == "6.6.9"
    assert lock["packages"]["node_modules/ws"]["version"] == "8.21.1"


def test_frappe_runtime_commands_preserve_queue_lists_and_site_routing() -> None:
    compose = yaml.safe_load(
        (ROOT / "infrastructure" / "docker" / "compose.yaml").read_text(encoding="utf-8")
    )
    services = compose["services"]
    assert services["worker-short"]["command"] == [
        "bench",
        "worker",
        "--queue",
        "short,default",
    ]
    assert services["worker-long"]["command"] == [
        "bench",
        "worker",
        "--queue",
        "long,default",
    ]
    health = services["backend"]["healthcheck"]["test"]
    assert health[:5] == [
        "CMD",
        "curl",
        "--fail",
        "--header",
        "Host: ${NOXUS_SITE:-noxus.localhost}",
    ]
    assert health[-1] == "http://localhost:8000/api/method/ping"


def test_frappe_public_health_method_explicitly_allows_guests() -> None:
    api = (ROOT / "frappe_apps" / "noxus_core" / "noxus_core" / "api" / "v1.py").read_text(
        encoding="utf-8"
    )
    assert "@frappe.whitelist(allow_guest=True)\ndef health()" in api


def test_frappe_apps_provide_their_declared_module_packages() -> None:
    for app in (ROOT / "frappe_apps").glob("noxus_*"):
        package = app / app.name
        declared_modules = (package / "modules.txt").read_text(encoding="utf-8").splitlines()
        assert declared_modules, f"{app.name} declares no Frappe modules"
        for module_name in declared_modules:
            module_package = re.sub(r"[^a-z0-9]+", "_", module_name.lower()).strip("_")
            assert (package / module_package / "__init__.py").is_file(), (
                f"{app.name} is missing its declared module package {module_package}"
            )


def test_frappe_apps_declare_complete_release_metadata() -> None:
    expected = {
        "app_name",
        "app_title",
        "app_publisher",
        "app_description",
        "app_email",
        "app_license",
        "app_version",
    }
    for hooks in (ROOT / "frappe_apps").glob("noxus_*/noxus_*/hooks.py"):
        tree = ast.parse(hooks.read_text(encoding="utf-8"))
        declared = {
            target.id
            for node in tree.body
            if isinstance(node, ast.Assign)
            for target in node.targets
            if isinstance(target, ast.Name)
        }
        assert expected <= declared, f"{hooks} is missing metadata: {sorted(expected - declared)}"


def test_github_actions_are_pinned_to_immutable_commits() -> None:
    action = re.compile(r"^\s*(?:-\s+)?uses: [^@\s]+@([0-9a-f]{40})(?:\s+#.*)?$")
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        uses = [
            line for line in workflow.read_text(encoding="utf-8").splitlines() if "uses:" in line
        ]
        assert uses, f"workflow contains no actions: {workflow}"
        for line in uses:
            assert action.match(line), f"mutable action reference in {workflow}: {line}"


def test_trivy_reporting_is_separate_from_release_blocking() -> None:
    for name in ("containers.yml", "security.yml"):
        workflow = yaml.safe_load(
            (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
        )
        steps = next(iter(workflow["jobs"].values()))["steps"]
        scans = [step for step in steps if str(step.get("uses", "")).startswith("aquasecurity/")]
        assert len(scans) == 2

        report, gate = scans
        assert report["with"]["format"] == "sarif"
        assert report["with"]["exit-code"] == "0"
        assert gate["with"]["format"] == "table"
        assert gate["with"]["severity"] == "CRITICAL,HIGH"
        assert gate["with"]["exit-code"] == "1"
        assert gate["with"]["skip-setup-trivy"] is True


def test_release_creates_metadata_directory_before_sbom() -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["artifacts"]["steps"]
    mkdir_index = next(
        index for index, step in enumerate(steps) if step.get("run") == "mkdir -p release-metadata"
    )
    sbom_index = next(
        index
        for index, step in enumerate(steps)
        if str(step.get("uses", "")).startswith("anchore/sbom-action@")
    )
    assert mkdir_index < sbom_index
