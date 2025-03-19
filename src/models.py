from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Task:
    """
    This is a unified class model that represents a task from either Notion or Google Tasks.
    """

    title: str
    completed: bool = False
    due_date: Optional[datetime] = None
    description: Optional[str] = None

    # The ID's to track the task in both systems
    notion_id: Optional[str] = None
    google_id: Optional[str] = None

    # Some additional metadata
    last_edited_time: Optional[datetime] = None

    @classmethod
    def from_notion(cls, notion_page: Dict[str, Any]) -> "Task":
        """
        Create a Task instance from a Notion page object
        """
        properties = notion_page.get("properties", {})

        # Extract the Notion properties based on your actual database schema
        title = (
            properties.get("Task Name", {})
            .get("title", [{}])[0]
            .get("text", {})
            .get("content", "")
        )

        # Check status - completed if "Dusted", in progress otherwise
        status = properties.get("Status", {}).get("select", {}).get("name", "")
        completed = status == "Dusted"  # "Dusted" means completed

        # Parsing the due date if available
        due_date = None
        if due_date_str := properties.get("Due Date", {}).get("date", {}).get("start"):
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                pass

        # Extracting the description if available (not in your Notion schema)
        description = ""

        return cls(
            title=title,
            completed=completed,
            due_date=due_date,
            description=description,
            notion_id=notion_page.get("id"),
            last_edited_time=datetime.fromisoformat(
                notion_page.get("last_edited_time", "")
            ),
        )

    @classmethod
    def from_google(cls, google_task: Dict[str, Any]) -> "Task":
        """
        Create a Task instance from a Google Task object
        """
        title = google_task.get("title", "")
        completed = google_task.get("status") == "completed"

        # Parse due date if available
        due_date = None
        if due_date_str := google_task.get("due"):
            try:
                due_date = datetime.fromisoformat(due_date_str.replace("Z", "+00:00"))
            except ValueError:
                pass

        return cls(
            title=title,
            completed=completed,
            due_date=due_date,
            description=google_task.get("notes", ""),
            google_id=google_task.get("id"),
            last_edited_time=datetime.fromisoformat(
                google_task.get("updated", "").replace("Z", "+00:00")
            ),
        )

    def to_notion_properties(self) -> Dict[str, Any]:
        """
        Convert task to Notion page properties format
        """
        # Use your actual Notion property names and values
        properties = {
            "Task Name": {"title": [{"text": {"content": self.title}}]},
            "Status": {"select": {"name": "Dusted" if self.completed else "Tackling"}},
        }

        if self.due_date:
            properties["Due Date"] = {"date": {"start": self.due_date.isoformat()}}

        return properties

    def to_google_task(self) -> Dict[str, Any]:
        """
        Convert task to Google Tasks format
        """
        task_data = {
            "title": self.title,
            "status": "completed" if self.completed else "needsAction",
        }

        if self.description:
            task_data["notes"] = self.description

        if self.due_date:
            # Google Tasks expects RFC 3339 timestamp
            task_data["due"] = self.due_date.isoformat() + "Z"

        return task_data
