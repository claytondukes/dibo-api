"""Build generation service."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set

from fastapi import HTTPException, status

from ..core.config import get_settings
from .models import (
    BuildFocus,
    BuildResponse,
    BuildStats,
    BuildType,
    BuildRecommendation,
    Gem,
    Skill,
    Equipment
)


logger = logging.getLogger(__name__)


class BuildService:
    """Service for generating and analyzing builds."""
    
    # Required data files that must exist
    REQUIRED_FILES = {
        # Core data files
        "synergies.json",
        "constraints.json",
        "stats.json",
        
        # Gem data
        "gems/progression.json",
        "gems/stat_boosts.json",
        "gems/synergies.json",
        "gems/gems.json",
        
        # Equipment data
        "equipment/sets.json",
        
        # Class-specific data
        "classes/barbarian/essences.json",
        "classes/barbarian/constraints.json",
        "classes/barbarian/base_skills.json"
    }
    
    # Supported character classes
    CHARACTER_CLASSES = {"barbarian"}  # Add more as they are implemented
    
    def __init__(self, data_dir: Optional[Path] = None) -> None:
        """Initialize the build service.
        
        Args:
            data_dir: Optional path to data directory. If not provided,
                     uses the default from settings.
        
        Raises:
            HTTPException: If required data files are missing or invalid.
        """
        self.settings = get_settings()
        self.data_dir = data_dir or Path(self.settings.PROJECT_ROOT) / "data" / "indexed"
        
        # Validate data directory exists
        if not self.data_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Data directory not found: {self.data_dir}"
            )
        
        # Load all indexed data
        try:
            # First try to load and parse all files
            data_files = {}
            
            # Load core files
            core_files = {f for f in self.REQUIRED_FILES if not f.startswith("classes/")}
            for filename in core_files:
                file_path = self.data_dir / filename
                if not file_path.exists():
                    raise FileNotFoundError(
                        f"Required data file not found: {file_path}"
                    )
                with open(file_path, "r") as f:
                    data_files[filename] = json.load(f)
            
            # Load class-specific files
            for class_name in self.CHARACTER_CLASSES:
                class_files = {
                    f for f in self.REQUIRED_FILES 
                    if f.startswith(f"classes/{class_name}/")
                }
                for filename in class_files:
                    file_path = self.data_dir / filename
                    if not file_path.exists():
                        raise FileNotFoundError(
                            f"Required class data file not found: {file_path}"
                        )
                    with open(file_path, "r") as f:
                        data_files[filename] = json.load(f)
            
            # Store loaded data in instance variables
            self.constraints = data_files["constraints.json"]
            self.synergies = data_files["synergies.json"]
            self.stats = data_files["stats.json"]
            
            # Store gem data
            self.gem_data = {
                "progression": data_files["gems/progression.json"],
                "stat_boosts": data_files["gems/stat_boosts.json"],
                "synergies": data_files["gems/synergies.json"],
                "effects": data_files["gems/gems.json"]
            }
            
            # Store equipment data
            self.equipment_data = {
                "sets": data_files["equipment/sets.json"]
            }
            
            # Store class-specific data
            self.class_data = {}
            self.class_constraints = {}
            for class_name in self.CHARACTER_CLASSES:
                self.class_data[class_name] = {
                    "essences": data_files[f"classes/{class_name}/essences.json"],
                    "base_skills": data_files[f"classes/{class_name}/base_skills.json"]
                }
                self.class_constraints[class_name] = data_files[
                    f"classes/{class_name}/constraints.json"
                ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading data files: {str(e)}"
            )
        
        # Validate loaded data
        self._validate_data_structure()
    
    def _validate_data_structure(self) -> None:
        """Validate the structure of loaded data.
        
        Raises:
            HTTPException: If data structure is invalid.
        """
        # Validate synergies structure
        for category, data in self.synergies.items():
            if not isinstance(data, dict):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Invalid synergy category structure: {category}"
                )
            required_keys = {"gems", "essences", "skills"}
            if not all(key in data for key in required_keys):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Missing required keys in synergy category: {category}"
                )
        
        # Validate constraints structure
        required_constraints = {"gem_slots", "essence_slots"}
        if not all(key in self.constraints for key in required_constraints):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Missing required constraint categories"
            )
            
        # Validate essence structure
        for class_name, data in self.class_data.items():
            essence_data = data["essences"]
            required_essence_keys = {"metadata", "essences", "indexes"}
            if not all(key in essence_data for key in required_essence_keys):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Missing required essence keys for class {class_name}"
                )
            
            # Validate essence indexes
            required_indexes = {"by_slot", "by_skill"}
            if not all(key in essence_data["indexes"] for key in required_indexes):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Missing required essence indexes for class {class_name}"
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
            # 1. Validate inventory if provided
            if inventory:
                self._validate_inventory(inventory)
            
            # 2. Select gems based on build type and focus
            selected_gems = self._select_gems(build_type, focus, inventory)
            
            # 3. Select skills that synergize with the gems
            selected_skills = self._select_skills(
                build_type,
                focus,
                selected_gems,
                inventory,
                character_class
            )
            
            # 4. Select equipment that complements the build
            selected_equipment = self._select_equipment(
                build_type,
                focus,
                selected_gems,
                selected_skills,
                inventory,
                character_class
            )
            
            # 5. Calculate build stats
            stats = self._calculate_stats(
                selected_gems,
                selected_skills,
                selected_equipment
            )
            
            # 6. Generate recommendations
            recommendations = self._generate_recommendations(
                build_type,
                focus,
                selected_gems,
                selected_skills,
                selected_equipment,
                inventory,
                character_class
            )
            
            return BuildResponse(
                build=BuildRecommendation(
                    gems=selected_gems,
                    skills=selected_skills,
                    equipment=list(selected_equipment.values()),
                    synergies=self._find_synergies(
                        selected_gems,
                        selected_skills,
                        list(selected_equipment.values())
                    )
                ),
                stats=stats,
                recommendations=recommendations
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
    
    def _select_gems(
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
                owned_rank = None
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
            progression_data = self.gem_data["progression"][primary_gem]
            primary_star_rating = progression_data.get("star_rating")
            if not primary_star_rating:
                return None
        except (KeyError, AttributeError):
            return None
        
        # Get all gems with matching star rating
        candidates = []
        for gem_name, data in self.gem_data["progression"].items():
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
    
    def _select_skills(
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
        """
        # Get skills that match the build focus
        focus_skills = []
        for category, data in self.synergies.items():
            if self._matches_focus(category, focus):
                focus_skills.extend(data["skills"])
        
        # Get skills that synergize with selected gems
        gem_skills = []
        for gem in selected_gems:
            for category in self._get_gem_categories(gem.name):
                if category in self.synergies:
                    gem_skills.extend(self.synergies[category]["skills"])
        
        # Combine and deduplicate skills
        all_skills = list(set(focus_skills + gem_skills))
        
        # Validate skill selection against class constraints
        if not self._validate_skill_selection(all_skills, character_class):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid skill selection for character class"
            )
        
        # Sort skills by effectiveness
        all_skills.sort(
            key=lambda s: self._calculate_skill_score(
                s, build_type, focus, selected_gems
            ),
            reverse=True
        )
        
        # Select top 5 skills with essences
        selected_skills = []
        essence_data = self.class_data[character_class]["essences"]
        
        for skill in all_skills[:5]:
            # Find best essence for this skill
            best_essence = None
            best_score = -1
            
            # Get all essences for this skill from the index
            skill_essences = essence_data["indexes"]["by_skill"].get(skill, [])
            
            for essence_slug in skill_essences:
                essence = essence_data["essences"][essence_slug]
                
                # Calculate score based on effect type and tags
                score = 0
                if "effect_type" in essence:
                    if build_type == BuildType.PVE and essence["effect_type"] == "pve":
                        score += 0.5
                    elif build_type == BuildType.PVP and essence["effect_type"] == "pvp":
                        score += 0.5
                
                if "effect_tags" in essence:
                    if focus == BuildFocus.DPS and "damage" in essence["effect_tags"]:
                        score += 0.3
                    elif focus == BuildFocus.SURVIVAL and "defense" in essence["effect_tags"]:
                        score += 0.3
                
                if score > best_score:
                    best_score = score
                    best_essence = essence
            
            selected_skills.append(Skill(
                name=skill,
                essence=best_essence["essence_name"] if best_essence else None
            ))
        
        return selected_skills
    
    def _select_equipment(
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
        
        # Get equipment slots
        set_slots = [
            "ring1", "ring2", "neck", "hands",
            "waist", "feet", "bracer1", "bracer2"
        ]
        
        # Select set pieces based on synergies
        set_pieces = self._select_set_pieces(
            build_type=build_type,
            focus=focus,
            selected_gems=selected_gems,
            selected_skills=selected_skills,
            inventory=inventory
        )
        
        # Assign set pieces to slots
        for slot, piece in zip(set_slots, set_pieces):
            equipment[slot] = piece
        
        # Validate equipment selection against class constraints
        if not self._validate_weapon_selection(equipment["hands"], character_class):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid equipment selection for character class"
            )
        
        return equipment
    
    def _validate_skill_selection(
        self,
        selected_skills: List[str],
        character_class: str
    ) -> bool:
        """Validate skill selection against constraints.
        
        Args:
            selected_skills: List of selected skills
            character_class: Character class
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Get class constraints
            class_constraints = self.class_constraints[character_class]
            available_skills = class_constraints["skill_slots"]["available_skills"]
            
            # Check number of skills
            if len(selected_skills) != self.constraints["skill_slots"]["total_required"]:
                return False
            
            # Check each skill is available
            return all(skill in available_skills for skill in selected_skills)
            
        except (KeyError, TypeError):
            return False
            
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
    
    def _select_set_pieces(
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
            available_sets = self.equipment_data["sets"]
            
            # Calculate scores for each set
            set_scores = []
            for set_name, data in available_sets.items():
                score = self._calculate_set_score(
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
                    self._get_best_set_pieces(
                        set_name=primary_set,
                        count=6,
                        inventory=inventory
                    )
                )
                
                # Add 2 pieces from secondary set
                selected_pieces.extend(
                    self._get_best_set_pieces(
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
    
    def _calculate_equipment_score(
        self,
        piece_name: str,
        slot: str,
        data: Dict,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill]
    ) -> float:
        """Calculate an equipment piece's effectiveness score.
        
        Args:
            piece_name: Name of the piece
            slot: Equipment slot
            data: Equipment data
            build_type: Type of build
            focus: Build focus
            selected_gems: Previously selected gems
            selected_skills: Previously selected skills
            
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        total_weight = 0.0
        
        try:
            # Base stats weight
            base_stats = data.get("base_stats", {})
            for stat, value in base_stats.items():
                if self._matches_focus(stat, focus):
                    stat_score = min(value / 100.0, 1.0)
                    score += stat_score
                    total_weight += 1.0
            
            # Essence modification weight
            essence_mods = data.get("essence_mods", {})
            for mod_name, mod_data in essence_mods.items():
                for stat, value in mod_data.items():
                    if self._matches_focus(stat, focus):
                        mod_score = min(value / 100.0, 1.0)
                        score += mod_score * 0.8  # Weight essence mods slightly less
                        total_weight += 0.8
            
            # Skill synergy weight
            skill_mods = data.get("skill_mods", {})
            for skill in selected_skills:
                if skill.name in skill_mods:
                    score += 0.5
                    total_weight += 0.5
            
            # Gem synergy weight
            gem_mods = data.get("gem_mods", {})
            for gem in selected_gems:
                if gem.name in gem_mods:
                    score += 0.5
                    total_weight += 0.5
        
        except (KeyError, AttributeError) as e:
            logger.warning(
                f"Error calculating score for {piece_name}: {str(e)}"
            )
            return 0.0
        
        # Normalize final score
        return score / max(total_weight, 1.0) if total_weight > 0 else 0.0
    
    def _calculate_set_score(
        self,
        set_name: str,
        data: Dict,
        build_type: BuildType,
        focus: BuildFocus,
        selected_gems: List[Gem],
        selected_skills: List[Skill]
    ) -> float:
        """Calculate a set's effectiveness score.
        
        Args:
            set_name: Name of the set
            data: Set data
            build_type: Type of build
            focus: Build focus
            selected_gems: Previously selected gems
            selected_skills: Previously selected skills
            
        Returns:
            Score from 0.0 to 1.0
        """
        score = 0.0
        total_weight = 0.0
        
        try:
            # Score 2-piece bonus
            bonus_2pc = data.get("bonus_2pc", {})
            for stat, value in bonus_2pc.items():
                if self._matches_focus(stat, focus):
                    stat_score = min(value / 100.0, 1.0)
                    score += stat_score
                    total_weight += 1.0
            
            # Score 4-piece bonus (weighted higher)
            bonus_4pc = data.get("bonus_4pc", {})
            for stat, value in bonus_4pc.items():
                if self._matches_focus(stat, focus):
                    stat_score = min(value / 100.0, 1.0)
                    score += stat_score * 1.5  # Weight 4pc bonus higher
                    total_weight += 1.5
            
            # Score 6-piece bonus (weighted highest)
            bonus_6pc = data.get("bonus_6pc", {})
            for stat, value in bonus_6pc.items():
                if self._matches_focus(stat, focus):
                    stat_score = min(value / 100.0, 1.0)
                    score += stat_score * 2.0  # Weight 6pc bonus highest
                    total_weight += 2.0
            
            # Score skill synergies
            skill_synergies = data.get("skill_synergies", {})
            for skill in selected_skills:
                if skill.name in skill_synergies:
                    score += 0.5
                    total_weight += 0.5
            
            # Score gem synergies
            gem_synergies = data.get("gem_synergies", {})
            for gem in selected_gems:
                if gem.name in gem_synergies:
                    score += 0.5
                    total_weight += 0.5
        
        except (KeyError, AttributeError) as e:
            logger.warning(
                f"Error calculating score for set {set_name}: {str(e)}"
            )
            return 0.0
        
        # Normalize final score
        return score / max(total_weight, 1.0) if total_weight > 0 else 0.0
    
    def _get_best_set_pieces(
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
            set_data = self.equipment_data["sets"][set_name]["pieces"]
            
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
    
    def _generate_recommendations(
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
    
    def _find_synergies(
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
        # Define category mappings for each focus
        focus_categories = {
            BuildFocus.DPS: {
                "critical_hit",
                "attack_speed",
                "damage",
                "penetration",
                "area_damage",
                "skill_damage",
                "primary_attack",
                "damage_over_time"
            },
            BuildFocus.SURVIVAL: {
                "life",
                "armor",
                "resistance",
                "block",
                "healing",
                "damage_reduction",
                "shield",
                "dodge"
            },
            BuildFocus.UTILITY: {
                "movement_speed",
                "cooldown_reduction",
                "crowd_control",
                "resource_generation",
                "buff_duration",
                "proc_chance",
                "area_effect",
                "control_duration"
            }
        }
        
        return category in focus_categories.get(focus, set())
    
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
                BuildFocus.UTILITY: {
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
                BuildFocus.UTILITY: {
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
            gem_stats = self.gem_data["stat_boosts"]
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
            # Get skill data
            skill_data = self.class_data["barbarian"]["base_skills"][skill_name]
            skill_type = skill_data.get("type")
            damage_type = skill_data.get("damage_type")
            
            # Initialize scoring variables
            score = 0.0
            weight = 0.0
            
            # Get base weight for skill type
            if skill_type in type_weights[build_type]:
                weight = type_weights[build_type][skill_type][focus]
                score = weight
            
            # Check essence modifications from class data
            if skill_name in self.class_data["barbarian"]["essences"]:
                for essence in self.class_data["barbarian"]["essences"][skill_name]:
                    effect = essence.get("effect", "")
                    for category, value in self._parse_effect(effect).items():
                        if self._matches_focus(category, focus):
                            mod_score = min(value / 100.0, 1.0)
                            score += mod_score * 0.5  # Weight essence mods less
                            weight += 0.5
            
            # Check gem synergies
            for gem in selected_gems:
                for category in self._get_gem_categories(gem.name):
                    if category in self.synergies:
                        if skill_name in self.synergies[category]["skills"]:
                            score += 0.5  # Bonus for gem synergy
                            weight += 0.5
        
        except (KeyError, AttributeError) as e:
            logger.warning(
                f"Error calculating skill score for {skill_name}: {str(e)}")
            return 0.0
        
        # Normalize final score
        return score / max(weight, 1.0) if weight > 0 else 0.0
    
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
