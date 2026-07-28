from pathlib import Path

from noxus_module_sdk.project import ProjectConfig, ProjectType

from noxusai.context import RuntimeContext
from noxusai.services.lifecycle import create_backup, lifecycle_action
from noxusai.services.process import CommandResult, ProcessRunner


def project(root: Path) -> ProjectConfig:
    (root / "compose.yaml").write_text("services: {}\n", encoding="utf-8")
    (root / "compose.production.yaml").write_text("services: {}\n", encoding="utf-8")
    return ProjectConfig(
        name="example",
        project_type=ProjectType.SAAS,
        database="mariadb",
        root=root,
    )


def test_start_uses_production_profile_and_override(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[tuple[str, ...], dict[str, str] | None]] = []

    def fake_run(self, args, **kwargs):
        safe_args = tuple(args)
        calls.append((safe_args, kwargs.get("env")))
        return CommandResult(safe_args, 0, "", "")

    monkeypatch.setattr(ProcessRunner, "run", fake_run)
    lifecycle_action(RuntimeContext(cwd=tmp_path), project(tmp_path), "start")

    args, environment = calls[-1]
    assert "--profile" in args
    assert args[args.index("--profile") + 1] == "production"
    assert str(tmp_path / "compose.production.yaml") in args
    assert environment == {"NOXUS_DEPLOYMENT_PROFILE": "production"}


def test_dev_uses_development_profile_without_override(tmp_path: Path, monkeypatch) -> None:
    calls: list[tuple[str, ...]] = []

    def fake_run(self, args, **kwargs):
        safe_args = tuple(args)
        calls.append(safe_args)
        return CommandResult(safe_args, 0, "", "")

    monkeypatch.setattr(ProcessRunner, "run", fake_run)
    lifecycle_action(RuntimeContext(cwd=tmp_path), project(tmp_path), "dev")

    args = calls[-1]
    assert args[args.index("--profile") + 1] == "development"
    assert str(tmp_path / "compose.production.yaml") not in args


def test_consecutive_backups_use_distinct_directories(tmp_path: Path) -> None:
    database = tmp_path / "db.sqlite3"
    database.write_bytes(b"sqlite fixture")
    website = ProjectConfig(
        name="example",
        project_type=ProjectType.WEBSITE,
        database="sqlite",
        docker=False,
        root=tmp_path,
    )
    context = RuntimeContext(cwd=tmp_path)

    first = create_backup(context, website)
    second = create_backup(context, website)

    assert first["backup"] != second["backup"]
    assert Path(str(first["backup"])).read_bytes() == b"sqlite fixture"
    assert Path(str(second["backup"])).read_bytes() == b"sqlite fixture"
