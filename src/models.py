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

        # Extract the Notion properties (These need to be adjusted based on your Notion database schema)
        title = (
            properties.get("Task Name", {})
            .get("title", [{}])[0]
            .get("text", {})
            .get("content", "")
        )
        completed = (
            properties.get("Status", {}).get("select", {}).get("name") == "Completed"
        )

        # Parsing the due date if available
        due_date = None
        if due_date_str := properties.get("Due Date", {}).get("date", {}).get("start"):
            try:
                due_date = datetime.fromisoformat(due_date_str)
            except ValueError:
                pass

        # Extracting the description if available
        description = ""
        # Ain't got description in Notion Tasks database

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
