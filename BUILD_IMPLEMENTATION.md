# DIBO API - Next Session Implementation Guide

## Current Context & Progress
- Authentication endpoints are complete and tested
- Build management system is implemented
- Gems API is fully functional with tests
- Equipment Sets schema and data structure exists but needs API implementation

## Next Task: Equipment Sets API Implementation

### Current State
1. Schema Location: `/api/models/game_data/schemas/equipment.py`
   - `EquipmentSet` model defined
   - `EquipmentSets` collection model ready
   - All required fields and validations set

2. Data Source:
   - JSON file: `equipment/sets.json`
   - Loaded via GameDataManager

3. Tests:
   - Schema tests exist in `tests/unit/models/game_data/test_schemas.py`
   - No API integration tests yet

### Implementation Steps

1. Create Equipment Routes
   ```python
   # /api/routes/game/equipment.py
   @router.get("/equipment/sets")
   async def list_equipment_sets(
       pieces: Optional[int] = Query(None),
       page: int = Query(1),
       per_page: int = Query(20, le=100)
   ) -> List[EquipmentSet]
   ```

2. Add Integration Tests
   - Create: `/tests/api/game/test_equipment.py`
   - Test cases:
     - List all sets
     - Filter by pieces (2/4/6)
     - Pagination
     - Invalid queries

3. Update Router Registration
   - File: `/api/routes/game/__init__.py`
   - Add: `from .equipment import router as equipment_router`
   - Include: `router.include_router(equipment_router)`

### Testing Requirements
- Use pytest fixtures from `conftest.py`
- Follow existing test patterns from `test_gems.py`
- Test all query parameters
- Verify response structure matches schema
- Check error cases

### API Response Format
```json
{
  "sets": [
    {
      "name": "Valor's Edge",
      "pieces": 4,
      "description": "Enhances critical strike capabilities",
      "bonuses": {
        "2": "+10% Critical Strike Chance",
        "4": "+25% Critical Strike Damage"
      },
      "use_case": "DPS builds focusing on critical hits"
    }
  ],
  "page": 1,
  "per_page": 20,
  "total": 45
}
```

### Important Notes
- Follow existing code style and patterns
- Maintain type hints throughout
- Document all public functions
- Add proper error handling
- Keep performance in mind for pagination

## Future Tasks (After Equipment Sets)
1. Skills API implementation
2. Essences API implementation
3. Cache layer for game data
4. API rate limiting

## Reference Files
- `/api/routes/game/gems.py` - Example of working game data endpoint
- `/tests/api/game/test_gems.py` - Example of proper test structure
- `/api/docs/endpoints.md` - API documentation to match
