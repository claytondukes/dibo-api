"""Test build generation service without any FastAPI dependencies."""

import json
from pathlib import Path

import pytest

from api.builds.models import BuildFocus, BuildType
from api.builds.service import BuildService

@pytest.fixture
def build_service():
    """Create a BuildService instance for testing."""
    return BuildService()

def test_load_indexed_data(build_service):
    """Test that indexed data is loaded correctly."""
    assert build_service.class_data is not None
    assert isinstance(build_service.class_data, dict)
    assert len(build_service.class_data) > 0

def test_class_data_consistency(build_service):
    """Test that class data is consistent with core data files."""
    for class_name, class_data in build_service.class_data.items():
        assert "base_skills" in class_data
        assert "essences" in class_data
        assert isinstance(class_data["base_skills"], dict)
        assert isinstance(class_data["essences"], dict)
