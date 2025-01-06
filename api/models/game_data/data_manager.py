"""Manager for loading and accessing game data."""
import json
from pathlib import Path
from typing import Dict, Optional

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
                if essence.gear_slot == slot
            }
        
        if skill:
            essences = {
                id_: essence
                for id_, essence in essences.items()
                if essence.modifies_skill == skill
            }
        
        return essences
