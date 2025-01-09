"""Main application module."""

import logging
import contextlib
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth.routes import router as auth_router
from .core.config import Settings, get_settings
from .routes import router as api_router
from .models.game_data.data_manager import GameDataManager


settings = get_settings()

# Configure logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
    
    # Initialize GameDataManager
    base_path = settings.PROJECT_ROOT / "data" / "indexed"
    logger.info(f"Initializing GameDataManager with base_path: {base_path}")
    app.state.data_manager = GameDataManager(base_path=base_path)
    
    yield
    
    # Shutdown
    logger.info("Shutting down %s", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    """Create FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Diablo Immortal Build Optimizer API",
        version=settings.VERSION,
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )

    # Set CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.ALLOW_CREDENTIALS,
        allow_methods=settings.ALLOW_METHODS.split(",") if settings.ALLOW_METHODS != "*" else ["*"],
        allow_headers=settings.ALLOW_HEADERS.split(",") if settings.ALLOW_HEADERS != "*" else ["*"],
    )

    # Add routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app


app = create_app()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs",
        "redoc": f"{settings.API_V1_STR}/redoc"
    }


def main():
    """Run application with uvicorn."""
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
