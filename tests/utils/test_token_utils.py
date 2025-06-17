import pytest
from sweflow.utils.token_utils import TokenCounter


class TestTokenCounter:
    """Test suite for the TokenCounter class."""

    def test_count_tokens_of_string(self, sample_text):
        """Test counting tokens in a string."""
        # This is a basic test to ensure the method runs without errors
        # The exact token count will depend on the tokenizer
        token_count = TokenCounter.count_tokens_of_string(sample_text)
        assert isinstance(token_count, int)
        assert token_count > 0

    def test_count_tokens_of_dict_of_strings(self, sample_dict):
        """Test counting tokens in a dictionary of strings."""
        token_count = TokenCounter.count_tokens_of_dict_of_strings(sample_dict)
        assert isinstance(token_count, int)
        assert token_count > 0

        # The sum of individual string token counts should equal the dictionary token count
        individual_counts = sum(
            TokenCounter.count_tokens_of_string(value)
            for value in sample_dict.values()
        )
        assert token_count == individual_counts

    def test_count_tokens_of_list_of_dicts_of_strings(self, sample_list_of_dicts):
        """Test counting tokens in a list of dictionaries of strings."""
        token_count = TokenCounter.count_tokens_of_list_of_dicts_of_strings(sample_list_of_dicts)
        assert isinstance(token_count, int)
        assert token_count > 0

        # The sum of individual dictionary token counts should equal the list token count
        individual_counts = sum(
            TokenCounter.count_tokens_of_dict_of_strings(dict_item)
            for dict_item in sample_list_of_dicts
        )
        assert token_count == individual_counts

    def test_count_tokens_with_string(self, sample_text):
        """Test the generic count_tokens method with a string."""
        token_count = TokenCounter.count_tokens(sample_text)
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count == TokenCounter.count_tokens_of_string(sample_text)

    def test_count_tokens_with_dict(self, sample_dict):
        """Test the generic count_tokens method with a dictionary."""
        token_count = TokenCounter.count_tokens(sample_dict)
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count == TokenCounter.count_tokens_of_dict_of_strings(sample_dict)

    def test_count_tokens_with_list_of_dicts(self, sample_list_of_dicts):
        """Test the generic count_tokens method with a list of dictionaries."""
        token_count = TokenCounter.count_tokens(sample_list_of_dicts)
        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count == TokenCounter.count_tokens_of_list_of_dicts_of_strings(sample_list_of_dicts)

    def test_count_tokens_with_invalid_input(self):
        """Test the generic count_tokens method with invalid input."""
        with pytest.raises(ValueError):
            TokenCounter.count_tokens(None)

        with pytest.raises(ValueError):
            TokenCounter.count_tokens(123)

        # Lists that don't contain dictionaries should raise an error
        with pytest.raises((ValueError, AttributeError)):
            TokenCounter.count_tokens([1, 2, 3])
