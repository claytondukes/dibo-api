"""Main application module."""

import logging
import contextlib
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.routes import router as auth_router
from .builds.routes import router as build_router
from .core.config import get_settings


settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application lifespan events."""
    # Startup
    logger.info(
        "Starting %s in %s mode",
        settings.PROJECT_NAME,
        settings.ENVIRONMENT
    )
    yield
    # Shutdown
    logger.info("Shutting down %s", settings.PROJECT_NAME)


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Diablo Immortal Build Optimizer API",
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(build_router, prefix=settings.API_V1_STR)


def main() -> None:
    """Run application with uvicorn."""
    logger.info("Starting uvicorn server")
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
