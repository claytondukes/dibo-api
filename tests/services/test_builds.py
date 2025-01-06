"""Tests for the build management service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException

from api.models.game_data.schemas.builds.models import BuildConfig
from api.models.game_data.schemas.equipment import EquipmentSlot
from api.models.game_data.schemas.gems import GemConfig
from api.models.game_data.schemas.stats import StatBlock
from api.services.builds import BuildService


def create_mock_gist():
    """Create a mock gist with valid build data."""
    valid_build_data = {
        "version": "1.0.0",
        "name": "Test Build",
        "class_type": "Warrior",
        "equipment": {
            "weapon": "mighty_sword",
            "armor": "plate_mail"
        },
        "gems": {
            "socket_1": {"type": "strength", "level": 1},
            "socket_2": {"type": "vitality", "level": 2}
        },
        "stats": {
            "strength": 10,
            "dexterity": 5,
            "intelligence": 3,
            "vitality": 7
        },
        "description": "A test build configuration",
        "tags": ["pvp", "beginner"]
    }
    
    return MagicMock(
        id="gist123",
        created_at="2025-01-05T23:03:16-05:00",
        updated_at="2025-01-05T23:03:16-05:00",
        files=[
            MagicMock(
                filename="build.json",
                content=f'{{"format_version": "1.0.0", "build": {str(valid_build_data).replace("\'", "\"")}}}',
                raw_url="https://gist.githubusercontent.com/raw/gist123/build.json"
            )
        ]
    )


@pytest.fixture
def valid_build():
    """Fixture providing a valid build configuration."""
    return BuildConfig(
        version="1.0.0",
        name="Test Build",
        class_type="Warrior",
        equipment={
            EquipmentSlot.WEAPON: "mighty_sword",
            EquipmentSlot.ARMOR: "plate_mail"
        },
        gems={
            "socket_1": GemConfig(type="strength", level=1),
            "socket_2": GemConfig(type="vitality", level=2)
        },
        stats=StatBlock(
            strength=10,
            dexterity=5,
            intelligence=3,
            vitality=7
        ),
        description="A test build configuration",
        tags=["pvp", "beginner"]
    )


@pytest.fixture
def mock_gist():
    """Fixture providing a mock gist response."""
    return create_mock_gist()


@pytest.fixture
def mock_data_manager():
    """Fixture providing a mock game data manager."""
    manager = AsyncMock()
    manager.item_exists.return_value = True
    manager.gem_exists.return_value = True
    manager.class_exists.return_value = True
    return manager


@pytest.fixture
def mock_gist_service():
    """Fixture providing a mock gist service."""
    service = AsyncMock()
    
    # Configure create_gist mock
    create_gist_mock = create_mock_gist()
    service.create_gist.return_value = create_gist_mock
    
    # Configure update_gist mock
    update_gist_mock = create_mock_gist()
    service.update_gist.return_value = update_gist_mock
    
    # Configure get_gist mock
    get_gist_mock = create_mock_gist()
    service.get_gist.return_value = get_gist_mock
    
    return service


@pytest.fixture
def build_service(mock_data_manager, mock_gist_service):
    """Fixture providing a build service instance."""
    return BuildService(
        data_manager=mock_data_manager,
        gist_service=mock_gist_service
    )


@pytest.mark.asyncio
async def test_validate_build_valid(build_service, valid_build):
    """Test validating a valid build configuration."""
    errors = await build_service.validate_build(valid_build)
    assert not errors


@pytest.mark.asyncio
async def test_validate_build_invalid_item(build_service, valid_build, mock_data_manager):
    """Test validating a build with an invalid item."""
    mock_data_manager.item_exists.return_value = False
    errors = await build_service.validate_build(valid_build)
    assert len(errors) == 2
    assert "Invalid item" in errors[0]


@pytest.mark.asyncio
async def test_validate_build_invalid_gem(build_service, valid_build, mock_data_manager):
    """Test validating a build with an invalid gem."""
    mock_data_manager.gem_exists.return_value = False
    errors = await build_service.validate_build(valid_build)
    assert len(errors) == 2
    assert "Invalid gem type" in errors[0]


@pytest.mark.asyncio
async def test_validate_build_invalid_class(build_service, valid_build, mock_data_manager):
    """Test validating a build with an invalid class."""
    mock_data_manager.class_exists.return_value = False
    errors = await build_service.validate_build(valid_build)
    assert len(errors) == 1
    assert "Invalid class type" in errors[0]


@pytest.mark.asyncio
async def test_save_build_success(build_service, valid_build, mock_gist_service):
    """Test successfully saving a build."""
    summary = await build_service.save_build(valid_build)
    assert summary.id == "gist123"
    assert summary.name == valid_build.name
    assert summary.class_type == valid_build.class_type


@pytest.mark.asyncio
async def test_save_build_validation_error(build_service, valid_build, mock_data_manager):
    """Test saving a build that fails validation."""
    mock_data_manager.item_exists.return_value = False
    with pytest.raises(HTTPException) as exc:
        await build_service.save_build(valid_build)
    assert exc.value.status_code == 400
    assert "Invalid build configuration" in exc.value.detail["message"]


@pytest.mark.asyncio
async def test_get_build_success(build_service, mock_gist, mock_gist_service):
    """Test successfully retrieving a build."""
    mock_gist_service.get_gist.return_value = mock_gist
    build = await build_service.get_build("gist123")
    assert isinstance(build, BuildConfig)


@pytest.mark.asyncio
async def test_get_build_not_found(build_service, mock_gist_service):
    """Test retrieving a non-existent build."""
    mock_gist_service.get_gist.side_effect = Exception("Not found")
    with pytest.raises(HTTPException) as exc:
        await build_service.get_build("nonexistent")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_build_success(build_service, valid_build, mock_gist_service):
    """Test successfully updating a build."""
    summary = await build_service.update_build("gist123", valid_build)
    assert summary.id == "gist123"
    assert summary.name == valid_build.name
    mock_gist_service.update_gist.assert_called_once()
