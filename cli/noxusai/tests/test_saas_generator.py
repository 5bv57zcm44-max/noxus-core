from pathlib import Path

from noxusai.context import RuntimeContext
from noxusai.services.saas_generator import generate_saas


def test_source_payload_generation_adds_maintenance_dependency(tmp_path: Path) -> None:
    target = tmp_path / "operations"
    result = generate_saas(
        RuntimeContext(cwd=tmp_path),
        target=target,
        name="operations",
        industry="maintenance",
        language="both",
        modules=["maintenance"],
        with_erpnext=False,
        edge_repository=None,
        edge_branch=None,
        admin_secret_file=None,
        docker=True,
        start=False,
    )
    assert result["created"] is True
    assert result["apps"] == ["noxus_core", "noxus_inventory", "noxus_maintenance"]
    assert (target / "compose.yaml").is_file()
    environment = (target / ".env").read_text()
    assert "NOXUS_ADMIN_PASSWORD" not in environment
    assert "NOXUS_APPS=noxus_core,noxus_inventory,noxus_maintenance" in environment
    generated_ignore = (target / ".gitignore").read_text()
    assert ".env\n" in generated_ignore
    assert "secrets/*.txt\n" in generated_ignore
    assert "!secrets/.gitkeep\n" in generated_ignore
