import os
import pytest
from pathlib import Path


@pytest.fixture
def test_data_dir():
    """Return the path to the test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def temp_dir(tmp_path):
    """Return a temporary directory for test use."""
    return tmp_path


@pytest.fixture
def sample_text():
    """Return a sample text for token counting tests."""
    return "This is a sample text for testing token counting functionality."


@pytest.fixture
def sample_dict():
    """Return a sample dictionary for token counting tests."""
    return {
        "key1": "This is the first value.",
        "key2": "This is the second value.",
        "key3": "This is the third value."
    }


@pytest.fixture
def sample_list_of_dicts():
    """Return a sample list of dictionaries for token counting tests."""
    return [
        {"key1": "Value 1", "key2": "Value 2"},
        {"key3": "Value 3", "key4": "Value 4"},
        {"key5": "Value 5", "key6": "Value 6"}
    ]
