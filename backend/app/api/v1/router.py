"""API v1 root router.

All v1 endpoints are registered here and mounted at ``/api/v1`` by
:mod:`app.main`. When a breaking change requires a v2 surface, a new
``app/api/v2/router.py`` is created and mounted alongside this one —
v1 remains fully intact.
"""

from fastapi import APIRouter

router = APIRouter()

# Endpoint routers are imported and included here as they are built.
# Example (uncomment when ready):
# from app.api.v1.endpoints import users, events, auth
# router.include_router(users.router, prefix="/users", tags=["users"])
# router.include_router(events.router, prefix="/events", tags=["events"])
# router.include_router(auth.router, prefix="/auth", tags=["auth"])


@router.get("/ping", tags=["ops"], summary="API v1 liveness")
async def ping() -> dict[str, str]:
    """Confirm the v1 API is reachable.

    Returns:
        A simple acknowledgement payload.
    """
    return {"message": "pong"}
