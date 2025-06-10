from typing import Dict, List

import tiktoken


class TokenCounter:

    @classmethod
    def count_tokens(cls, string: None | str | Dict[str, str] | List[Dict[str, str]], encoding_name: str = "o200k_base") -> int:
        """
        Count the number of tokens in a string, dictionary of strings, or list of dictionaries of strings.
        """
        if isinstance(string, str):
            return cls.count_tokens_of_string(string, encoding_name)
        elif isinstance(string, dict):
            return cls.count_tokens_of_dict_of_strings(string, encoding_name)
        elif isinstance(string, list):
            return cls.count_tokens_of_list_of_dicts_of_strings(string, encoding_name)
        else:
            raise ValueError(f"Invalid input type: {type(string)}")

    @classmethod
    def count_tokens_of_string(cls, string: str, encoding_name: str = "o200k_base") -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string, allowed_special="all"))
        return num_tokens

    @classmethod
    def count_tokens_of_dict_of_strings(cls, strings: Dict[str, str], encoding_name: str = "o200k_base") -> int:
        """Returns the number of tokens in a dictionary of text strings."""
        num_tokens = 0
        for key, string in strings.items():
            num_tokens += cls.count_tokens_of_string(string, encoding_name)
        return num_tokens

    @classmethod
    def count_tokens_of_list_of_dicts_of_strings(cls, strings: List[Dict[str, str]], encoding_name: str = "o200k_base") -> int:
        """Returns the number of tokens in a list of dictionaries of text strings."""
        num_tokens = 0
        for string_dict in strings:
            num_tokens += cls.count_tokens_of_dict_of_strings(string_dict, encoding_name)
        return num_tokens
