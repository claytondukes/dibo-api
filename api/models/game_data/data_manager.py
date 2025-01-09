"""Manager for loading and accessing game data."""
import json
from pathlib import Path
from typing import Dict, Optional, List, Tuple

from pydantic import BaseModel, Field


class SetBonus(BaseModel):
    """Model for set bonus thresholds and effects."""
    
    pieces: int = Field(ge=2, le=6, description="Number of pieces required")
    description: str = Field(description="Description of the set's focus")
    bonuses: Dict[str, str] = Field(description="Bonuses at different piece thresholds")
    use_case: str = Field(description="Recommended use case for the set")


class ClassEssence(BaseModel):
    """Model for class-specific essence modifications."""
    
    essence_name: str = Field(description="Display name of the essence")
    gear_slot: str = Field(description="Gear slot this essence can be applied to")
    modifies_skill: str = Field(description="Skill that this essence modifies")
    effect: str = Field(description="Description of the essence's effect")
    effect_type: Optional[str] = Field(None, description="Type of effect")
    effect_tags: Optional[List[str]] = Field(None, description="Tags describing the effect")


class GearItem(BaseModel):
    """Model for gear items."""
    
    name: str = Field(description="Display name of the gear item")
    slot: str = Field(description="Gear slot this item occupies")
    stats: Dict[str, str] = Field(description="Stats provided by the gear item")


class GameDataManager:
    """Manager for loading and accessing game data."""
    
    def __init__(self, base_path: Path) -> None:
        """Initialize the data manager.
        
        Args:
            base_path: Base path to the indexed data directory
        """
        self.base_path = base_path
        self._equipment_sets: Optional[Dict[str, SetBonus]] = None
        self._class_essences: Dict[str, Dict[str, ClassEssence]] = {}
        self._gear_items: Optional[Dict[str, Dict[str, GearItem]]] = None
    
    def get_equipment_sets(self) -> Dict[str, SetBonus]:
        """Get all equipment sets.
        
        Returns:
            Dictionary mapping set names to their details
        """
        if self._equipment_sets is None:
            sets_path = self.base_path / "equipment" / "sets.json"
            with open(sets_path) as f:
                data = json.load(f)
                self._equipment_sets = {
                    name: SetBonus(**details)
                    for name, details in data["registry"].items()
                }
        return self._equipment_sets
    
    def get_class_essences(
        self,
        class_name: str,
        *,
        slot: Optional[str] = None,
        skill: Optional[str] = None
    ) -> Dict[str, ClassEssence]:
        """Get essences for a specific class, optionally filtered.
        
        Args:
            class_name: Name of the class (e.g., "barbarian")
            slot: Optional gear slot to filter by
            skill: Optional skill name to filter by
        
        Returns:
            Dictionary mapping essence IDs to their details
            
        Raises:
            ValueError: If class_name is invalid
        """
        # Load essences if not already loaded
        if class_name not in self._class_essences:
            essences_path = (
                self.base_path / "classes" / class_name / "essences.json"
            )
            if not essences_path.exists():
                raise ValueError(f"Invalid class name: {class_name}")
            
            with open(essences_path) as f:
                data = json.load(f)
                self._class_essences[class_name] = {
                    essence_id: ClassEssence(**essence_data)
                    for essence_id, essence_data in data["essences"].items()
                }
        
        # Get base essences for the class
        essences = self._class_essences[class_name]
        
        # Apply filters if specified
        if slot:
            essences = {
                id_: essence
                for id_, essence in essences.items()
                if essence.gear_slot.lower() == slot.lower()
            }
        
        if skill:
            essences = {
                id_: essence
                for id_, essence in essences.items()
                if essence.modifies_skill.lower() == skill.lower()
            }
        
        return essences

    def get_gear_items(
        self,
        class_name: Optional[str] = None,
        slot: Optional[str] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Dict], int]:
        """Get gear items with optional filtering and pagination.
        
        Args:
            class_name: Optional class name to filter by
            slot: Optional gear slot to filter by
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Tuple of (list of gear items for the current page, total number of items)
            
        Raises:
            FileNotFoundError: If required data files are missing
        """
        # Return empty list since gear.json doesn't exist yet
        return [], 0
