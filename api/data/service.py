"""Service for accessing game data."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, TypeVar, Generic, Union

from fastapi import HTTPException, status

from ..core.config import get_settings
from .models import (
    BuildCategory,
    GemBase,
    EquipmentSet,
    Skill,
    PaginatedResponse,
    StatInfo
)


logger = logging.getLogger(__name__)
T = TypeVar("T")


class DataService:
    """Service for accessing game data."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        """Initialize the data service.

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

        # Load all data files
        try:
            self._load_data()
        except Exception as e:
            logger.error("Error loading data files: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error loading data files: {str(e)}"
            )

    def _load_data(self) -> None:
        """Load all game data from files."""
        # Load gems data
        gems_file = self.data_dir / "gems" / "gem_skillmap.json"
        if not gems_file.exists():
            raise FileNotFoundError(f"Gems data file not found: {gems_file}")
        with open(gems_file, "r") as f:
            self.gems_data = json.load(f)

        # Load equipment sets data
        sets_file = self.data_dir / "equipment" / "sets.json"
        if not sets_file.exists():
            raise FileNotFoundError(f"Sets data file not found: {sets_file}")
        with open(sets_file, "r") as f:
            self.sets_data = json.load(f)

        # Load skills data for each class
        self.skills_data = {}
        for class_dir in (self.data_dir / "classes").iterdir():
            if class_dir.is_dir():
                skills_file = class_dir / "base_skills.json"
                if skills_file.exists():
                    with open(skills_file, "r") as f:
                        self.skills_data[class_dir.name] = json.load(f)

    def _paginate(
        self,
        items: List[T],
        page: int,
        per_page: int
    ) -> PaginatedResponse[T]:
        """Create a paginated response.

        Args:
            items: List of items to paginate
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            PaginatedResponse containing the paginated items
        """
        total = len(items)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        return PaginatedResponse(
            items=items[start_idx:end_idx],
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

    def get_gems(
        self,
        stars: Optional[int] = None,
        category: Optional[BuildCategory] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[GemBase]:
        """Get gems with optional filtering.

        Args:
            stars: Optional star rating to filter by
            category: Optional category to filter by
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            PaginatedResponse containing the filtered gems
        """
        # Get gems from the correct category if specified
        gems = []
        categories = [category.value] if category else self.gems_data["gems_by_skill"].keys()
        
        for cat in categories:
            for gem in self.gems_data["gems_by_skill"][cat]:
                if stars and int(gem["Stars"]) != stars:
                    continue
                
                gems.append(GemBase(
                    name=gem["Name"],
                    stars=int(gem["Stars"]),
                    base_effect=gem["Base Effect"],
                    rank_10_effect=gem.get("Rank 10 Effect"),
                    categories=[BuildCategory(cat)]
                ))

        # Remove duplicates while preserving order
        seen = set()
        unique_gems = []
        for gem in gems:
            if gem.name not in seen:
                seen.add(gem.name)
                unique_gems.append(gem)

        return self._paginate(unique_gems, page, per_page)

    def get_sets(
        self,
        pieces: Optional[int] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[EquipmentSet]:
        """Get equipment sets with optional filtering.

        Args:
            pieces: Optional number of pieces to filter by
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            PaginatedResponse containing the filtered sets
        """
        sets = []
        for name, data in self.sets_data["registry"].items():
            if pieces and data["pieces"] != pieces:
                continue

            sets.append(EquipmentSet(
                name=name,
                description=data["description"],
                bonuses=data["bonuses"],
                use_case=data["use_case"]
            ))

        return self._paginate(sets, page, per_page)

    def get_skills(
        self,
        character_class: str,
        category: Optional[BuildCategory] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[Skill]:
        """Get skills for a character class.

        Args:
            character_class: Character class name
            category: Optional category to filter by
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            PaginatedResponse containing the filtered skills

        Raises:
            HTTPException: If character class is not found
        """
        if character_class not in self.skills_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Character class not found: {character_class}"
            )

        skills = []
        class_skills = self.skills_data[character_class]
        
        for skill_data in class_skills["skills"]:
            if category and category.value not in skill_data["categories"]:
                continue

            skills.append(Skill(
                name=skill_data["name"],
                description=skill_data["description"],
                cooldown=skill_data.get("cooldown"),
                categories=[
                    BuildCategory(cat)
                    for cat in skill_data["categories"]
                ]
            ))

        return self._paginate(skills, page, per_page)

    def get_stats(self, stat: Optional[str] = None) -> Union[Dict[str, StatInfo], StatInfo]:
        """Get stats data with optional filtering.

        Args:
            stat: Optional stat name to filter by

        Returns:
            If stat is specified, returns StatInfo for that stat.
            Otherwise returns dictionary mapping stat names to their info.

        Raises:
            HTTPException: If stat specified but not found
        """
        stats_file = self.data_dir / "stats.json"
        if not stats_file.exists():
            raise FileNotFoundError(f"Stats data file not found: {stats_file}")

        with open(stats_file, "r") as f:
            data = json.load(f)

        if stat:
            if stat not in data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Stat not found: {stat}"
                )
            return StatInfo(**data[stat])

        return {name: StatInfo(**info) for name, info in data.items()}


# Singleton instance
_data_service = DataService()


def get_data_service() -> DataService:
    """Get DataService instance."""
    return _data_service
