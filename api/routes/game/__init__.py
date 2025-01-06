"""
Game-related API routes.
"""

from fastapi import APIRouter

from .gems import router as gems_router

router = APIRouter(prefix="/game")
router.include_router(gems_router)

__all__ = ["router"]
