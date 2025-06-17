import pytest
import ast
from sweflow.extensions.python.helper.code_utils import (
    CodeParser,
    format_docstring,
    FileSkeletonizer,
    skeletonize_file
)


class TestCodeParser:
    """Test suite for the CodeParser class."""

    @pytest.fixture
    def sample_function_code(self):
        """Sample function code for testing."""
        return """
def test_function():
    \"\"\"This is a test function.\"\"\"
    return "Hello, World!"
"""

    @pytest.fixture
    def sample_decorated_function_code(self):
        """Sample decorated function code for testing."""
        return """
@decorator1
@decorator2
def test_function():
    \"\"\"This is a test function.\"\"\"
    return "Hello, World!"
"""

    def test_get_start_line(self, sample_function_code, sample_decorated_function_code):
        """Test getting the start line of a function."""
        # Test with a regular function
        tree = ast.parse(sample_function_code)
        function_node = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        start_line = CodeParser.get_start_line(function_node)
        assert start_line == 2  # Line number in the sample code

        # Test with a decorated function
        tree = ast.parse(sample_decorated_function_code)
        function_node = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        start_line = CodeParser.get_start_line(function_node)
        assert start_line == 2  # Line number of the first decorator in the sample code

    def test_get_function_node(self, sample_function_code):
        """Test getting a function node by name and line number."""
        # Test with a valid function
        function_node = CodeParser.get_function_node(sample_function_code, "test_function", 2)
        assert function_node is not None
        assert isinstance(function_node, ast.FunctionDef)
        assert function_node.name == "test_function"

        # Test with an invalid function name
        function_node = CodeParser.get_function_node(sample_function_code, "invalid_function", 2)
        assert function_node is None

        # Test with an invalid line number
        function_node = CodeParser.get_function_node(sample_function_code, "test_function", 999)
        assert function_node is None

    def test_get_node_content(self, sample_function_code):
        """Test getting the content of a node."""
        tree = ast.parse(sample_function_code)
        function_node = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        content = CodeParser.get_node_content(function_node)
        
        # The content should contain the function definition
        assert "def test_function():" in content
        assert "This is a test function." in content
        assert "return 'Hello, World!'" in content

    def test_get_function_content(self, sample_function_code):
        """Test getting the content of a function."""
        # Test with a valid function
        content = CodeParser.get_function_content(sample_function_code, "test_function", 2)
        assert content is not None
        assert "def test_function():" in content
        assert "This is a test function." in content
        assert "return 'Hello, World!'" in content

        # Test with an invalid function name
        content = CodeParser.get_function_content(sample_function_code, "invalid_function", 2)
        assert content is None

        # Test with an invalid line number
        content = CodeParser.get_function_content(sample_function_code, "test_function", 999)
        assert content is None


class TestFormatDocstring:
    """Test suite for the format_docstring function."""

    def test_format_docstring_single_line(self):
        """Test formatting a single-line docstring."""
        docstring = "This is a single-line docstring."
        indent = "    "
        formatted = format_docstring(docstring, indent)
        assert formatted == "    This is a single-line docstring."

    def test_format_docstring_multi_line(self):
        """Test formatting a multi-line docstring."""
        docstring = """This is a multi-line docstring.
        
It has multiple paragraphs."""
        indent = "    "
        formatted = format_docstring(docstring, indent)
        assert "    This is a multi-line docstring." in formatted
        assert "    It has multiple paragraphs." in formatted


class TestFileSkeletonizer:
    """Test suite for the FileSkeletonizer class."""

    @pytest.fixture
    def sample_file_info(self):
        """Sample file info for testing."""
        return {
            "filepath": "test.py",
            "content": """
def function1():
    \"\"\"Function 1 docstring.\"\"\"
    return "Function 1"

def function2():
    \"\"\"Function 2 docstring.\"\"\"
    return "Function 2"
"""
        }

    @pytest.fixture
    def target_core_nodes(self):
        """Sample target core nodes for testing."""
        return ["test.py:2:function1"]

    @pytest.fixture
    def dependent_core_nodes(self):
        """Sample dependent core nodes for testing."""
        return ["test.py:6:function2"]

    @pytest.fixture
    def docstrings(self):
        """Sample docstrings for testing."""
        return {
            "test.py:2:function1": {"docstring": "Updated function 1 docstring."},
            "test.py:6:function2": {"docstring": "Updated function 2 docstring."}
        }

    def test_skeletonize_file(self, sample_file_info, target_core_nodes, dependent_core_nodes, docstrings):
        """Test skeletonizing a file."""
        skeletonized_code, reference_code = skeletonize_file(
            sample_file_info,
            target_core_nodes,
            dependent_core_nodes,
            docstrings
        )

        # Check the skeletonized code
        assert "def function1():" in skeletonized_code
        assert "Updated function 1 docstring." in skeletonized_code
        assert "..." in skeletonized_code  # Ellipsis for the function body
        assert "return \"Function 1\"" not in skeletonized_code

        # Check the reference code
        assert "def function1():" in reference_code
        assert "Updated function 1 docstring." in reference_code
        assert "return 'Function 1'" in reference_code
        assert "def function2():" in reference_code
        assert "Updated function 2 docstring." in reference_code
        assert "return 'Function 2'" in reference_code
