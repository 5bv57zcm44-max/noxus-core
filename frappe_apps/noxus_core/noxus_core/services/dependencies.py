from __future__ import annotations

from collections import defaultdict
from typing import Any

from packaging.specifiers import SpecifierSet
from packaging.version import Version


def resolve(
    manifests: list[dict[str, Any]], selected: list[str], platform: dict[str, str]
) -> dict[str, Any]:
    catalog = {item["name"]: item for item in manifests}
    required: set[str] = set(selected)
    warnings: list[str] = []
    visiting: list[str] = []
    visited: set[str] = set()
    order: list[str] = []

    def split(spec: str) -> tuple[str, str]:
        for index, character in enumerate(spec):
            if character in "<>=!~":
                return spec[:index], spec[index:]
        return spec, ""

    def visit(name: str) -> None:
        if name in visiting:
            start = visiting.index(name)
            raise ValueError("Circular dependency: " + " -> ".join([*visiting[start:], name]))
        if name in visited:
            return
        manifest = catalog.get(name)
        if not manifest:
            raise ValueError(f"Missing dependency: {name}")
        visiting.append(name)
        for requirement in manifest.get("dependencies", {}).get("required", []):
            dependency, constraint = split(requirement)
            dependency_manifest = catalog.get(dependency)
            if not dependency_manifest:
                raise ValueError(f"{name} requires missing dependency {dependency}")
            if constraint and Version(dependency_manifest["version"]) not in SpecifierSet(
                constraint
            ):
                raise ValueError(
                    f"{name} requires {requirement}, found {dependency_manifest['version']}"
                )
            required.add(dependency)
            visit(dependency)
        for recommendation in manifest.get("dependencies", {}).get("recommended", []):
            recommended, _constraint = split(recommendation)
            if recommended not in required:
                warnings.append(f"{name} recommends {recommendation}")
        for conflict in manifest.get("dependencies", {}).get("conflicts", []):
            conflict_name, _constraint = split(conflict)
            if conflict_name in required:
                raise ValueError(f"{name} conflicts with {conflict}")
        for component, constraint in manifest.get("platform", {}).items():
            if (
                constraint
                and component in platform
                and Version(platform[component]) not in SpecifierSet(constraint)
            ):
                raise ValueError(f"{name} does not support {component} {platform[component]}")
        visiting.pop()
        visited.add(name)
        order.append(name)

    for module in sorted(required):
        visit(module)
    return {"install_order": order, "warnings": sorted(set(warnings)), "graph": defaultdict(list)}
