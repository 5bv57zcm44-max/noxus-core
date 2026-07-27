def after_install() -> None:
    from noxus_core.module_runtime import ensure_module

    from noxus_maintenance.schema import ROLES, SCHEMAS

    ensure_module(SCHEMAS, ROLES)
