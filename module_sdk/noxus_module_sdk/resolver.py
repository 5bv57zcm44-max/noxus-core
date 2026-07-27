from __future__ import annotations

from dataclasses import dataclass, field

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from noxus_module_sdk.manifest import DependencySpec, ModuleManifest


class ResolutionError(ValueError):
    pass


@dataclass(slots=True)
class ResolutionResult:
    installation_order: list[ModuleManifest]
    recommended: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class DependencyResolver:
    def __init__(
        self,
        manifests: list[ModuleManifest],
        *,
        python_version: str = "3.14.6",
        frappe_version: str = "16.28.0",
        erpnext_version: str | None = None,
    ) -> None:
        self.catalog = {manifest.name: manifest for manifest in manifests}
        if len(self.catalog) != len(manifests):
            raise ResolutionError("Module catalog contains duplicate names")
        self.python_version = Version(python_version)
        self.frappe_version = Version(frappe_version)
        self.erpnext_version = Version(erpnext_version) if erpnext_version else None

    def resolve(
        self, requested: list[str], *, include_recommended: bool = False
    ) -> ResolutionResult:
        selected: set[str] = set()
        recommended: set[str] = set()
        visiting: list[str] = []

        def visit(name: str) -> None:
            if name == "erpnext":
                if self.erpnext_version is None:
                    raise ResolutionError("ERPNext was requested but is not enabled")
                selected.add(name)
                return
            if name in visiting:
                cycle = [*visiting[visiting.index(name) :], name]
                raise ResolutionError(f"Circular dependency detected: {' -> '.join(cycle)}")
            if name in selected:
                return
            manifest = self.catalog.get(name)
            if manifest is None:
                raise ResolutionError(f"Missing module dependency: {name}")
            self._validate_platform(manifest)
            visiting.append(name)
            for dependency in sorted(manifest.dependencies.required, key=lambda item: item.name):
                self._validate_dependency_version(manifest, dependency)
                visit(dependency.name)
            for dependency in manifest.dependencies.recommended:
                recommended.add(str(dependency))
                if include_recommended and (
                    dependency.name == "erpnext" or dependency.name in self.catalog
                ):
                    self._validate_dependency_version(manifest, dependency)
                    visit(dependency.name)
            visiting.pop()
            selected.add(name)

        for requested_name in sorted(set(requested)):
            visit(requested_name)

        for name in sorted(selected):
            if name == "erpnext":
                continue
            manifest = self.catalog[name]
            for conflict in manifest.dependencies.conflicts:
                if conflict.name in selected:
                    raise ResolutionError(f"{manifest.name} conflicts with {conflict}")

        ordered_names = self._topological_sort(selected)
        ordered = [self.catalog[name] for name in ordered_names if name != "erpnext"]
        return ResolutionResult(
            installation_order=ordered,
            recommended=sorted(recommended),
            warnings=[
                f"Recommended dependency not selected: {item}" for item in sorted(recommended)
            ],
        )

    def _validate_platform(self, manifest: ModuleManifest) -> None:
        requirements = manifest.platform
        if self.python_version not in SpecifierSet(requirements.python):
            raise ResolutionError(f"{manifest.name} does not support Python {self.python_version}")
        if self.frappe_version not in SpecifierSet(requirements.frappe):
            raise ResolutionError(f"{manifest.name} does not support Frappe {self.frappe_version}")
        if requirements.erpnext:
            if self.erpnext_version is None:
                raise ResolutionError(f"{manifest.name} requires ERPNext")
            if self.erpnext_version not in SpecifierSet(requirements.erpnext):
                raise ResolutionError(
                    f"{manifest.name} does not support ERPNext {self.erpnext_version}"
                )

    def _validate_dependency_version(
        self, manifest: ModuleManifest, dependency: DependencySpec
    ) -> None:
        if dependency.name == "erpnext":
            if self.erpnext_version is None or not dependency.accepts(str(self.erpnext_version)):
                raise ResolutionError(f"{manifest.name} requires {dependency}")
            return
        candidate = self.catalog.get(dependency.name)
        if candidate is None or not dependency.accepts(candidate.version):
            found = candidate.version if candidate else "not installed"
            raise ResolutionError(f"{manifest.name} requires {dependency}; found {found}")

    def _topological_sort(self, selected: set[str]) -> list[str]:
        output: list[str] = []
        permanent: set[str] = set()

        def add(name: str) -> None:
            if name in permanent:
                return
            if name == "erpnext":
                permanent.add(name)
                output.append(name)
                return
            manifest = self.catalog[name]
            for dependency in sorted(manifest.dependencies.required, key=lambda item: item.name):
                if dependency.name in selected:
                    add(dependency.name)
            permanent.add(name)
            output.append(name)

        for item in sorted(selected):
            add(item)
        return output
