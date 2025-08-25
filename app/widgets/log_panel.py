# log_panel.py
from typing import List
from PyQt5.QtWidgets import QTextEdit
from .base import BasePanelWidget
from ..db import TaskStatus  # for convenience / type safety

class LogPanel(BasePanelWidget):
    def __init__(self, panel_id, title, bg, bus, controller):
        super().__init__(panel_id, title, bg, bus, controller)
        self.view = QTextEdit()
        self.view.setReadOnly(True)
        self.view.setStyleSheet("background: rgba(0,0,0,0.25); color: #e9f0f8;")
        self.body_layout.addWidget(self.view, 1)
        # Subscribe to logs
        self.bus.log.connect(self.append_line)

    def append_line(self, text: str):
        self.view.append(text)

    # ---------- NEW: Project/Task helpers ----------
    def _write_projects(self, data):
        # Display format:
        # Project Name
        #   - Task Name: brief description [status]
        for proj in data:
            tasks = proj.get("tasks", [])
            if not tasks:
                continue
            self.append_line(f"{proj['project_name']}")
            for t in tasks:
                desc = t.get("description", "")
                status = t.get("status", "")
                self.append_line(f"  - {t['name']}: {desc} [{status}]")

    def show_active_projects(self):
        """Show projects that have visible tasks in progress."""
        svc = self.controller.tasks
        rows = svc.list_projects_with_tasks(include_hidden=False, status_filter=[TaskStatus.IN_PROGRESS])
        self.append_line("[projects] Active projects & in‑progress tasks:")
        self._write_projects(rows)

    def show_completed_tasks(self):
        """Show all completed (visible) tasks grouped by project."""
        svc = self.controller.tasks
        rows = svc.list_projects_with_tasks(include_hidden=False, status_filter=[TaskStatus.COMPLETED])
        self.append_line("[projects] Completed tasks:")
        self._write_projects(rows)

    def set_task_status(self, project_key: str, task_key: str, status: str):
        """
        Change a task's status: 'Unassigned'|'In Progress'|'Completed'.
        Also reveals tasks as they become relevant.
        """
        mapping = {
            "Unassigned": TaskStatus.UNASSIGNED,
            "In Progress": TaskStatus.IN_PROGRESS,
            "Completed": TaskStatus.COMPLETED,
            # allow lowercase too
            "unassigned": TaskStatus.UNASSIGNED,
            "in_progress": TaskStatus.IN_PROGRESS,
            "completed": TaskStatus.COMPLETED,
        }
        s = mapping.get(status, None)
        if s is None:
            self.bus.log.emit(f"[projects] Unknown status: {status}")
            return False

        ok = self.controller.tasks.set_task_status(project_key, task_key, s)
        if ok:
            self.bus.log.emit(f"[projects] {project_key}.{task_key} -> {s.value}")
        else:
            self.bus.log.emit(f"[projects] Could not update {project_key}.{task_key}")
        return ok
