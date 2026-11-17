from enum import StrEnum

class Role(StrEnum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    TECHNICIAN = "technician"
    VIEWER = "viewer"

VIEW = {
    "dashboard.view",
    "system.view",
    "issue.view",
    "release.view",
}

TECH = VIEW | {
    "issue.create",
    "issue.edit",
    "issue.comment",
}

ENGINEER = TECH | {
    "system.create",
    "system.edit",
    "system.detele",
    "issue.detele",
    "relese.edit",
}

ADMIN = ENGINEER | {
    "user.manage",
    "lookup.manage",
    "trash.restore",
    "audit.view",
}

ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.VIEWER: frozenset(VIEW),
    Role.TECHNICIAN: frozenset(TECH),
    Role.ENGINEER: frozenset(ENGINEER),
    Role.ADMIN: frozenset(ADMIN),
}

def has_permission(role: str | None, permission: str) -> bool:
    if not role:
        return False
    try:
        return permission in ROLE_PERMISSIONS[Role(role)]
    except:
        return False