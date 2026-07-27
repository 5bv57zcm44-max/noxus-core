from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import yaml
from noxus_module_sdk.project import ProjectConfig
from noxusai.context import RuntimeContext
from noxusai.errors import ExitCode, NoxusError
from noxusai.services.website_generator import generate_website


def _hash(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def update_generated_website(context: RuntimeContext, project: ProjectConfig) -> dict[str, object]:
    lock_path = project.root / ".noxus" / "template-lock.json"
    if not lock_path.is_file():
        raise NoxusError("Generated template lock is missing", exit_code=ExitCode.CONFLICT)
    old_lock = json.loads(lock_path.read_text(encoding="utf-8"))
    old_hashes = old_lock.get("files", {})
    if not isinstance(old_hashes, dict):
        raise NoxusError("Generated template lock is invalid", exit_code=ExitCode.CONFLICT)

    with tempfile.TemporaryDirectory(prefix="noxus-update-") as temporary:
        reference = Path(temporary) / project.name
        generate_website(
            RuntimeContext(cwd=Path(temporary)),
            target=reference,
            name=project.name,
            database=project.database,
            authentication=project.authentication,
            language=project.language,
            modules=project.modules,
            docker=project.docker,
            initialize_git=False,
            start=False,
        )
        new_lock = json.loads(
            (reference / ".noxus" / "template-lock.json").read_text(encoding="utf-8")
        )
        new_hashes = new_lock["files"]
        replaced: list[str] = []
        conflicts: list[dict[str, str | None]] = []
        unchanged: list[str] = []
        for relative, new_hash in sorted(new_hashes.items()):
            destination = project.root / relative
            current_hash = _hash(destination)
            old_hash = old_hashes.get(relative)
            if current_hash == new_hash:
                unchanged.append(relative)
            elif current_hash == old_hash:
                replaced.append(relative)
                if not context.dry_run:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(reference / relative, destination)
            else:
                conflicts.append(
                    {"path": relative, "old": old_hash, "current": current_hash, "new": new_hash}
                )
        plan = {
            "template_version": new_lock["template_version"],
            "replaced": replaced,
            "unchanged": unchanged,
            "conflicts": conflicts,
        }
        plan_path = project.root / ".noxus" / "update-plan.yml"
        if not context.dry_run:
            plan_path.write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
            safe_hashes = dict(old_hashes)
            for relative in replaced:
                safe_hashes[relative] = new_hashes[relative]
            lock_path.write_text(
                json.dumps(
                    {"template_version": new_lock["template_version"], "files": safe_hashes},
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        return {**plan, "plan": str(plan_path), "applied": not context.dry_run}
