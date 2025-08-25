# task_service.py
from typing import List, Dict, Optional
from sqlmodel import select
from .db import Session, Task, Project, TaskStatus

class TaskService:
    """Simple data-access layer for Projects/Tasks."""
    def __init__(self, session_factory):
        # session_factory: () -> Session
        self._session_factory = session_factory

    # --- read helpers ---
    def list_projects_with_tasks(
        self,
        include_hidden: bool = False,
        status_filter: Optional[List[TaskStatus]] = None,
    ) -> List[Dict]:
        with self._session_factory() as s:
            projects = s.exec(select(Project)).all()
            out = []
            for p in projects:
                tasks_q = select(Task).where(Task.project_id == p.id).order_by(Task.order_index.asc())
                tasks = s.exec(tasks_q).all()
                rows = []
                for t in tasks:
                    if not include_hidden and t.hidden:
                        continue
                    if status_filter and t.status not in status_filter:
                        continue
                    rows.append({
                        "project_key": p.key,
                        "task_key": t.key,
                        "name": t.name,
                        "description": t.description,
                        "status": t.status.value,
                        "hidden": t.hidden,
                        "order_index": t.order_index,
                    })
                out.append({
                    "project_key": p.key,
                    "project_name": p.name,
                    "project_desc": p.description,
                    "tasks": rows
                })
            return out

    # --- mutation helpers ---
    def set_task_status(self, project_key: str, task_key: str, status: TaskStatus) -> bool:
        with self._session_factory() as s:
            p = s.exec(select(Project).where(Project.key == project_key)).first()
            if not p:
                return False
            t = s.exec(select(Task).where(Task.project_id == p.id, Task.key == task_key)).first()
            if not t:
                return False

            # reveal when moving to in_progress/completed
            t.status = status
            if status in (TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED):
                t.hidden = False
            # if completed, optionally auto‑reveal the *next* task
            if status == TaskStatus.COMPLETED:
                nxt = s.exec(
                    select(Task)
                    .where(Task.project_id == p.id, Task.order_index > t.order_index)
                    .order_by(Task.order_index.asc())
                ).first()
                if nxt and nxt.hidden:
                    nxt.hidden = False
                    if nxt.status == TaskStatus.UNASSIGNED:
                        nxt.status = TaskStatus.IN_PROGRESS

            s.add(t)
            s.commit()
            return True
