"""
Game-related API routes.
"""

from fastapi import APIRouter

from .gems import router as gems_router
from .gear import router as gear_router
from ...builds.routes import router as builds_router

router = APIRouter(prefix="/game")
router.include_router(gems_router)
router.include_router(gear_router)
router.include_router(builds_router)

__all__ = ["router"]
