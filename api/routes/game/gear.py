"""API routes for gear-related endpoints."""
from typing import Annotated, List, Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from api.models.game_data.manager import GameDataManager
from api.models.game_data.schemas.gear import GearSlot


router = APIRouter(tags=["game"])


# Standard gear slots that are consistent across all classes
STANDARD_GEAR_SLOTS = {
    "primary": [
        "head",
        "chest",
        "shoulders",
        "legs",
        "main_hand_1",
        "off_hand_1",
        "main_hand_2",
        "off_hand_2"
    ],
    "set": [
        "neck",
        "waist",
        "feet",
        "hands",
        "ring_1",
        "ring_2",
        "bracer_1",
        "bracer_2"
    ]
}


class GearSlotsResponse(BaseModel):
    """Response model for gear slots endpoint."""
    slots: List[str] = Field(description="List of available gear slots")


class GearListResponse(BaseModel):
    """Response model for gear listing endpoint."""
    items: list[dict] = Field(description="List of gear items")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total: int = Field(description="Total number of items")


class EssenceResponse(BaseModel):
    """Response model for essence listing endpoint."""
    name: str = Field(description="Name of the essence")
    slot: str = Field(description="Gear slot this essence applies to")
    skill: str = Field(description="Skill modified by this essence")
    effect: str = Field(description="Effect description")
    effect_type: Optional[str] = Field(None, description="Type of effect")
    effect_tags: Optional[List[str]] = Field(None, description="Tags describing the effect")


class EssenceListResponse(BaseModel):
    """Response model for essence listing endpoint."""
    essences: List[EssenceResponse] = Field(description="List of essences")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total: int = Field(description="Total number of essences")


def get_data_manager(request: Request) -> GameDataManager:
    """Get the GameDataManager instance from app state."""
    return request.app.state.data_manager


@router.get("/gear/slots", response_model=GearSlotsResponse)
async def list_gear_slots(
    gear_type: Optional[Literal["primary", "set"]] = Query(
        None,
        alias="type",
        description="Filter by gear type (primary or set)"
    )
) -> GearSlotsResponse:
    """List available gear slots."""
    if gear_type:
        slots = STANDARD_GEAR_SLOTS.get(gear_type, [])
    else:
        slots = STANDARD_GEAR_SLOTS["primary"] + STANDARD_GEAR_SLOTS["set"]
    
    return GearSlotsResponse(slots=slots)


@router.get("/gear", response_model=GearListResponse)
async def list_gear(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)],
    class_name: Optional[str] = Query(None, alias="class"),
    slot: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    per_page: int = Query(20, gt=0, le=100)
) -> GearListResponse:
    """List available gear items with optional filtering."""
    # For now, return an empty list since gear is standardized
    # and specific items are determined by essences
    return GearListResponse(
        items=[],
        page=page,
        per_page=per_page,
        total=0
    )


@router.get("/gear/{class_name}/essences", response_model=EssenceListResponse)
async def list_class_essences(
    class_name: str,
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)],
    slot: Optional[str] = Query(None, description="Filter by gear slot"),
    skill: Optional[str] = Query(None, description="Filter by modified skill"),
    page: int = Query(1, gt=0, description="Page number"),
    per_page: int = Query(20, gt=0, le=100, description="Items per page")
) -> EssenceListResponse:
    """List available essences for a specific class."""
    try:
        essences_data = data_manager.get_class_essences(
            class_name=class_name,
            slot=slot,
            skill=skill
        )
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_essences = list(essences_data.items())[start_idx:end_idx]
        
        # Convert to response format
        essences = [
            EssenceResponse(
                name=essence.essence_name,
                slot=essence.gear_slot,
                skill=essence.modifies_skill,
                effect=essence.effect,
                effect_type=essence.effect_type,
                effect_tags=essence.effect_tags
            )
            for _, essence in paginated_essences
        ]
        
        return EssenceListResponse(
            essences=essences,
            page=page,
            per_page=per_page,
            total=len(essences_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
