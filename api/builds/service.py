"""Build generation service."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from fastapi import HTTPException, status
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..models.game_data.manager import GameDataManager
from .models import (
    BuildFocus,
    BuildRecommendation,
    BuildResponse,
    BuildStats,
    BuildType,
    Gem,
    Skill,
    Equipment
)


logger = logging.getLogger(__name__)


class ScoreWeights(BaseModel):
    """Score weights for build type configuration."""
    base_type_match: float = Field(description="Base type match weight")
    second_type_match: float = Field(description="Secondary type match weight")
    term_match: float = Field(description="Term match weight")
    cooldown: Optional[Dict[str, Union[float, int]]] = Field(
        default=None,
        description="Optional cooldown configuration"
    )
    utility_modifier: float = Field(description="Utility modifier weight")


class BuildTypeConfig(BaseModel):
    """Build type configuration."""
    terms: List[str] = Field(description="List of terms for matching")
    score_weights: ScoreWeights = Field(description="Score weights configuration")


class BuildService:
    """Service for generating and analyzing builds."""
    
    # Required data files that must exist
    REQUIRED_FILES = {
        # Core data files
        "build_types": "build_types.json",
        "stats": "gems/stat_boosts.json",
        "constraints": "constraints.json",
        "synergies": "synergies.json",
        
        # Gem-related files
        "gems/skillmap": "gems/gem_skillmap.json",
        "gems/data": "gems/gems.json",
        "gems/stat_boosts": "gems/stat_boosts.json",
        "gems/synergies": "gems/synergies.json",
        
        # Equipment data
        "sets": "sets.json",
        
        # Class-specific data
        "classes/barbarian/essences": "classes/barbarian/essences.json",
    }
    
    # Static gear slots (right side of character)
    GEAR_SLOTS = {
        "HEAD": "Head",           # Helm slot
        "CHEST": "Chest",        # Torso armor
        "SHOULDERS": "Shoulders", # Shoulder armor
        "LEGS": "Legs",          # Leg armor
        "MAIN_HAND_1": "Main Hand (Set 1)",  # Primary weapon set 1
        "OFF_HAND_1": "Off-Hand (Set 1)",    # Off-hand weapon/shield set 1
        "MAIN_HAND_2": "Main Hand (Set 2)",  # Primary weapon set 2
        "OFF_HAND_2": "Off-Hand (Set 2)"     # Off-hand weapon/shield set 2
    }
    
    # Static set slots (left side of character)
    SET_SLOTS = {
        "NECK": "Neck",       # Necklace slot
        "WAIST": "Waist",     # Belt slot
        "HANDS": "Hands",     # Gloves slot
        "FEET": "Feet",       # Boot slot
        "RING_1": "Ring 1",   # First ring slot
        "RING_2": "Ring 2",   # Second ring slot
        "BRACER_1": "Bracer 1", # First bracer slot
        "BRACER_2": "Bracer 2"  # Second bracer slot
    }
    
    # Supported character classes
    CHARACTER_CLASSES: Set[str] = set()  
    
    def __init__(self, data_dir: Optional[Path] = None) -> None:
        """Initialize the build service.
        
        Note: This should not be called directly. Use create() instead.
        
        Args:
            data_dir: Optional path to data directory. If not provided,
                     uses the default from settings.
        """
        self.settings = get_settings()
        self.data_dir = data_dir or self.settings.DATA_DIR
        
        if not self.data_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data directory not found: {self.data_dir}"
            )
            
        self.data_manager = GameDataManager(self.data_dir)
        self._load_data()
        
        # Dynamically detect available character classes
        self.CHARACTER_CLASSES = self._get_available_classes()
        
    @classmethod
    async def create(cls, data_dir: Optional[Path] = None) -> 'BuildService':
        """Create and initialize a BuildService instance.
        
        Args:
            data_dir: Optional path to data directory. If not provided,
                     uses the default from settings.
        
        Returns:
            Initialized BuildService instance
            
        Raises:
            HTTPException: If initialization fails
        """
        instance = cls(data_dir)
        await instance.initialize()
        return instance

    async def initialize(self) -> None:
        """Initialize the build service by loading required data."""
        try:
            # Load core data
            self.build_types = await self.data_manager.get_data("build_types")
            self.constraints = await self.data_manager.get_data("constraints")
            
            # Load set data
            self.set_bonuses = await self.data_manager.get_data("sets")
            
            # Load gem data
            self.gem_data = await self.data_manager.get_data("gems/data")
            self.gem_skillmap = await self.data_manager.get_data("gems/skillmap")
            self.stat_boosts = await self.data_manager.get_data("gems/stat_boosts")
            self.synergies = await self.data_manager.get_data("gems/synergies")
            
            # Load class-specific data
            self.class_data = {}
            self.class_constraints = {}
            for class_name in self.CHARACTER_CLASSES:
                self.class_data[class_name] = {
                    "essences": self._load_json_file(f"classes/{class_name}/essences.json"),
                    "base_skills": self._load_json_file(f"classes/{class_name}/base_skills.json")
                }
                self.class_constraints[class_name] = self._load_json_file(
                    f"classes/{class_name}/constraints.json"
                )
            
            # Validate loaded data
            self._validate_data_structure()
            
        except Exception as e:
            logger.error(f"Failed to initialize data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize data: {str(e)}"
            )
            
    def _load_json_file(self, relative_path: str) -> Dict:
        """Load a JSON file from the data directory.
        
        Args:
            relative_path: Path relative to data directory
            
        Returns:
            Loaded JSON data
            
        Raises:
            HTTPException: If file not found or invalid
        """
        try:
            file_path = self.data_dir / relative_path
            if not file_path.exists():
                raise FileNotFoundError(f"Required data file not found: {file_path}")
                
            with open(file_path, "r") as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading {relative_path}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load {relative_path}: {str(e)}"
            )
    
    def _validate_data_structure(self) -> None:
        """Validate the structure of loaded data.
        
        Raises:
            HTTPException: If data structure is invalid.
        """
        # Validate synergies structure
        if not isinstance(self.synergies, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Synergies must be a dictionary"
            )
        
        required_synergy_keys = {"metadata", "synergies"}
        if not all(key in self.synergies for key in required_synergy_keys):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing required keys in synergies data"
            )
        
        # Validate constraints structure
        required_constraints = {"gem_slots", "essence_slots"}
        if not all(key in self.constraints for key in required_constraints):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing required constraint categories"
            )
        
        # Validate stats structure
        required_stats_keys = {"metadata", "stats"}
        if not all(key in self.stat_boosts for key in required_stats_keys):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing required keys in stats data"
            )
        
        # Validate equipment data structure
        required_equipment_keys = {"metadata", "gear", "sets"}  
        if not all(key in self.set_bonuses for key in required_equipment_keys):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing required keys in equipment data"
            )
        
        # Validate class data structure
        for class_name, data in self.class_data.items():
            # Validate base skills
            required_skill_keys = {"metadata", "skills"}
            if not all(key in data["base_skills"] for key in required_skill_keys):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Missing required keys in base skills for class {class_name}"
                )
            
            # Validate essences
            required_essence_keys = {"metadata", "essences", "indexes"}
            if not all(key in data["essences"] for key in required_essence_keys):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Missing required essence keys for class {class_name}"
                )

    async def generate_build(
        self,
        build_type: BuildType,
        focus: BuildFocus,
        character_class: str,
        inventory: Optional[Dict] = None
    ) -> BuildResponse:
        """Generate a build based on specified criteria.
        
        Args:
            build_type: Type of build to generate (PVE, PVP, etc.)
            focus: Primary focus of the build (DPS, survival, etc.)
            character_class: Character class
            inventory: Optional user inventory to consider
        
        Returns:
            BuildResponse containing the generated build
        """
        try:
            # Validate character class
            if character_class not in self.CHARACTER_CLASSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid character class: {character_class}"
                )
            
            # Select gems based on build type and focus
            selected_gems = await self._select_gems(build_type, focus, inventory)
            
            # Select skills that synergize with the build
            selected_skills = await self._select_skills(
                build_type,
                focus,
                selected_gems,
                inventory,
                character_class
            )
            
            # Select equipment that complements the build
            selected_equipment = await self._select_equipment(
                build_type,
                focus,
                selected_gems,
                selected_skills,
                inventory,
                character_class
            )
            
            # Generate recommendations for improvement
            recommendations = await self._generate_recommendations(
                build_type,
                focus,
                selected_gems,
                selected_skills,
                selected_equipment,
                inventory,
                character_class
            )
            
            # Find synergies between selected items
            synergies = await self._find_synergies(
                selected_gems,
                selected_skills,
                selected_equipment
            )
            
            return BuildResponse(
                build_type=build_type,
                focus=focus,
                character_class=character_class,
                gems=selected_gems,
                skills=selected_skills,
                equipment=selected_equipment,
                recommendations=recommendations,
                synergies=synergies
            )
            
        except Exception as e:
            logger.error(f"Error generating build: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate build: {str(e)}"
            )
    
    def _validate_inventory(self, inventory: Dict) -> None:
        """Validate inventory format and contents.
        
        Args:
            inventory: User's inventory to validate
            
        Raises:
            HTTPException: If inventory format is invalid
        """
        if not isinstance(inventory, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inventory must be a dictionary"
            )
        
        for item_name, item_data in inventory.items():
            if not isinstance(item_data, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid data for item: {item_name}"
                )
            
            if "owned_rank" not in item_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing owned_rank for item: {item_name}"
                )
            
            if not isinstance(item_data["owned_rank"], (int, type(None))):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid owned_rank for item: {item_name}"
                )
    
    async def _select_gems(
        self,
        build_type: BuildType,
        focus: BuildFocus,
        inventory: Optional[Dict] = None
    ) -> List[Gem]:
        """Select gems based on build criteria.
        
        Args:
            build_type: Type of build
            focus: Build focus
            inventory: Optional user inventory
            
        Returns:
            List of selected gems
        """
        # Get gem slot constraints
        slot_constraints = self.constraints["gem_slots"]
        total_slots = slot_constraints["total_required"]
        
        # Initialize selected gems
        selected_gems = []
        used_gems = set()  # Track used gems to avoid duplicates
        
        # Get gems that match the build focus
        focus_gems = []
        for category, data in self.synergies.items():
            if self._matches_focus(category, focus):
                focus_gems.extend(data["gems"])
        
        # Sort gems by effectiveness for the build type
        focus_gems.sort(
            key=lambda g: self._calculate_gem_score(g, build_type, focus),
            reverse=True
        )
        
        # Select primary gems first
        for gem in focus_gems:
            if len(selected_gems) >= total_slots:
                break
                
            if gem in used_gems:
                continue
            
            # Check if gem is in inventory
            if inventory and gem in inventory:
                owned_rank = inventory[gem]["owned_rank"]
                quality = inventory[gem].get("quality")
            else:
                # Get rank from gem data
                gem_data = None
                for skill_gems in self.gem_data["effects"]["gems_by_skill"].values():
                    for g in skill_gems:
                        if g["Name"] == gem:
                            gem_data = g
                            break
                    if gem_data:
                        break
                
                if not gem_data:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Gem data not found: {gem}"
                    )
                
                owned_rank = int(gem_data["Rank"])
                quality = None
            
            # Find best aux gem for this primary gem
            aux_gem = self._select_aux_gem(
                primary_gem=gem,
                build_type=build_type,
                focus=focus,
                inventory=inventory,
                used_gems=used_gems
            )
            
            selected_gems.append(Gem(
                name=gem,
                rank=owned_rank,
                quality=quality,
                aux_gem=aux_gem
            ))
            
            # Mark both primary and aux gems as used
            used_gems.add(gem)
            if aux_gem:
                used_gems.add(aux_gem)
        
        return selected_gems
    
    def _select_aux_gem(
        self,
        primary_gem: str,
        build_type: BuildType,
        focus: BuildFocus,
        inventory: Optional[Dict],
        used_gems: Set[str]
    ) -> Optional[str]:
        """Select an aux gem for a primary gem.
        
        Args:
            primary_gem: Name of the primary gem
            build_type: Type of build
            focus: Build focus
            inventory: Optional user inventory
            used_gems: Set of already used gems
            
        Returns:
            Name of selected aux gem or None
        """
        # Get primary gem's star rating
        try:
            progression_data = self.gem_data["gems"][primary_gem]
            primary_star_rating = progression_data.get("star_rating")
            if not primary_star_rating:
                return None
        except (KeyError, AttributeError):
            return None
        
        # Get all gems with matching star rating
        candidates = []
        for gem_name, data in self.gem_data["gems"].items():
            if (
                gem_name != primary_gem
                and gem_name not in used_gems
                and data.get("star_rating") == primary_star_rating
            ):
                candidates.append(gem_name)
        
        if not candidates:
            return None
        
        # Calculate aux scores
        aux_scores = []
        for gem_name in candidates:
            # Calculate base score
            base_score = self._calculate_gem_score(gem_name, build_type, focus)
            
            # Adjust score based on rank 1 effect value
            try:
                rank_1_value = self.gem_data["stat_boosts"][gem_name]["rank_1"]
                rank_1_ratio = rank_1_value / 100.0
            except (KeyError, AttributeError):
                rank_1_ratio = 0.5
            
            # Final score is weighted towards rank 1 effectiveness
            final_score = (base_score * 0.4) + (rank_1_ratio * 0.6)
            aux_scores.append((gem_name, final_score))
        
        # Sort by score and return best option
        aux_scores.sort(key=lambda x: x[1], reverse=True)
        return aux_scores[0][0] if aux_scores else None
    
    async def _select_skills(
        self,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        inventory: Optional[Dict] = None,
        character_class: str = "barbarian"
    ) -> List[Skill]:
        """Select skills that synergize with the build.
        
        Args:
            build_type: Type of build
            focus: Build focus
            selected_gems: Previously selected gems
            inventory: Optional user inventory
            character_class: Character class
            
        Returns:
            List of selected skills
            
        Raises:
            HTTPException: If unable to select valid skills
        """
        # Get available skills and weapons from constraints
        class_constraints = self.class_constraints[character_class]
        available_skills = class_constraints["skill_slots"]["available_skills"]
        available_weapons = class_constraints["weapon_slots"]["available_weapons"]
        
        if not available_weapons:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No weapon skills available"
            )
            
        # Get build type requirements
        build_constraints = self.constraints["build_types"][build_type.value.lower()]
        build_required_categories = build_constraints.get("required_categories", {})
        
        # Get skill registry
        skill_registry = self.class_data[character_class]["base_skills"]["registry"]
        
        # First check if we can meet build type requirements with available skills
        available_categories = {}
        for skill in available_skills + available_weapons:
            skill_data = skill_registry[skill]
            for category in skill_data.get("categories", []):
                available_categories[category] = available_categories.get(category, 0) + 1
                
        # Verify build type requirements can be met
        for category, count in build_required_categories.items():
            if available_categories.get(category, 0) < count:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Required skill categories not met for build type {build_type.value}. Category {category} needs {count}, but only {available_categories.get(category, 0)} available"
                )
        
        # Get skills that match focus and have gem synergies
        skill_scores = {}
        for skill in available_skills + available_weapons:
            # Calculate base score from focus match
            base_score = self._calculate_skill_score(skill, build_type, focus, selected_gems)
            
            # Add bonus for gem synergies
            gem_synergy_bonus = 0
            for gem in selected_gems:
                gem_categories = self._get_gem_categories(gem.name)
                skill_categories = skill_registry[skill].get("categories", [])
                matching_categories = set(gem_categories) & set(skill_categories)
                if matching_categories:
                    gem_synergy_bonus += 0.2 * len(matching_categories)
            
            # Add bonus for essence availability
            essence_data = self.class_data[character_class]["essences"]
            skill_essences = essence_data.get("indexes", {}).get("by_skill", {}).get(skill, [])
            if skill_essences:
                best_essence_score = 0
                for essence_slug in skill_essences[:10]:  # Limit essence search
                    essence = essence_data["essences"].get(essence_slug)
                    if essence:
                        score = self._calculate_essence_score(essence, build_type, focus, selected_gems)
                        best_essence_score = max(best_essence_score, score)
                base_score += best_essence_score * 0.3  # Weight essence contribution
            
            final_score = base_score + gem_synergy_bonus
            skill_scores[skill] = final_score
        
        # Sort skills by score
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)
        
        # First select a weapon skill with highest score
        weapon_skill = None
        for skill, _ in sorted_skills:
            if skill in available_weapons:
                weapon_skill = skill
                break
                
        if not weapon_skill:
            # If no weapon skill found in synergies, take first available
            weapon_skill = available_weapons[0]
            
        selected_skills = [Skill(name=weapon_skill, essence=None)]
        used_skills = {weapon_skill}
        
        # Then select secondary skills prioritizing synergies and essences
        essence_data = self.class_data[character_class]["essences"]
        secondary_skills = []
        
        for skill, _ in sorted_skills:
            if skill in used_skills:
                continue
                
            # Find best essence for this skill
            best_essence = None
            best_score = -1
            
            # Get essences for this skill
            skill_essences = essence_data.get("indexes", {}).get("by_skill", {}).get(skill, [])
            
            for essence_slug in skill_essences[:10]:  # Limit essence search
                essence = essence_data["essences"].get(essence_slug)
                if not essence:
                    continue
                    
                score = self._calculate_essence_score(essence, build_type, focus, selected_gems)
                if score > best_score:
                    best_score = score
                    best_essence = essence
                    
            secondary_skills.append(Skill(
                name=skill,
                essence=best_essence["essence_name"] if best_essence else None
            ))
            used_skills.add(skill)
            
            if len(secondary_skills) >= 4:
                break
                
        # Add secondary skills
        selected_skills.extend(secondary_skills)
        
        # If we still need more skills, add from available_skills
        remaining_slots = 5 - len(selected_skills)
        if remaining_slots > 0:
            for skill, _ in sorted_skills:
                if skill not in used_skills:
                    selected_skills.append(Skill(name=skill, essence=None))
                    used_skills.add(skill)
                    remaining_slots -= 1
                    if remaining_slots == 0:
                        break
                        
        # Validate final selection
        skill_names = [s.name for s in selected_skills]
        if not self._validate_skill_selection(skill_names, character_class, build_type):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to create valid skill selection"
            )
            
        return selected_skills
    
    def _validate_skill_selection(
        self,
        selected_skills: List[str],
        character_class: str,
        build_type: BuildType = None
    ) -> bool:
        """Validate skill selection against constraints.
        
        Args:
            selected_skills: List of selected skills
            character_class: Character class
            build_type: Optional build type for additional validation
            
        Returns:
            True if valid, False otherwise
            
        Raises:
            HTTPException: If validation fails with specific reason
        """
        try:
            # Get class constraints and skill data
            class_constraints = self.class_constraints[character_class]
            skill_registry = self.class_data[character_class]["base_skills"]["registry"]
            
            # Check if all selected skills exist in registry
            for skill in selected_skills:
                if skill not in skill_registry:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Selected skill {skill} not found in registry"
                    )
                    
            # Get categories for selected skills
            skill_categories = {}
            for skill in selected_skills:
                skill_data = skill_registry[skill]
                categories = skill_data.get("categories", [])
                for category in categories:
                    skill_categories[category] = skill_categories.get(category, 0) + 1
                    
            # Check build type specific requirements first
            if build_type:
                build_constraints = self.constraints["build_types"][build_type.value.lower()]
                build_required_categories = build_constraints.get("required_categories", {})
                
                for category, count in build_required_categories.items():
                    if skill_categories.get(category, 0) < count:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Required skill categories not met for build type {build_type.value}. Category {category} needs {count}, has {skill_categories.get(category, 0)}"
                        )
                    
            # Then check required categories from class constraints
            required_categories = class_constraints.get("required_categories", {})
            for category, count in required_categories.items():
                if skill_categories.get(category, 0) < count:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Required class category {category} not met. Need {count}, have {skill_categories.get(category, 0)}"
                    )
                    
            # Check incompatible skills
            incompatible_skills = class_constraints.get("incompatible_skills", [])
            for incompatible_pair in incompatible_skills:
                if all(skill in selected_skills for skill in incompatible_pair):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Incompatible skills selected: {incompatible_pair}"
                    )
                    
            # Check weapon slot requirements
            weapon_slots = class_constraints.get("weapon_slots", {})
            available_weapons = weapon_slots.get("available_weapons", [])
            weapon_skill_found = False
            
            for skill in selected_skills:
                if skill in available_weapons:
                    weapon_skill_found = True
                    break
                    
            if not weapon_skill_found and available_weapons:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No weapon skill selected"
                )
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating skill selection: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error validating skill selection: {str(e)}"
            )

    def _validate_weapon_selection(
        self,
        selected_weapon: str,
        character_class: str
    ) -> bool:
        """Validate weapon selection against constraints.
        
        Args:
            selected_weapon: Selected weapon
            character_class: Character class
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Get class constraints
            class_constraints = self.class_constraints[character_class]
            available_weapons = class_constraints["weapon_slots"]["available_weapons"]
            
            # Check weapon is available
            return selected_weapon in available_weapons
            
        except (KeyError, TypeError):
            return False
    
    async def _select_equipment(
        self,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill],
        inventory: Optional[Dict] = None,
        character_class: str = "barbarian"
    ) -> Dict[str, Equipment]:
        """Select equipment that complements the build.
        
        Args:
            build_type: Type of build
            focus: Build focus
            selected_gems: Previously selected gems
            selected_skills: Previously selected skills
            inventory: Optional user inventory
            character_class: Character class
            
        Returns:
            Dict mapping slot names to selected equipment
        """
        equipment = {}
        
        # Select set pieces based on synergies
        set_pieces = await self._select_set_pieces(
            build_type=build_type,
            focus=focus,
            selected_gems=selected_gems,
            selected_skills=selected_skills,
            inventory=inventory
        )
        
        # Assign set pieces to slots
        for slot, piece in zip(self.SET_SLOTS.values(), set_pieces):
            equipment[slot] = piece
        
        # Validate equipment selection against class constraints
        if not self._validate_weapon_selection(equipment["Hands"], character_class):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid equipment selection for character class"
            )
        
        return equipment
    
    async def _select_set_pieces(
        self,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill],
        inventory: Optional[Dict]
    ) -> List[Equipment]:
        """Select set pieces based on build criteria.
        
        Args:
            build_type: Type of build
            focus: Build focus
            selected_gems: Previously selected gems
            selected_skills: Previously selected skills
            inventory: Optional user inventory
            
        Returns:
            List of selected set pieces
        """
        try:
            # Get available sets
            available_sets = self.set_bonuses  
            
            # Calculate scores for each set
            set_scores = []
            for set_name, data in available_sets.items():
                score = await self._calculate_set_score(
                    set_name=set_name,
                    data=data,
                    build_type=build_type,
                    focus=focus,
                    selected_gems=selected_gems,
                    selected_skills=selected_skills
                )
                set_scores.append((set_name, score))
            
            # Sort sets by score
            set_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select pieces based on valid combinations (6+2, 4+4, etc.)
            selected_pieces = []
            remaining_slots = 8
            
            # Try 6+2 combination first
            if remaining_slots >= 8:
                primary_set = set_scores[0][0]
                secondary_set = set_scores[1][0]
                
                # Add 6 pieces from primary set
                selected_pieces.extend(
                    await self._get_best_set_pieces(
                        set_name=primary_set,
                        count=6,
                        inventory=inventory
                    )
                )
                
                # Add 2 pieces from secondary set
                selected_pieces.extend(
                    await self._get_best_set_pieces(
                        set_name=secondary_set,
                        count=2,
                        inventory=inventory
                    )
                )
            
            return selected_pieces
        
        except (KeyError, AttributeError) as e:
            logger.warning(f"Error selecting set pieces: {str(e)}")
            return [
                Equipment(
                    name=None,
                    slot=f"set_{i}",
                    rank=None,
                    quality=None,
                    essence=None
                )
                for i in range(8)
            ]
    
    async def _calculate_equipment_score(
        self,
        equipment_name: str,
        slot: str,
        data: Dict,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill]
    ) -> float:
        """Calculate score for a piece of equipment.
        
        Args:
            equipment_name: Name of the equipment
            slot: Slot of the equipment
            data: Equipment data
            build_type: Type of build (PVE, PVP, etc)
            focus: Build focus (DPS, Survival, etc)
            selected_gems: List of selected gems
            selected_skills: List of selected skills
            
        Returns:
            Score between 0 and 1
        """
        total_score = 0.0
        
        # Score base stats
        base_stats = data.get("base_stats", {})
        if focus == BuildFocus.DPS:
            total_score += (
                base_stats.get("damage", 0) * 0.4 +
                base_stats.get("critical_hit", 0) * 0.3 +
                base_stats.get("attack_speed", 0) * 0.3
            )
        else:  # Survival focus
            total_score += (
                base_stats.get("life", 0) * 0.4 +
                base_stats.get("armor", 0) * 0.3 +
                base_stats.get("resistance", 0) * 0.3
            )
            
        # Score essence mods
        essence_mods = data.get("essence_mods", {})
        for essence_name, mods in essence_mods.items():
            if focus == BuildFocus.DPS:
                total_score += (
                    mods.get("damage", 0) * 0.4 +
                    mods.get("critical_hit", 0) * 0.3 +
                    mods.get("attack_speed", 0) * 0.3
                )
            else:  # Survival focus
                total_score += (
                    mods.get("life", 0) * 0.4 +
                    mods.get("armor", 0) * 0.3 +
                    mods.get("resistance", 0) * 0.3
                )
                
        # Score skill mods
        skill_mods = data.get("skill_mods", {})
        for skill in selected_skills:
            if skill.name in skill_mods:
                mods = skill_mods[skill.name]
                if focus == BuildFocus.DPS:
                    total_score += mods.get("damage", 0) * 0.5
                else:  # Survival focus
                    total_score += mods.get("defense", 0) * 0.5
                    
        # Score gem mods
        gem_mods = data.get("gem_mods", {})
        for gem in selected_gems:
            if gem.name in gem_mods:
                mods = gem_mods[gem.name]
                total_score += mods.get("effect_bonus", 0) * 0.3
                
        # Normalize score to 0-1 range
        return min(max(total_score / 100.0, 0.0), 1.0)

    async def _calculate_set_score(
        self,
        set_name: str,
        data: Dict,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill]
    ) -> float:
        """Calculate score for a set.
        
        Args:
            set_name: Name of the set
            data: Set data
            build_type: Type of build (PVE, PVP, etc)
            focus: Build focus (DPS, Survival, etc)
            selected_gems: List of selected gems
            selected_skills: List of selected skills
            
        Returns:
            Score between 0 and 1
        """
        total_score = 0.0
        
        # Score set bonuses
        for bonus_key in ["bonus_2pc", "bonus_4pc", "bonus_6pc"]:
            bonus = data.get(bonus_key, {})
            if focus == BuildFocus.DPS:
                total_score += (
                    bonus.get("damage", 0) * 0.4 +
                    bonus.get("critical_hit", 0) * 0.3 +
                    bonus.get("attack_speed", 0) * 0.3
                )
            else:  # Survival focus
                total_score += (
                    bonus.get("life", 0) * 0.4 +
                    bonus.get("armor", 0) * 0.3 +
                    bonus.get("resistance", 0) * 0.3
                )
                
        # Score skill synergies
        skill_synergies = data.get("skill_synergies", {})
        for skill in selected_skills:
            if skill.name in skill_synergies:
                synergies = skill_synergies[skill.name]
                if focus == BuildFocus.DPS:
                    total_score += synergies.get("damage", 0) * 0.5
                else:  # Survival focus
                    total_score += synergies.get("defense", 0) * 0.5
                    
        # Score gem synergies
        gem_synergies = data.get("gem_synergies", {})
        for gem in selected_gems:
            if gem.name in gem_synergies:
                synergies = gem_synergies[gem.name]
                total_score += synergies.get("effect_bonus", 0) * 0.3
                
        # Normalize score to 0-1 range
        return min(max(total_score / 100.0, 0.0), 1.0)
    
    async def _get_best_set_pieces(
        self,
        set_name: str,
        count: int,
        inventory: Optional[Dict]
    ) -> List[Equipment]:
        """Get the best pieces from a set.
        
        Args:
            set_name: Name of the set
            count: Number of pieces to get
            inventory: Optional user inventory
            
        Returns:
            List of selected equipment pieces
        """
        try:
            pieces = []
            set_data = self.set_bonuses[set_name]  
            
            # Sort pieces by their base stats
            sorted_pieces = sorted(
                set_data.items(),
                key=lambda x: sum(x[1].get("base_stats", {}).values()),
                reverse=True
            )
            
            # Take the top N pieces
            for piece_name, _ in sorted_pieces[:count]:
                # Get details from inventory if available
                if inventory and piece_name in inventory:
                    details = inventory[piece_name]
                    pieces.append(Equipment(
                        name=piece_name,
                        slot=details.get("slot"),
                        rank=details.get("rank"),
                        quality=details.get("quality"),
                        essence=details.get("essence")
                    ))
                else:
                    pieces.append(Equipment(
                        name=piece_name,
                        slot=None,
                        rank=None,
                        quality=None,
                        essence=None
                    ))
            
            return pieces
        
        except (KeyError, AttributeError) as e:
            logger.warning(
                f"Error getting pieces for set {set_name}: {str(e)}"
            )
            return [
                Equipment(
                    name=None,
                    slot=f"set_{i}",
                    rank=None,
                    quality=None,
                    essence=None
                )
                for i in range(count)
            ]
    
    def _calculate_stats(
        self,
        selected_gems: List[Gem],
        selected_skills: List[Skill],
        selected_equipment: Dict[str, Equipment]
    ) -> BuildStats:
        """Calculate build stats based on selections.
        
        Args:
            selected_gems: Selected gems
            selected_skills: Selected skills
            selected_equipment: Selected equipment
            
        Returns:
            BuildStats object with calculated stats
        """
        # TODO: Implement stat calculation
        return BuildStats(
            dps=0.0,
            survival=0.0,
            utility=0.0
        )
    
    async def _generate_recommendations(
        self,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill],
        selected_equipment: Dict[str, Equipment],
        inventory: Optional[Dict] = None,
        character_class: str = "barbarian"
    ) -> List[str]:
        """Generate recommendations for build improvement.
        
        Args:
            build_type: Type of build
            focus: Build focus
            selected_gems: Selected gems
            selected_skills: Selected skills
            selected_equipment: Selected equipment
            inventory: Optional user inventory
            character_class: Character class
            
        Returns:
            List of recommendations
        """
        # TODO: Implement recommendation generation
        return []
    
    async def _find_synergies(
        self,
        selected_gems: List[Gem],
        selected_skills: List[Skill],
        selected_equipment: List[Equipment]
    ) -> List[str]:
        """Find synergies between selected items.
        
        Args:
            selected_gems: Selected gems
            selected_skills: Selected skills
            selected_equipment: Selected equipment
            
        Returns:
            List of synergy descriptions
        """
        # TODO: Implement synergy detection
        return []
    
    def _matches_focus(self, category: str, focus: BuildFocus) -> bool:
        """Check if a category matches the build focus.
        
        Args:
            category: Category to check
            focus: Build focus
            
        Returns:
            True if category matches focus
        """
        # Get focus categories from build types data
        build_types = self.build_types
        focus_categories = set()
        
        # Extract categories from terms in build types data
        for build_type in build_types.values():
            if focus.value.lower() in build_type:
                focus_data = build_type[focus.value.lower()]
                focus_categories.update(
                    term.split()[0] for term in focus_data.get("terms", [])
                )
        
        return category in focus_categories

    def _calculate_gem_score(
        self,
        gem_name: str,
        build_type: BuildType,
        focus: BuildFocus
    ) -> float:
        """Calculate a gem's effectiveness score.
        
        Args:
            gem_name: Name of the gem
            build_type: Type of build
            focus: Build focus
            
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        total_weight = 0.0
        
        # Get gem's categories and their stats
        categories = self._get_gem_categories(gem_name)
        
        # Base weights for different aspects
        weights = {
            BuildType.PVE: {
                BuildFocus.DPS: {
                    "critical_hit": 1.0,
                    "attack_speed": 0.9,
                    "damage": 1.0,
                    "penetration": 0.8,
                    "area_damage": 0.9,
                    "skill_damage": 0.8,
                    "primary_attack": 0.7,
                    "damage_over_time": 0.7
                },
                BuildFocus.SURVIVAL: {
                    "life": 1.0,
                    "armor": 0.9,
                    "resistance": 0.8,
                    "block": 0.7,
                    "healing": 0.9,
                    "damage_reduction": 1.0,
                    "shield": 0.8,
                    "dodge": 0.7
                },
                BuildFocus.BUFF: {
                    "movement_speed": 0.9,
                    "cooldown_reduction": 1.0,
                    "crowd_control": 0.7,
                    "resource_generation": 0.8,
                    "buff_duration": 0.8,
                    "proc_chance": 0.7,
                    "area_effect": 0.9,
                    "control_duration": 0.6
                }
            },
            BuildType.PVP: {
                BuildFocus.DPS: {
                    "critical_hit": 0.9,
                    "attack_speed": 0.8,
                    "damage": 1.0,
                    "penetration": 1.0,
                    "area_damage": 0.7,
                    "skill_damage": 0.9,
                    "primary_attack": 0.8,
                    "damage_over_time": 0.6
                },
                BuildFocus.SURVIVAL: {
                    "life": 1.0,
                    "armor": 1.0,
                    "resistance": 0.9,
                    "block": 0.8,
                    "healing": 0.7,
                    "damage_reduction": 1.0,
                    "shield": 0.9,
                    "dodge": 0.8
                },
                BuildFocus.BUFF: {
                    "movement_speed": 1.0,
                    "cooldown_reduction": 0.9,
                    "crowd_control": 1.0,
                    "resource_generation": 0.7,
                    "buff_duration": 0.8,
                    "proc_chance": 0.7,
                    "area_effect": 0.8,
                    "control_duration": 0.9
                }
            }
        }
        
        # Get stat values for the gem
        try:
            gem_stats = self.stat_boosts
            for category in categories:
                if category in gem_stats:
                    # Get weight for this category
                    weight = weights[build_type][focus].get(category, 0.5)
                    total_weight += weight
                    
                    # Calculate score based on stat values
                    if gem_name in gem_stats[category]:
                        stat_data = gem_stats[category][gem_name]
                        
                        # Higher scores for scaling stats
                        scaling_bonus = 0.2 if stat_data.get("scaling", False) else 0.0
                        
                        # Base score from rank 10 value
                        rank_10_value = stat_data.get("rank_10", 0.0)
                        normalized_value = min(rank_10_value / 100.0, 1.0)
                        
                        category_score = (normalized_value + scaling_bonus) * weight
                        score += category_score
        
        except (KeyError, AttributeError) as e:
            logger.warning(
                f"Error calculating score for gem {gem_name}: {str(e)}"
            )
            return 0.0
        
        # Normalize final score
        return score / max(total_weight, 1.0) if total_weight > 0 else 0.0
    
    def _calculate_skill_score(
        self,
        skill_name: str,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem]
    ) -> float:
        """Calculate effectiveness score for a skill.
        
        Args:
            skill_name: Name of skill
            build_type: Type of build
            focus: Build focus
            selected_gems: Previously selected gems
            
        Returns:
            Score between 0 and 1
        """
        try:
            # Define type weights for different build types and focuses
            type_weights = {
                BuildType.PVE: {
                    BuildFocus.DPS: {
                        "damage": 1.0,
                        "aoe": 0.9,
                        "control": 0.5,
                        "mobility": 0.3
                    },
                    BuildFocus.SURVIVAL: {
                        "damage": 0.4,
                        "control": 0.8,
                        "mobility": 0.6,
                        "defense": 1.0
                    },
                    BuildFocus.BUFF: {
                        "damage": 0.3,
                        "control": 0.7,
                        "mobility": 0.5,
                        "support": 1.0
                    }
                },
                BuildType.PVP: {
                    BuildFocus.DPS: {
                        "damage": 0.9,
                        "control": 0.7,
                        "mobility": 0.8,
                        "aoe": 0.5
                    },
                    BuildFocus.SURVIVAL: {
                        "damage": 0.5,
                        "control": 0.8,
                        "mobility": 0.7,
                        "defense": 1.0
                    },
                    BuildFocus.BUFF: {
                        "damage": 0.4,
                        "control": 0.9,
                        "mobility": 0.8,
                        "support": 1.0
                    }
                }
            }
            
            # Get skill data
            skill_data = self.class_data["barbarian"]["base_skills"]["registry"][skill_name]
            score = 0.0
            weight = 0.0
            
            # Calculate score based on base type
            base_type = skill_data.get("base_type")
            if base_type in type_weights[build_type][focus]:
                type_score = type_weights[build_type][focus][base_type]
                score += type_score
                weight += 1.0
            
            # Add score for secondary type if present
            second_type = skill_data.get("second_base_type")
            if second_type and second_type in type_weights[build_type][focus]:
                type_score = type_weights[build_type][focus][second_type] * 0.5  # Half weight for secondary
                score += type_score
                weight += 0.5
            
            # Check categories
            categories = skill_data.get("categories", [])
            for category in categories:
                if self._matches_focus(category, focus):
                    score += 0.3  # Bonus for matching category
                    weight += 0.3
            
            # Check gem synergies
            for gem in selected_gems:
                for category in self._get_gem_categories(gem.name):
                    if category in self.synergies:
                        if skill_name in self.synergies[category]["skills"]:
                            score += 0.5  # Bonus for gem synergy
                            weight += 0.5
            
            # Normalize final score
            return score / max(weight, 1.0) if weight > 0 else 0.0
            
        except (KeyError, AttributeError) as e:
            logger.warning(f"Error calculating skill score for {skill_name}: {str(e)}")
            return 0.0
    
    def _get_gem_categories(self, gem_name: str) -> List[str]:
        """Get categories that a gem belongs to.
        
        Args:
            gem_name: Name of the gem
            
        Returns:
            List of category names
        """
        # First check synergies
        categories = []
        for category, data in self.synergies.items():
            if gem_name in data["gems"]:
                categories.append(category)
        
        return list(set(categories))  # Remove duplicates
    
    def _calculate_essence_score(
        self,
        essence: Dict,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem]
    ) -> float:
        """Calculate effectiveness score for an essence.
        
        Args:
            essence: Essence data
            build_type: Type of build
            focus: Build focus
            selected_gems: Previously selected gems
            
        Returns:
            Score between 0 and 1
        """
        skill_type = essence.get("skill_type", "")
        effect = essence.get("effect", "")
        effect_tags = essence.get("effect_tags", [])
        
        base_score = 0.0
        focus_bonus = 0.0
        build_type_bonus = 0.0
        gem_bonus = 0.0
        
        # Score based on effect type
        if skill_type:
            if focus == BuildFocus.DPS:
                if skill_type == "damage":
                    base_score = 0.4  # Increased base score for damage
                    focus_bonus = 0.3  # Focus bonus for damage
                    # Higher scores for percentage-based effects
                    if isinstance(effect, str):
                        if "increased" in effect.lower() or "more" in effect.lower():
                            base_score = max(base_score, 0.6)  # Higher base score for percentage bonuses
                            focus_bonus = max(focus_bonus, 0.4)  # Increased bonus for percentage effects
                        if "attack_speed" in effect_tags:
                            base_score = max(base_score, 0.6)  # Higher base score for attack speed
                            focus_bonus = max(focus_bonus, 0.4)  # Increased bonus for attack speed
                elif skill_type in {"control", "buff"}:
                    base_score = 0.1  # Lower score for non-damage essences
                    focus_bonus = 0.0  # No focus bonus for non-damage essences
            elif focus == BuildFocus.SURVIVAL:
                if skill_type in {"control", "buff"}:
                    base_score = 0.4  # Base score for defensive essences
                    focus_bonus = 0.3  # Focus bonus for survival
                elif skill_type == "damage":
                    base_score = 0.1  # Lower score for damage essences
                    focus_bonus = 0.1  # Lower focus bonus
                    
        # Build type bonuses
        if build_type == BuildType.PVP:
            # In PvP, control and utility skills are more valuable
            if skill_type == "control" or "utility" in effect_tags:
                build_type_bonus = 0.4  # Higher bonus for control/utility in PvP
                base_score = max(base_score, 0.3)  # Higher minimum score for control/utility
            elif "pvp" in effect_tags:
                build_type_bonus = 0.3  # Higher bonus for PvP effects
                base_score = max(base_score, 0.5)  # Higher minimum score for PvP effects
            elif "pve" in effect_tags:
                base_score = min(base_score, 0.1)  # Lower score for PvE effects in PvP
                focus_bonus = 0.0  # No focus bonus for PvE effects
                build_type_bonus = 0.0  # No build type bonus for PvE effects
            elif skill_type == "damage":
                # Reduce score for pure damage skills in PvP unless they have PvP tag
                base_score = min(base_score, 0.15)  # Lower base score for damage
                focus_bonus = min(focus_bonus, 0.1)  # Lower focus bonus for damage
        elif build_type == BuildType.FARM:
            if "farm" in effect_tags:
                build_type_bonus = 0.2
                base_score = max(base_score, 0.3)  # Higher minimum score for farming effects
        elif build_type == BuildType.RAID:
            if skill_type == "damage":
                build_type_bonus = 0.4  # Increased bonus for damage skills in raids
                base_score = max(base_score, 0.5)  # Higher minimum score for damage
                # Additional bonus for attack speed in raids
                if "attack_speed" in effect_tags:
                    build_type_bonus += 0.3  # Extra bonus for attack speed in raids
                # Additional bonus for percentage-based effects in raids
                if isinstance(effect, str):
                    if "increased" in effect.lower() or "more" in effect.lower():
                        build_type_bonus += 0.3  # Extra bonus for percentage-based effects in raids
                
        # Percentage bonus
        if isinstance(effect, str):
            if "increased" in effect.lower() or "more" in effect.lower():
                # Only apply percentage bonus if it's aligned with the focus and build type
                if (focus == BuildFocus.DPS and skill_type == "damage"):
                    # In PvP, only give percentage bonus to PvP-tagged skills
                    if build_type == BuildType.PVP and "pvp" not in effect_tags:
                        pass  # No percentage bonus for non-PvP damage skills
                    else:
                        base_score = max(base_score, 0.4)  # Higher minimum score for percentage bonuses
                        focus_bonus = max(focus_bonus, 0.3)  # Increased bonus for percentage effects
                elif (focus == BuildFocus.SURVIVAL and skill_type in {"control", "buff"}):
                    base_score = max(base_score, 0.3)  # Higher minimum score for percentage bonuses
                    focus_bonus = max(focus_bonus, 0.2)  # Increased bonus for percentage effects
            
            # Cooldown reduction bonus
            if "cooldown" in effect.lower() and "reduced" in effect.lower():
                base_score = max(base_score, 0.3)  # Higher minimum score for cooldown reduction
            
        # Attack speed bonus (separate from percentage bonus)
        if "attack_speed" in effect_tags:
            base_score = max(base_score, 0.4)  # Higher minimum score for attack speed
            focus_bonus = max(focus_bonus, 0.3)  # Increased bonus for attack speed
        
        # Calculate initial score before gem bonus
        initial_score = base_score + focus_bonus + build_type_bonus
        
        # Gem synergies
        for gem in selected_gems:
            if gem.name in self.gem_data["synergies"]:
                gem_synergies = self.gem_data["synergies"][gem.name].get("skills", [])
                if essence.get("skill") in gem_synergies:
                    gem_bonus = 0.3  # Fixed bonus for gem synergy
                    break  # Only apply one gem bonus
                    
        # Calculate final score
        total_score = initial_score + gem_bonus
        
        # Normalize score to 0-1 range
        return min(max(total_score, 0.0), 1.0)

    async def _select_gear_piece(
        self,
        slot: str,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill],
        inventory: Optional[Dict] = None
    ) -> Equipment:
        """Select the best gear piece for a given slot.
        
        Args:
            slot: Equipment slot to select for
            build_type: Type of build (PVE, PVP, etc)
            focus: Build focus (DPS, Survival, etc)
            selected_gems: List of selected gems
            selected_skills: List of selected skills
            inventory: Optional inventory data
            
        Returns:
            Selected Equipment piece
        """
        # Get gear data for slot
        gear_data = self.set_bonuses.get("gear", {}).get(slot, {})  
        if not gear_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No gear data found for slot: {slot}"
            )
        
        # If inventory provided, filter to available pieces
        if inventory and slot in inventory:
            gear_data = {
                name: data for name, data in gear_data.items()
                if name in inventory[slot]
            }
            
        # Score each piece
        piece_scores = []
        for piece_name, data in gear_data.items():
            score = await self._calculate_equipment_score(
                equipment_name=piece_name,
                slot=slot,
                data=data,
                build_type=build_type,
                focus=focus,
                selected_gems=selected_gems,
                selected_skills=selected_skills
            )
            
            piece_scores.append((piece_name, score))
        
        if not piece_scores:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No valid gear pieces found for slot: {slot}"
            )
        
        # Select highest scoring piece
        piece_name, _ = max(piece_scores, key=lambda x: x[1])
        return Equipment(
            name=piece_name,
            slot=slot,
            set_name=gear_data[piece_name]["set"]
        )

    async def analyze_build(
        self,
        build: BuildRecommendation,
        character_class: str
    ) -> BuildResponse:
        """Analyze a specific build configuration.
        
        Args:
            build: Build configuration to analyze
            character_class: Character class
            
        Returns:
            BuildResponse containing analysis results
        """
        try:
            # Validate character class
            if character_class not in self.CHARACTER_CLASSES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid character class: {character_class}"
                )
            
            # Find synergies between items
            synergies = await self._find_synergies(
                build.gems,
                build.skills,
                build.equipment
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                build.build_type,
                build.focus,
                build.gems,
                build.skills,
                build.equipment,
                None,  # No inventory for analysis
                character_class
            )
            
            return BuildResponse(
                build_type=build.build_type,
                focus=build.focus,
                character_class=character_class,
                gems=build.gems,
                skills=build.skills,
                equipment=build.equipment,
                recommendations=recommendations,
                synergies=synergies
            )
            
        except Exception as e:
            logger.error(f"Error analyzing build: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to analyze build: {str(e)}"
            )

    def _load_data(self) -> None:
        """Load required data from data directory."""
        # Load core data
        self.stats = self._load_json_file("gems/stat_boosts.json")
        self.build_types = self._load_json_file("build_types.json")
        
        # Load set data
        self.set_bonuses = self._load_json_file("sets.json")
        
        # Load gem data
        self.gem_data = self._load_json_file("gems/gems.json")
        
        # Load raw JSON files for other data
        self.constraints = self._load_json_file("constraints.json")
        self.synergies = self._load_json_file("synergies.json")
        
        # Load class-specific data
        self.class_data = {}
        self.class_constraints = {}
        for class_name in self.CHARACTER_CLASSES:
            self.class_data[class_name] = {
                "essences": self._load_json_file(f"classes/{class_name}/essences.json"),
                "base_skills": self._load_json_file(f"classes/{class_name}/base_skills.json")
            }
            self.class_constraints[class_name] = self._load_json_file(
                f"classes/{class_name}/constraints.json"
            )

    def _get_available_classes(self) -> Set[str]:
        """Get available character classes by scanning the classes directory.
        
        Returns:
            Set of available character class names
        """
        classes_dir = self.data_dir / "classes"
        if not classes_dir.exists():
            return set()
            
        return {d.name for d in classes_dir.iterdir() if d.is_dir()}
