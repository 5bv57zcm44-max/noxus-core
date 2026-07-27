from __future__ import annotations

from typing import Any, Literal

from pydantic import ValidationError

from noxus_core.contracts import BlueprintRequest, ResolveRequest


def validate_configuration(
    kind: Literal["blueprint", "resolution"], value: dict[str, Any]
) -> dict[str, Any]:
    model = BlueprintRequest if kind == "blueprint" else ResolveRequest
    try:
        validated = model.model_validate(value)
    except ValidationError as exc:
        return {"valid": False, "errors": exc.errors(include_url=False)}
    if isinstance(validated, BlueprintRequest):
        from noxus_core.services.blueprints import verify_blueprint

        try:
            verify_blueprint(validated)
        except ValueError as exc:
            return {"valid": False, "errors": [{"msg": str(exc)}]}
    return {"valid": True, "normalized": validated.model_dump(mode="json"), "errors": []}
