import ast
import pytest
from sweflow.extensions.python.helper.code_utils import (
    CodeParser, 
    format_docstring, 
    FileSkeletonizer,
    skeletonize_file
)


def test_code_parser():
    """Test the CodeParser class."""
    # Test source code with a simple function
    source_code = """
def test_function():
    \"\"\"This is a test function.\"\"\"
    return "Hello, world!"
"""
    
    # Test get_function_node
    node = CodeParser.get_function_node(source_code, "test_function", 2)
    assert isinstance(node, ast.FunctionDef)
    assert node.name == "test_function"
    
    # Test get_node_content
    content = CodeParser.get_node_content(node)
    assert "def test_function():" in content
    assert "This is a test function." in content
    assert "return" in content
    assert "Hello, world!" in content
    
    # Test get_function_content
    function_content = CodeParser.get_function_content(source_code, "test_function", 2)
    assert "def test_function():" in function_content
    assert "This is a test function." in function_content
    assert "return" in function_content
    assert "Hello, world!" in function_content
    
    # Test with non-existent function
    assert CodeParser.get_function_content(source_code, "non_existent_function", 2) is None


def test_format_docstring():
    """Test the format_docstring function."""
    docstring = """This is a test docstring.
    
It has multiple lines.
And some indentation."""
    
    formatted = format_docstring(docstring, "    ")
    assert "    This is a test docstring." in formatted
    assert "    It has multiple lines." in formatted
    assert "    And some indentation." in formatted


def test_file_skeletonizer():
    """Test the FileSkeletonizer class."""
    # Test source code with multiple functions
    source_code = """
def function1():
    \"\"\"Function 1 docstring.\"\"\"
    return "Function 1"

def function2():
    \"\"\"Function 2 docstring.\"\"\"
    return "Function 2"
"""
    
    filepath = "test_file.py"
    target_core_nodes = [f"{filepath}:2:function1"]
    dependent_core_nodes = [f"{filepath}:6:function2"]
    docstrings = {
        f"{filepath}:2:function1": {"docstring": "Updated function 1 docstring."},
        f"{filepath}:6:function2": {"docstring": "Updated function 2 docstring."}
    }
    
    file_info = {
        "filepath": filepath,
        "content": source_code
    }
    
    # Test skeletonize_file
    skeletonized_code, reference_code = skeletonize_file(
        file_info,
        target_core_nodes,
        dependent_core_nodes,
        docstrings
    )
    
    # Check that the skeletonized code contains the target function with ellipsis
    assert "def function1():" in skeletonized_code
    assert "Updated function 1 docstring." in skeletonized_code
    assert "..." in skeletonized_code
    
    # Check that the reference code contains both functions with updated docstrings
    assert "def function1():" in reference_code
    assert "def function2():" in reference_code
    assert "Updated function 1 docstring." in reference_code
    assert "Updated function 2 docstring." in reference_code
    assert "Function 1" in reference_code
    assert "Function 2" in reference_code


def test_file_skeletonizer_with_decorators():
    """Test the FileSkeletonizer class with decorated functions."""
    # Test source code with decorated functions
    source_code = """
@decorator
def decorated_function():
    \"\"\"Decorated function docstring.\"\"\"
    return "Decorated function"
"""
    
    filepath = "test_file.py"
    target_core_nodes = [f"{filepath}:2:decorated_function"]
    dependent_core_nodes = []
    docstrings = {
        f"{filepath}:2:decorated_function": {"docstring": "Updated decorated function docstring."}
    }
    
    file_info = {
        "filepath": filepath,
        "content": source_code
    }
    
    # Test skeletonize_file
    skeletonized_code, reference_code = skeletonize_file(
        file_info,
        target_core_nodes,
        dependent_core_nodes,
        docstrings
    )
    
    # Check that the skeletonized code contains the decorated function with ellipsis
    assert "@decorator" in skeletonized_code
    assert "def decorated_function():" in skeletonized_code
    assert "Updated decorated function docstring." in skeletonized_code
    assert "..." in skeletonized_code