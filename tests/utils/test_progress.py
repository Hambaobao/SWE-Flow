from rich.progress import Progress
from sweflow.utils.progress import create_progress


def test_create_progress():
    """Test that create_progress returns a valid Progress instance."""
    progress = create_progress()
    assert isinstance(progress, Progress)
    
    # Check that the progress bar has the expected columns
    assert len(progress.columns) == 6
    
    # Test that we can use the progress bar
    with progress:
        task = progress.add_task("[bold blue]Processing...", total=10)
        for i in range(10):
            progress.update(task, advance=1)
        
        # Check that the task is completed
        assert progress.tasks[0].completed == 10