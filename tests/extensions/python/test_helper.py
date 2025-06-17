import pytest
from pathlib import Path
import json
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock

from sweflow.extensions.python.helper import (
    collect_nodes,
    read_file_from_project,
    generate_patch,
    convert_patch_to_replace,
    generate_test_script
)


class TestHelperFunctions:
    """Test suite for the helper functions in the Python extension."""

    @pytest.fixture
    def sample_project_dir(self, tmp_path):
        """Create a sample project directory with some files."""
        project_dir = tmp_path / "sample_project"
        project_dir.mkdir()
        
        # Create a Python file
        python_file = project_dir / "sample.py"
        python_file.write_text("def hello():\n    return 'Hello, World!'\n")
        
        # Create a text file
        text_file = project_dir / "sample.txt"
        text_file.write_text("This is a sample text file.")
        
        return project_dir

    def test_read_file_from_project(self, sample_project_dir):
        """Test reading a file from a project."""
        # Test reading a Python file
        content = read_file_from_project(sample_project_dir, "sample.py")
        assert content == "def hello():\n    return 'Hello, World!'\n"
        
        # Test reading a text file
        content = read_file_from_project(sample_project_dir, "sample.txt")
        assert content == "This is a sample text file."
        
        # Test reading a non-existent file
        with pytest.raises(FileNotFoundError):
            read_file_from_project(sample_project_dir, "non_existent.py")

    def test_generate_patch(self):
        """Test generating a patch from skeleton and reference files."""
        skeleton_files = [
            {"filepath": "file1.py", "content": "def func1():\n    pass\n"},
            {"filepath": "file2.py", "content": "def func2():\n    pass\n"}
        ]
        
        reference_files = [
            {"filepath": "file1.py", "content": "def func1():\n    return 'Hello'\n"},
            {"filepath": "file2.py", "content": "def func2():\n    return 'World'\n"}
        ]
        
        patch = generate_patch(skeleton_files, reference_files)
        
        # The patch should contain the differences between the skeleton and reference files
        assert "def func1():" in patch
        assert "return 'Hello'" in patch
        assert "def func2():" in patch
        assert "return 'World'" in patch

    def test_convert_patch_to_replace(self):
        """Test converting a patch to a replace format."""
        patch = """
--- file1.py
+++ file1.py
@@ -1,2 +1,2 @@
 def func1():
-    pass
+    return 'Hello'
"""
        
        replace = convert_patch_to_replace(patch)
        
        # The replace format should contain the file name and the changes
        assert "file1.py" in replace
        assert "def func1():" in replace
        assert "pass" in replace
        assert "return 'Hello'" in replace

    def test_generate_test_script(self):
        """Test generating a test script."""
        test_ids = ["test1", "test2"]
        
        script = generate_test_script(test_ids)
        
        # The script should contain the test IDs
        assert "pytest" in script
        assert "test1" in script
        assert "test2" in script
