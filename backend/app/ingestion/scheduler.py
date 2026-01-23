"""
Scheduler for periodic data updates and ingestion tasks.
"""
from typing import Callable
from datetime import datetime, timedelta, timezone
from app.core.logging import logger


class DataScheduler:
    """Scheduler for periodic data ingestion and updates."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.tasks = []
        logger.info("DataScheduler initialized")
    
    def schedule_task(
        self,
        task_func: Callable,
        interval_minutes: int,
        task_name: str = "unnamed_task"
    ):
        """
        Schedule a task to run periodically.
        
        Args:
            task_func: Function to execute
            interval_minutes: Interval between executions in minutes
            task_name: Name identifier for the task
        """
        task = {
            "name": task_name,
            "function": task_func,
            "interval": interval_minutes,
            "last_run": None,
            "next_run": datetime.now(timezone.utc)
        }
        self.tasks.append(task)
        logger.info(f"Scheduled task: {task_name} (interval: {interval_minutes} minutes)")
    
    def run_pending(self):
        """Execute any tasks that are due to run."""
        current_time = datetime.now(timezone.utc)
        
        for task in self.tasks:
            if task["next_run"] <= current_time:
                try:
                    logger.info(f"Running scheduled task: {task['name']}")
                    task["function"]()
                    task["last_run"] = current_time
                    task["next_run"] = current_time + timedelta(minutes=task["interval"])
                    logger.info(f"Task completed: {task['name']}")
                except Exception as e:
                    logger.error(f"Error running task {task['name']}: {str(e)}")
