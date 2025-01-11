"""
Game-related API routes.
"""

from fastapi import APIRouter

from .gems import router as gems_router
from .gear import router as gear_router
from .sets import router as sets_router
from .classes import router as classes_router
from .stats import router as stats_router
from .constraints import router as constraints_router
from .synergies import router as synergies_router
from .modes import router as modes_router
from ...builds.routes import router as builds_router

router = APIRouter(prefix="/game", tags=["game"])

# Include routers in order of specificity
router.include_router(sets_router)  # Include sets router first for /sets/bonuses
router.include_router(gems_router)
router.include_router(gear_router)
router.include_router(classes_router)
router.include_router(stats_router)
router.include_router(constraints_router)
router.include_router(synergies_router)
router.include_router(modes_router)
router.include_router(builds_router)

__all__ = ["router"]
