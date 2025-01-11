"""API routes for equipment set-related operations."""

from typing import Annotated, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from api.models.game_data.manager import GameDataManager


router = APIRouter(tags=["game"])


class SetBonus(BaseModel):
    """Model for set bonus information."""
    
    description: str = Field(description="Description of the bonus effect")


class SetInfo(BaseModel):
    """Model for set information."""
    
    name: str = Field(description="Name of the set")
    pieces: int = Field(description="Number of pieces in the set", ge=2, le=6)
    description: str = Field(description="Description of the set")
    bonuses: Dict[str, str] = Field(description="Set bonuses at different piece thresholds")
    use_case: str = Field(description="Recommended use case for the set")


class SetListResponse(BaseModel):
    """Response model for set listing endpoint."""
    
    sets: List[SetInfo] = Field(description="List of equipment sets")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total: int = Field(description="Total number of sets")


class SetBonusesResponse(BaseModel):
    """Response model for active set bonuses endpoint."""
    
    active_bonuses: Dict[str, List[str]] = Field(
        description="Active bonuses for each equipped set"
    )
    total_sets: int = Field(description="Total number of active sets")


def get_data_manager(request: Request) -> GameDataManager:
    """Get the GameDataManager instance from app state."""
    return request.app.state.data_manager


@router.get("/sets/bonuses", response_model=SetBonusesResponse)
async def get_active_set_bonuses(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)],
    equipped_sets: Annotated[str, Query(
        ..., 
        description="JSON string of set names and number of pieces equipped, e.g., {'SetName': 4}",
        example='{"SetName": 4}',
        openapi_extra={"type": "string", "format": "json"}
    )]
) -> SetBonusesResponse:
    """Get active set bonuses based on equipped set pieces.
    
    Args:
        data_manager: Game data manager instance
        equipped_sets: JSON string mapping set names to number of equipped pieces
    
    Returns:
        Active set bonuses for each equipped set
        
    Raises:
        HTTPException: If any sets are not found or invalid piece counts
    """
    try:
        # Parse JSON string into Dict[str, int]
        import json
        sets_dict = json.loads(equipped_sets)
        if not isinstance(sets_dict, dict) or not all(isinstance(k, str) and isinstance(v, int) for k, v in sets_dict.items()):
            raise ValueError("Invalid format: expected Dict[str, int]")

        # Get all sets data using the convenience method
        sets_data = await data_manager.get_equipment_sets()
        
        active_bonuses = {}
        for set_name, pieces in sets_dict.items():
            set_data = sets_data.get(set_name)
            if not set_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Set '{set_name}' not found"
                )
                
            if pieces > set_data["pieces"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid piece count for set '{set_name}'"
                )
                
            # Calculate active bonuses
            set_bonuses = []
            for threshold in sorted(map(int, set_data["bonuses"].keys())):
                if pieces >= threshold:
                    set_bonuses.append(set_data["bonuses"][str(threshold)])
                    
            if set_bonuses:
                active_bonuses[set_name] = set_bonuses
                
        return SetBonusesResponse(
            active_bonuses=active_bonuses,
            total_sets=len(active_bonuses)
        )
        
    except Exception as e:
        logger.error(f"Error getting set bonuses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/sets", response_model=SetListResponse)
async def list_sets(
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)],
    pieces: Optional[int] = Query(
        None,
        ge=2,
        le=6,
        description="Filter by number of pieces (2, 4, or 6)"
    ),
    page: int = Query(1, gt=0, description="Page number"),
    per_page: int = Query(20, gt=0, le=100, description="Items per page")
) -> SetListResponse:
    """List all available equipment sets with optional filtering.
    
    Args:
        data_manager: Game data manager instance
        pieces: Optional filter by number of pieces
        page: Page number (1-based)
        per_page: Items per page (max 100)
    
    Returns:
        Paginated list of equipment sets
        
    Raises:
        HTTPException: If invalid parameters are provided
    """
    try:
        # Get all sets data using the convenience method
        sets_data = await data_manager.get_equipment_sets()
        
        # Filter by pieces if specified
        if pieces:
            sets_data = {
                name: data
                for name, data in sets_data.items()
                if data["pieces"] == pieces
            }
        
        # Calculate pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_sets = list(sets_data.items())[start_idx:end_idx]
        
        # Convert to response format
        sets = [
            SetInfo(
                name=name,
                pieces=data["pieces"],
                description=data["description"],
                bonuses=data["bonuses"],
                use_case=data["use_case"]
            )
            for name, data in paginated_sets
        ]
        
        return SetListResponse(
            sets=sets,
            page=page,
            per_page=per_page,
            total=len(sets_data)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/sets/{set_name}", response_model=SetInfo)
async def get_set_details(
    set_name: str,
    data_manager: Annotated[GameDataManager, Depends(get_data_manager)]
) -> SetInfo:
    """Get detailed information about a specific equipment set.
    
    Args:
        set_name: Name of the set to retrieve
        data_manager: Game data manager instance
    
    Returns:
        Detailed set information
        
    Raises:
        HTTPException: If set is not found
    """
    try:
        # Get all sets data using the convenience method
        sets_data = await data_manager.get_equipment_sets()
        set_data = sets_data.get(set_name)
        if not set_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Set '{set_name}' not found"
            )
            
        return SetInfo(
            name=set_name,
            pieces=set_data["pieces"],
            description=set_data["description"],
            bonuses=set_data["bonuses"],
            use_case=set_data["use_case"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
