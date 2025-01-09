"""API routes for class-related operations."""

import json
from typing import Annotated, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
import logging

from api.models.game_data.data_manager import GameDataManager
from api.models.game_data.schemas.classes import ClassInfo, ClassSkill


logger = logging.getLogger(__name__)

router = APIRouter(tags=["game"])


class ClassListResponse(BaseModel):
    """Response model for class listing endpoint."""
    classes: List[str] = Field(description="List of available class names")


def get_data_manager(request: Request) -> GameDataManager:
    """Get the GameDataManager instance from app state."""
    return request.app.state.data_manager


@router.get("/classes", response_model=ClassListResponse)
async def list_classes(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> ClassListResponse:
    """List all available character classes.

    Args:
        data_manager: Game data manager instance

    Returns:
        List of class names

    Raises:
        HTTPException: If classes data cannot be loaded
    """
    try:
        classes_dir = data_manager.base_path / "classes"
        if not classes_dir.exists():
            raise FileNotFoundError("Classes directory not found")
        
        # Get class names from directory names
        class_names = [d.name for d in classes_dir.iterdir() if d.is_dir()]
        return ClassListResponse(classes=class_names)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/classes/{class_name}", response_model=ClassInfo)
async def get_class_details(
    class_name: str,
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> ClassInfo:
    """Get detailed information about a specific class.

    Args:
        class_name: Name of the class to retrieve
        data_manager: Game data manager instance

    Returns:
        Detailed class information

    Raises:
        HTTPException: If class is not found or data cannot be loaded
    """
    try:
        class_dir = data_manager.base_path / "classes" / class_name
        if not class_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class not found: {class_name}"
            )
            
        # Load class data from JSON files
        with open(class_dir / "base_skills.json") as f:
            skills_data = json.load(f)
            
        # Create class info
        class_data = {
            "name": class_name,
            "description": skills_data.get("description", ""),
            "primary_resource": skills_data.get("resource", ""),
            "skills": skills_data.get("skills", {}),
            "mechanics": skills_data.get("mechanics", []),
            "recommended_playstyle": skills_data.get("playstyle", None)
        }
            
        return ClassInfo(**class_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting class details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
