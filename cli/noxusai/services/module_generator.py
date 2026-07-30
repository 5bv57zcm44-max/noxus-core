from __future__ import annotations

import json
import re
from importlib.resources import files
from pathlib import Path

import yaml
from noxusai.context import RuntimeContext
from noxusai.errors import ExitCode, NoxusError


def _license_text() -> str:
    packaged = files("noxusai").joinpath("payload").joinpath("LICENSE")
    if packaged.is_file():
        return packaged.read_text(encoding="utf-8")
    return (Path(__file__).resolve().parents[3] / "LICENSE").read_text(encoding="utf-8")


def generate_module(
    context: RuntimeContext, module_name: str, directory: Path
) -> dict[str, object]:
    slug = module_name.strip().lower().replace("-", "_").replace(" ", "_")
    if slug.startswith("noxus_"):
        slug = slug[6:]
    if not re.fullmatch(r"[a-z](?:[a-z0-9_]{0,56}[a-z0-9])?", slug):
        raise NoxusError("Module name must contain lowercase letters, numbers, or underscores")
    package = f"noxus_{slug}"
    target = (directory.resolve() / package).resolve()
    if target.parent != directory.resolve():
        raise NoxusError("Module target escapes the selected directory", exit_code=ExitCode.UNSAFE)
    if target.exists():
        raise NoxusError(f"Target already exists: {target}", exit_code=ExitCode.CONFLICT)
    if context.dry_run:
        return {"module": package, "target": str(target), "created": False}

    doctype = "Sample Record"
    doctype_slug = "sample_record"
    files: dict[str, str] = {
        "noxus-module.yml": yaml.safe_dump(
            {
                "schema_version": 1,
                "name": package,
                "display_name": slug.replace("_", " ").title(),
                "version": "1.0.0",
                "description": f"{slug.replace('_', ' ').title()} operations",
                "publisher": "NOXUS AI",
                "license": "GPL-3.0-or-later",
                "category": "operations",
                "dependencies": {"required": ["noxus_core>=1.0.0"]},
                "features": ["sample_records"],
                "roles": [f"{slug.replace('_', ' ').title()} Manager", "Viewer"],
                "permissions": [f"{slug}.read", f"{slug}.manage"],
                "api": {"namespace": f"/api/v2/method/{package}.api.v1"},
            },
            sort_keys=False,
        ),
        "README.md": f"# {package}\n\nA generated, tested NOXUS Frappe module.\n",
        "LICENSE": _license_text(),
        "pyproject.toml": (
            "[build-system]\n"
            "requires = ['setuptools==83.0.0']\n"
            "build-backend = 'setuptools.build_meta'\n\n"
            f"[project]\nname = '{package}'\nversion = '1.0.0'\n"
            "description = 'Generated NOXUS module'\n"
            "requires-python = '>=3.14,<3.15'\nlicense = 'GPL-3.0-or-later'\n"
        ),
        f"{package}/__init__.py": '__version__ = "1.0.0"\n',
        f"{package}/hooks.py": (
            f'app_name = "{package}"\n'
            f'app_title = "{slug.title()}"\n'
            'app_license = "GPL-3.0-or-later"\n'
        ),
        f"{package}/modules.txt": f"{slug.replace('_', ' ').title()}\n",
        f"{package}/{slug}/__init__.py": "",
        f"{package}/{slug}/doctype/{doctype_slug}/__init__.py": "",
        f"{package}/{slug}/doctype/{doctype_slug}/{doctype_slug}.py": (
            "from frappe.model.document import Document\n\n\n"
            f"class {doctype.replace(' ', '')}(Document):\n    pass\n"
        ),
        f"{package}/{slug}/doctype/{doctype_slug}/{doctype_slug}.json": json.dumps(
            {
                "doctype": "DocType",
                "name": doctype,
                "module": slug.replace("_", " ").title(),
                "autoname": "format:SAMPLE-.#####",
                "fields": [
                    {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1},
                    {
                        "fieldname": "status",
                        "fieldtype": "Select",
                        "label": "Status",
                        "options": "Open\nClosed",
                    },
                ],
                "permissions": [
                    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}
                ],
            },
            indent=2,
        ),
        f"{package}/api/__init__.py": "",
        f"{package}/api/v1.py": (
            "import frappe\n\n\n@frappe.whitelist()\ndef health():\n    return {'module': '"
            + package
            + "', 'status': 'ok'}\n"
        ),
        f"{package}/services/__init__.py": "",
        f"{package}/services/sample_records.py": (
            "import frappe\n\n\ndef create(title: str):\n"
            f"    return frappe.get_doc({{'doctype': '{doctype}', 'title': title}}).insert()\n"
        ),
        f"{package}/tests/__init__.py": "",
        f"{package}/tests/test_sample_record.py": (
            "import frappe\nfrom frappe.tests.utils import FrappeTestCase\n\n\n"
            "class TestSampleRecord(FrappeTestCase):\n"
            "    def test_create_sample(self):\n"
            "        doc = frappe.get_doc("
            f"{{'doctype': '{doctype}', 'title': 'Verified'}}"
            ").insert()\n"
            "        self.assertEqual(doc.title, 'Verified')\n"
        ),
        "fixtures/.gitkeep": "",
        "patches/.gitkeep": "",
        "permissions/README.md": "Permissions are declared in the manifest and DocType JSON.\n",
        "workflows/README.md": "Versioned workflow fixtures belong here.\n",
        "reports/README.md": "Script and query reports belong here.\n",
    }
    for relative, content in files.items():
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return {"module": package, "target": str(target), "created": True, "files": len(files)}
