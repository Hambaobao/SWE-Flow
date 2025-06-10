import pytest
from sweflow.utils.token_utils import TokenCounter


def test_count_tokens_of_string():
    """Test counting tokens in a string."""
    # Test with a simple string
    result = TokenCounter.count_tokens_of_string("Hello, world!")
    assert isinstance(result, int)
    assert result > 0

    # Test with an empty string
    result = TokenCounter.count_tokens_of_string("")
    assert result == 0


def test_count_tokens_of_dict_of_strings():
    """Test counting tokens in a dictionary of strings."""
    test_dict = {
        "key1": "Hello, world!",
        "key2": "This is a test.",
        "key3": ""
    }
    result = TokenCounter.count_tokens_of_dict_of_strings(test_dict)
    assert isinstance(result, int)
    assert result > 0

    # Test with empty dictionary
    result = TokenCounter.count_tokens_of_dict_of_strings({})
    assert result == 0


def test_count_tokens_of_list_of_dicts_of_strings():
    """Test counting tokens in a list of dictionaries of strings."""
    test_list = [
        {"key1": "Hello, world!"},
        {"key2": "This is a test.", "key3": "Another string."},
        {"key4": ""}
    ]
    result = TokenCounter.count_tokens_of_list_of_dicts_of_strings(test_list)
    assert isinstance(result, int)
    assert result > 0

    # Test with empty list
    result = TokenCounter.count_tokens_of_list_of_dicts_of_strings([])
    assert result == 0


def test_count_tokens():
    """Test the main count_tokens method with different input types."""
    # Test with string
    result = TokenCounter.count_tokens("Hello, world!")
    assert isinstance(result, int)
    assert result > 0

    # Test with dictionary
    test_dict = {"key1": "Hello, world!", "key2": "This is a test."}
    result = TokenCounter.count_tokens(test_dict)
    assert isinstance(result, int)
    assert result > 0

    # Test with list of dictionaries
    test_list = [{"key1": "Hello, world!"}, {"key2": "This is a test."}]
    result = TokenCounter.count_tokens(test_list)
    assert isinstance(result, int)
    assert result > 0

    # Test with invalid input type
    with pytest.raises(ValueError):
        TokenCounter.count_tokens(123)