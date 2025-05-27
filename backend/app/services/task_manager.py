# backend/app/services/task_manager.py

import asyncio
import uuid
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime, timezone
from dataclasses import dataclass
import json

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    id: str
    status: TaskStatus
    progress: float
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)

class TaskManager:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        
    def create_task(self) -> str:
        """Create a new task and return its ID."""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            status=TaskStatus.PENDING,
            progress=0.0
        )
        self._tasks[task_id] = task
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    def update_task_progress(self, task_id: str, progress: float):
        """Update task progress (0.0 to 1.0)."""
        if task_id in self._tasks:
            self._tasks[task_id].progress = progress
    
    def mark_task_running(self, task_id: str):
        """Mark task as running."""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
    
    def mark_task_completed(self, task_id: str, result: Any = None):
        """Mark task as completed with optional result."""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.COMPLETED
            task.progress = 1.0
            task.result = result
            task.completed_at = datetime.now(timezone.utc)
    
    def mark_task_failed(self, task_id: str, error: str):
        """Mark task as failed with error message."""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.status = TaskStatus.FAILED
            task.error = error
            task.completed_at = datetime.now(timezone.utc)
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """Remove tasks older than max_age_hours."""
        cutoff = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
        to_remove = []
        
        for task_id, task in self._tasks.items():
            if task.created_at.timestamp() < cutoff:
                to_remove.append(task_id)
        
        for task_id in to_remove:
            del self._tasks[task_id]
    
    def get_task_dict(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task as dictionary for JSON serialization."""
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "status": task.status.value,
            "progress": task.progress,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }

# Global task manager instance
task_manager = TaskManager()
