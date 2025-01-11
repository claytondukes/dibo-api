"""Build management service.

This module provides functionality for managing character builds, including
validation, storage, and retrieval using GitHub Gists as the storage backend.
"""

from typing import List

from fastapi import HTTPException
from pydantic import ValidationError

from ..models.game_data.schemas.builds.models import BuildConfig, BuildSummary
from ..models.game_data.manager import GameDataManager
from ..utils.gists import GistService


class BuildService:
    """Service for managing character builds."""

    def __init__(self, data_manager: GameDataManager, gist_service: GistService):
        """Initialize the build service.
        
        Args:
            data_manager: Game data manager for validating builds
            gist_service: Gist service for build storage
        """
        self._data_manager = data_manager
        self._gist_service = gist_service

    async def validate_build(self, build: BuildConfig) -> List[str]:
        """Validate a build configuration."""
        errors = []

        # Validate class type
        if not await self._data_manager.class_exists(build.class_type):
            errors.append(f"Invalid class type: {build.class_type}")

        # Validate equipment
        for slot, item_name in build.equipment.items():
            if not await self._data_manager.item_exists(item_name):
                errors.append(f"Invalid item '{item_name}' in slot {slot}")

        # Validate gems
        for socket, gem_name in build.gems.items():
            if not await self._data_manager.gem_exists(gem_name):
                errors.append(f"Invalid gem type: {gem_name}")

        return errors

    async def save_build(
        self, build: BuildConfig, description: str | None = None
    ) -> BuildSummary:
        """Save a build configuration to a gist.
        
        Args:
            build: Build configuration to save
            description: Optional gist description

        Returns:
            Summary of the saved build

        Raises:
            HTTPException: If build validation fails or gist creation fails
        """
        # Validate build
        errors = await self.validate_build(build)
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid build configuration",
                    "errors": errors
                }
            )

        # Create gist content using Pydantic's json serialization
        gist_content = {
            "build": build.model_dump_json(),
            "format_version": "1.0.0"
        }

        # Save to gist
        try:
            gist = await self._gist_service.create_gist(
                files={
                    "build.json": {
                        "content": gist_content
                    }
                },
                description=description or f"{build.name} - {build.class_type} Build",
                public=True
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to save build: {str(e)}"
            )

        # Create summary
        return BuildSummary(
            id=gist.id,
            version=build.version,
            name=build.name,
            class_type=build.class_type,
            tags=build.tags,
            created_at=gist.created_at,
            updated_at=gist.updated_at
        )

    async def get_build(self, build_id: str) -> BuildConfig:
        """Retrieve a build configuration from a gist.
        
        Args:
            build_id: ID of the gist containing the build

        Returns:
            The build configuration

        Raises:
            HTTPException: If build not found or invalid format
        """
        try:
            gist = await self._gist_service.get_gist(build_id)
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Build not found: {str(e)}"
            )

        # Find build.json file
        build_file = next(
            (f for f in gist.files if f.filename == "build.json"),
            None
        )
        if not build_file:
            raise HTTPException(
                status_code=400,
                detail="Invalid build format: missing build.json"
            )

        # Parse build data
        try:
            content = BuildConfig.model_validate_json(build_file.content)
            if "format_version" not in content or "build" not in content:
                raise ValueError("Invalid build format")
            return BuildConfig.model_validate(content["build"])
        except ValidationError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid build format: {str(e)}"
            )

    async def update_build(
        self, build_id: str, build: BuildConfig, description: str | None = None
    ) -> BuildSummary:
        """Update an existing build configuration.
        
        Args:
            build_id: ID of the gist to update
            build: New build configuration
            description: Optional new description

        Returns:
            Updated build summary

        Raises:
            HTTPException: If build not found, validation fails, or update fails
        """
        # Validate build exists
        try:
            await self._gist_service.get_gist(build_id)
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Build not found: {str(e)}"
            )

        # Validate new build
        errors = await self.validate_build(build)
        if errors:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid build configuration",
                    "errors": errors
                }
            )

        # Update gist
        gist_content = {
            "build": build.model_dump_json(),
            "format_version": "1.0.0"
        }

        try:
            gist = await self._gist_service.update_gist(
                gist_id=build_id,
                files={
                    "build.json": {
                        "content": gist_content
                    }
                },
                description=description
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update build: {str(e)}"
            )

        # Return updated summary
        return BuildSummary(
            id=gist.id,
            version=build.version,
            name=build.name,
            class_type=build.class_type,
            tags=build.tags,
            created_at=gist.created_at,
            updated_at=gist.updated_at
        )
