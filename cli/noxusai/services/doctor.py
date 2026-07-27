from __future__ import annotations

import shutil
import socket
import sys
from dataclasses import asdict, dataclass

from noxusai.context import RuntimeContext
from noxusai.services.process import ProcessRunner


@dataclass(slots=True)
class Check:
    name: str
    status: str
    detail: str
    required: bool = True


def _command_check(runner: ProcessRunner, name: str, args: list[str], required: bool) -> Check:
    executable = shutil.which(args[0])
    if not executable:
        return Check(name, "fail" if required else "warning", "not found", required)
    result = runner.run(args, check=False, timeout=15)
    detail = result.stdout.splitlines()[0] if result.stdout else result.stderr.splitlines()[0]
    return Check(name, "pass" if result.returncode == 0 else "fail", detail, required)


def _port_check(port: int) -> Check:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.25)
        used = probe.connect_ex(("127.0.0.1", port)) == 0
    return Check(
        f"Port {port}", "warning" if used else "pass", "in use" if used else "available", False
    )


def run_doctor(context: RuntimeContext, workflow: str = "all") -> list[Check]:
    runner = ProcessRunner(context)
    version = sys.version_info
    supported = (3, 11) <= version[:2] < (3, 15)
    checks = [
        Check(
            "Python",
            "pass" if supported else "fail",
            f"{version.major}.{version.minor}.{version.micro}; supported >=3.11,<3.15",
        ),
        _command_check(runner, "Git", ["git", "--version"], workflow in {"all", "edge"}),
        _command_check(runner, "Docker", ["docker", "--version"], workflow in {"all", "saas"}),
        _command_check(
            runner,
            "Docker Compose",
            ["docker", "compose", "version"],
            workflow in {"all", "saas"},
        ),
        _command_check(runner, "Node.js", ["node", "--version"], False),
    ]
    free_gib = shutil.disk_usage(context.cwd).free / 1024**3
    required_gib = 15 if workflow in {"all", "saas"} else 2
    checks.append(
        Check(
            "Disk space",
            "pass" if free_gib >= required_gib else "fail",
            f"{free_gib:.1f} GiB free; {required_gib} GiB required",
        )
    )
    checks.extend(_port_check(port) for port in (8000, 8080, 5173))
    return checks


def serialize_checks(checks: list[Check]) -> list[dict[str, object]]:
    return [asdict(check) for check in checks]
