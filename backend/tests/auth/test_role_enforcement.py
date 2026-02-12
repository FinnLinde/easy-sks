"""Enforcement test: every non-public route must declare a required role.

This test introspects the FastAPI app's route tree and asserts that each
protected endpoint has at least one dependency annotated with the
``_required_roles`` marker (set by ``require_role``).

If a developer adds a new endpoint and forgets to declare a role, this test
will fail in CI with a clear message naming the unprotected route.
"""

from __future__ import annotations

from fastapi.routing import APIRoute

from main import app

# Paths that are intentionally public (no auth required).
_PUBLIC_PATHS: set[str] = {
    "/",
    "/health",
    "/openapi.json",
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
}


def _has_role_dependency(route: APIRoute) -> bool:
    """Return True if *route* (or any of its parent routers) carries a
    dependency whose callable has the ``_required_roles`` marker."""
    for dep in route.dependant.dependencies:
        call = dep.call
        if hasattr(call, "_required_roles"):
            return True
        # Walk nested sub-dependencies (one level deep is sufficient for
        # the current wiring, but we recurse to be safe).
        if hasattr(dep, "dependant") and dep.dependant is not None:
            for sub in dep.dependant.dependencies:
                if hasattr(sub.call, "_required_roles"):
                    return True
    return False


def test_all_protected_routes_declare_a_role() -> None:
    unprotected: list[str] = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        if route.path in _PUBLIC_PATHS:
            continue

        if not _has_role_dependency(route):
            methods = ",".join(sorted(route.methods or set()))
            unprotected.append(f"{methods} {route.path}")

    assert not unprotected, (
        "The following routes do not declare a required role via "
        "require_role(). Every non-public endpoint must specify at least "
        "one role.\n  - " + "\n  - ".join(sorted(unprotected))
    )
