import os
import subprocess
import sys
from pathlib import Path

import yaml
from noxusai.context import RuntimeContext
from noxusai.services.configuration import load_project
from noxusai.services.website_generator import MODULES, generate_website
from noxusai.services.website_update import update_generated_website


def test_generate_full_website_is_safe_and_complete(tmp_path: Path) -> None:
    target = tmp_path / "example-site"
    result = generate_website(
        RuntimeContext(cwd=tmp_path),
        target=target,
        name="example-site",
        database="postgres",
        authentication="both",
        language="both",
        modules=list(MODULES),
        docker=True,
        initialize_git=False,
        start=False,
    )

    assert result["created"] is True
    assert (target / "Dockerfile").is_file()
    assert (target / "compose.production.yaml").is_file()
    assert (target / "secrets" / "postgres_password.txt").stat().st_size >= 32
    assert (target / "secrets" / "django_secret.txt").stat().st_size >= 64
    assert (target / "apps" / "contact" / "models.py").is_file()
    assert "class ContactRecord" in (target / "apps" / "contact" / "models.py").read_text()
    config = yaml.safe_load((target / ".noxus" / "project.yml").read_text())
    assert config["modules"] == sorted(MODULES)
    assert "root" not in config
    assert "files" in (target / ".noxus" / "template-lock.json").read_text()


def test_generate_sqlite_minimal_project(tmp_path: Path) -> None:
    target = tmp_path / "minimal-site"
    generate_website(
        RuntimeContext(cwd=tmp_path),
        target=target,
        name="minimal-site",
        database="sqlite",
        authentication="session",
        language="arabic",
        modules=["company"],
        docker=False,
        initialize_git=False,
        start=False,
    )
    assert not (target / "compose.yaml").exists()
    assert 'title_key = "ar"' in (target / "apps" / "company" / "tests" / "test_api.py").read_text()


def test_generated_full_project_migrates_checks_and_tests(tmp_path: Path) -> None:
    target = tmp_path / "validated-site"
    generate_website(
        RuntimeContext(cwd=tmp_path),
        target=target,
        name="validated-site",
        database="sqlite",
        authentication="both",
        language="both",
        modules=list(MODULES),
        docker=False,
        initialize_git=False,
        start=False,
    )
    environment = {**os.environ, "DJANGO_SETTINGS_MODULE": "config.settings.test"}
    for command in (
        [sys.executable, "manage.py", "migrate", "--noinput"],
        [sys.executable, "manage.py", "check"],
        [sys.executable, "-m", "pytest", "-q"],
    ):
        completed = subprocess.run(
            command,
            cwd=target,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr


def test_update_reports_user_edits_without_overwriting(tmp_path: Path) -> None:
    target = tmp_path / "editable-site"
    context = RuntimeContext(cwd=tmp_path)
    generate_website(
        context,
        target=target,
        name="editable-site",
        database="sqlite",
        authentication="session",
        language="both",
        modules=["company"],
        docker=False,
        initialize_git=False,
        start=False,
    )
    readme = target / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nUser documentation.\n", encoding="utf-8"
    )
    project = load_project(target)
    result = update_generated_website(RuntimeContext(cwd=target), project)
    assert any(item["path"] == "README.md" for item in result["conflicts"])
    assert readme.read_text(encoding="utf-8").endswith("User documentation.\n")
