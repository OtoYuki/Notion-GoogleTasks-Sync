from typing import List, Dict, Any, Optional
from notion_client import Client
from datetime import datetime

from .config import NOTION_API_KEY, NOTION_DATABASE_ID
from .models import Task


class NotionTaskClient:
    """The Client to interact with the Notion Tasks Database"""

    def __init__(self):
        self.client = Client(auth=NOTION_API_KEY)
        self.database_id = NOTION_DATABASE_ID

    def fetch_tasks(self) -> List[Task]:
        """
        Fetch tasks from the Notion database and return them as Task instances.
        """
        tasks = []

        # Query the Notion database
        response = self.client.databases.query(database_id=self.database_id)

        # Convert each page into a Task object
        for page in response.get("results", []):
            try:
                task = Task.from_notion(page)
                tasks.append(task)
            except Exception as e:
                print(f"Error processing page {page.get('id')}: {e}")

        return tasks

    def create_task(self, task: Task) -> Task:
        """Create a new task in Notion"""
        properties = task.to_notion_properties()

        # Create the page in Notion
        response = self.client.pages.create(
            parent={"database_id": self.database_id}, properties=properties
        )

        # Update the task with the Notion ID
        task.notion_id = response["id"]
        task.last_edited_time = datetime.fromisoformat(response["last_edited_time"])

        return task

    def update_task(self, task: Task) -> Task:
        """Update an existing task in Notion"""
        if not task.notion_id:
            raise ValueError("Cannot update task without a Notion ID")

        properties = task.to_notion_properties()

        # Update the page in Notion
        response = self.client.pages.update(
            page_id=task.notion_id, properties=properties
        )

        # Update the task with the new last_edited_time
        task.last_edited_time = datetime.fromisoformat(response["last_edited_time"])

        return task

    def get_task_by_id(self, notion_id: str) -> Optional[Task]:
        """Get a task by its Notion ID"""
        try:
            response = self.client.pages.retrieve(page_id=notion_id)
            return Task.from_notion(response)
        except Exception as e:
            print(f"Error retrieving Notion page: {e}")
            return None
