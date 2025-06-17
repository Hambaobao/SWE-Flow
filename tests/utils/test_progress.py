from rich.progress import Progress
from sweflow.utils.progress import create_progress


def test_create_progress():
    """Test that create_progress returns a valid Progress instance."""
    progress = create_progress()
    
    # Check that the returned object is a Progress instance
    assert isinstance(progress, Progress)
    
    # Check that the Progress instance has the expected columns
    column_types = [type(column) for column in progress.columns]
    
    # We don't need to check the exact column types, just that there are the expected number
    # and that the Progress instance is properly configured
    assert len(column_types) == 6  # TextColumn, BarColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
    
    # Test that we can add a task to the progress bar
    with progress:
        task_id = progress.add_task("Test task", total=100)
        assert task_id is not None
        
        # Test that we can update the progress
        progress.update(task_id, advance=10)
        task = progress.tasks[0]
        assert task.completed == 10
