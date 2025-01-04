# Game Data API Implementation Plan

## Overview

This document outlines the implementation plan for the Game Data API endpoints, which will provide access to game data such as gems, equipment sets, skills, and stats.

## Module Structure

```
api/
├── data/
│   ├── __init__.py
│   ├── models.py      # Pydantic models for data responses
│   ├── routes.py      # API route definitions
│   └── service.py     # Data access service
```

## Implementation Details

### 1. Data Models (models.py)

```python
class BuildCategory(str, Enum):
    """Categories for game elements."""
    MOVEMENT = "movement"
    PRIMARY_ATTACK = "primary_attack"
    ATTACK = "attack"
    DEFENSE = "defense"
    SUMMON = "summon"
    CHANNELED = "channeled"
    UTILITY = "utility"

class GemBase(BaseModel):
    name: str
    stars: int
    base_effect: str
    rank_10_effect: Optional[str]
    categories: List[BuildCategory]

class SetBonus(BaseModel):
    pieces: int
    bonus: str

class EquipmentSet(BaseModel):
    name: str
    description: str
    bonuses: Dict[str, str]  # e.g., "2": "bonus text"
    use_case: str

class StatValue(BaseModel):
    conditions: List[str]
    value: float
    unit: str
    scaling: bool

class StatModifier(BaseModel):
    name: str
    stars: Optional[str]
    base_values: List[StatValue]
    rank_10_values: List[StatValue]
    conditions: List[str]
    rank_10_conditions: List[str]

class StatInfo(BaseModel):
    gems: List[StatModifier]
    essences: List[StatModifier]

StatsResponse = RootModel[Dict[str, StatInfo]]

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
```

### 2. Data Service (service.py)

```python
class DataService:
    def __init__(self):
        # Load data files once at startup
        self._load_data()
        
    def get_gems(
        self, 
        stars: Optional[int] = None,
        category: Optional[BuildCategory] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[GemBase]:
        """Get gems with optional filtering."""
        
    def get_sets(
        self,
        pieces: Optional[int] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[EquipmentSet]:
        """Get equipment sets with optional filtering."""
        
    def get_skills(
        self,
        character_class: str,
        category: Optional[BuildCategory] = None,
        page: int = 1,
        per_page: int = 20
    ) -> PaginatedResponse[Skill]:
        """Get skills for a character class."""

    def get_stats(
        self,
        stat: Optional[str] = None
    ) -> Union[Dict[str, StatInfo], StatInfo]:
        """Get stats data with optional filtering."""
```

### 3. Routes Implementation (routes.py)

```python
router = APIRouter(prefix="/data", tags=["game-data"])

@router.get("/gems", response_model=PaginatedResponse[GemBase])
async def list_gems(
    stars: Optional[int] = Query(None),
    category: Optional[BuildCategory] = Query(None),
    page: int = Query(1, gt=0),
    per_page: int = Query(20, le=100)
):
    """List available gems with optional filtering."""

@router.get("/sets", response_model=PaginatedResponse[EquipmentSet])
async def list_sets(
    pieces: Optional[int] = Query(None),
    page: int = Query(1, gt=0),
    per_page: int = Query(20, le=100)
):
    """List available equipment sets."""

@router.get("/skills/{character_class}")
async def list_skills(
    character_class: str,
    category: Optional[BuildCategory] = Query(None),
    page: int = Query(1, gt=0),
    per_page: int = Query(20, le=100)
):
    """List available skills for a character class."""

@router.get("/stats", response_model=Union[Dict[str, StatInfo], StatInfo])
async def list_stats(
    stat: Optional[str] = Query(None)
):
    """List stat relationships with optional filtering."""
```

### 4. Caching Strategy

- Use FastAPI's caching mechanisms
- Cache responses since data is static
- Add cache headers for client-side caching

### 5. API Documentation

```markdown
### Game Data

1. **List Gems**
GET /data/gems

Query Parameters:
- stars: Filter by star rating (1, 2, or 5)
- category: Filter by category (movement, attack, etc.)
- page: Page number (default: 1)
- per_page: Items per page (default: 20, max: 100)

2. **List Equipment Sets**
GET /data/sets

Query Parameters:
- pieces: Filter by number of pieces (2, 4, or 6)
- page: Page number
- per_page: Items per page

3. **List Skills**
GET /data/skills/{character_class}

Path Parameters:
- character_class: Character class name

Query Parameters:
- category: Filter by category
- page: Page number
- per_page: Items per page

4. **List Stats**
GET /data/stats

Query Parameters:
- stat: Optional specific stat to retrieve
```

### 6. Testing Plan

```python
def test_list_gems():
    # Test gem listing with various filters
    
def test_list_sets():
    # Test set listing with piece filters
    
def test_list_skills():
    # Test skill listing for different classes
    
def test_list_stats():
    # Test stats listing with and without filters
    
def test_pagination():
    # Test pagination works correctly
    
def test_caching():
    # Test cache headers are set correctly
```

## Implementation Order

1. Create module structure
2. Implement data models
3. Create basic service with data loading
4. Add routes without filtering
5. Add filtering and pagination
6. Implement caching
7. Add tests
8. Update documentation

## Notes

- All endpoints will use proper error handling
- Responses will be properly paginated where applicable
- Data will be cached appropriately
- Documentation will be kept up to date
- Tests will be written for all functionality
