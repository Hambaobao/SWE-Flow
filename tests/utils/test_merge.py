import json
import pytest
from pathlib import Path
from sweflow.utils.merge import merge_to_jsonl


class TestMerge:
    """Test suite for the merge module."""

    @pytest.fixture
    def mock_input_dir(self, tmp_path):
        """Create a mock input directory with test data files."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        # Create step-flags.json
        step_flags = [
            {"step": 0, "flag": True},
            {"step": 1, "flag": False},
            {"step": 2, "flag": True}
        ]
        with open(input_dir / "step-flags.json", "w") as f:
            json.dump(step_flags, f)

        # Create specifications.json
        specifications = [
            {"step": 0, "specification": "Spec 0"},
            {"step": 1, "specification": "Spec 1"},
            {"step": 2, "specification": "Spec 2"}
        ]
        with open(input_dir / "specifications.json", "w") as f:
            json.dump(specifications, f)

        # Create base-commits.json
        base_commits = [
            {"step": 0, "base-commit": "base0"},
            {"step": 1, "base-commit": "base1"},
            {"step": 2, "base-commit": "base2"}
        ]
        with open(input_dir / "base-commits.json", "w") as f:
            json.dump(base_commits, f)

        # Create reference-commits.json
        reference_commits = [
            {"step": 0, "reference-commit": "ref0"},
            {"step": 1, "reference-commit": "ref1"},
            {"step": 2, "reference-commit": "ref2"}
        ]
        with open(input_dir / "reference-commits.json", "w") as f:
            json.dump(reference_commits, f)

        # Create fail-to-pass-test-ids.json
        fail_to_pass_test_ids = [
            {"step": 0, "fail-to-pass-test-ids": ["test0"]},
            {"step": 1, "fail-to-pass-test-ids": ["test1"]},
            {"step": 2, "fail-to-pass-test-ids": ["test2"]}
        ]
        with open(input_dir / "fail-to-pass-test-ids.json", "w") as f:
            json.dump(fail_to_pass_test_ids, f)

        # Create pass-to-pass-test-ids.json
        pass_to_pass_test_ids = [
            {"step": 0, "pass-to-pass-test-ids": []},
            {"step": 1, "pass-to-pass-test-ids": ["test0"]},
            {"step": 2, "pass-to-pass-test-ids": ["test0", "test1"]}
        ]
        with open(input_dir / "pass-to-pass-test-ids.json", "w") as f:
            json.dump(pass_to_pass_test_ids, f)

        # Create reference-patches.json
        reference_patches = [
            {"step": 0, "reference-patch": "patch0"},
            {"step": 1, "reference-patch": "patch1"},
            {"step": 2, "reference-patch": "patch2"}
        ]
        with open(input_dir / "reference-patches.json", "w") as f:
            json.dump(reference_patches, f)

        return input_dir

    def test_merge_to_jsonl(self, mock_input_dir, tmp_path):
        """Test merging JSON files to a JSONL file."""
        output_file = tmp_path / "output.jsonl"
        repository = "test/repo"

        # Call the function under test
        merge_to_jsonl(repository, mock_input_dir, output_file)

        # Check that the output file exists
        assert output_file.exists()

        # Read the output file and check its contents
        with open(output_file, "r") as f:
            lines = f.readlines()

        # We should have 2 lines (steps 0 and 2, as step 1 has flag=False)
        assert len(lines) == 2

        # Parse the lines and check their contents
        data = [json.loads(line) for line in lines]

        # Check the first item (step 0)
        assert data[0]["instance_id"] == "test__--__repo-dev-1"
        assert data[0]["repo"] == "test/repo"
        assert data[0]["problem_statement"] == "Spec 0"
        assert data[0]["base_commit"] == "base0"
        assert data[0]["reference_commit"] == "ref0"
        assert data[0]["patch"] == "patch0"
        assert data[0]["fail_to_pass"] == ["test0"]
        assert data[0]["pass_to_pass"] == []

        # Check the second item (step 2)
        assert data[1]["instance_id"] == "test__--__repo-dev-2"
        assert data[1]["repo"] == "test/repo"
        assert data[1]["problem_statement"] == "Spec 2"
        assert data[1]["base_commit"] == "base2"
        assert data[1]["reference_commit"] == "ref2"
        assert data[1]["patch"] == "patch2"
        assert data[1]["fail_to_pass"] == ["test2"]
        assert data[1]["pass_to_pass"] == ["test0", "test1"]
