"""Shared, framework-neutral contracts for NOXUS modules and blueprints."""

from noxus_module_sdk.blueprint import SolutionBlueprint
from noxus_module_sdk.manifest import ModuleManifest
from noxus_module_sdk.project import ProjectConfig, ProjectType
from noxus_module_sdk.release import ReleaseManifest
from noxus_module_sdk.resolver import DependencyResolver, ResolutionResult

__all__ = [
    "DependencyResolver",
    "ModuleManifest",
    "ProjectConfig",
    "ProjectType",
    "ReleaseManifest",
    "ResolutionResult",
    "SolutionBlueprint",
]
