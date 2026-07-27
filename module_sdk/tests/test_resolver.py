from __future__ import annotations

import pytest
from noxus_module_sdk.resolver import DependencyResolver, ResolutionError

from .test_manifest import manifest


def test_resolver_returns_deterministic_dependency_order() -> None:
    core = manifest("noxus_core")
    inventory = manifest("noxus_inventory", ["noxus_core>=1.0.0"])
    maintenance = manifest("noxus_maintenance", ["noxus_core>=1.0.0", "noxus_inventory>=1.0.0"])
    result = DependencyResolver([maintenance, inventory, core]).resolve(["noxus_maintenance"])
    assert [item.name for item in result.installation_order] == [
        "noxus_core",
        "noxus_inventory",
        "noxus_maintenance",
    ]


def test_resolver_reports_cycle_path() -> None:
    first = manifest("noxus_first", ["noxus_second>=1.0.0"])
    second = manifest("noxus_second", ["noxus_first>=1.0.0"])
    with pytest.raises(ResolutionError, match="noxus_first -> noxus_second -> noxus_first"):
        DependencyResolver([first, second]).resolve(["noxus_first"])


def test_resolver_reports_missing_dependency() -> None:
    value = manifest("noxus_maintenance", ["noxus_inventory>=1.0.0"])
    with pytest.raises(ResolutionError, match="requires noxus_inventory"):
        DependencyResolver([value]).resolve(["noxus_maintenance"])
