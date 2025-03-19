import os
import json
import pickle
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .config import CLIENT_ID, CLIENT_SECRET
from .models import Task


class GoogleTaskClient:
    """Client to interact with Google Tasks API"""

    # Define the scopes our application needs
    SCOPES = ["https://www.googleapis.com/auth/tasks"]
    # Path to store credentials
    TOKEN_PATH = Path.home() / ".notion_google_sync" / "token.pickle"

    def __init__(self, task_list_name: str = "My Tasks"):
        """Initialize Google Tasks client with optional task list name"""
        self.task_list_name = task_list_name
        self.task_list_id = None
        self.service = self._authenticate()

    def _authenticate(self) -> Any:
        """Authenticate with Google and return a service object"""
        creds = None

        # Create directory for token if it doesn't exist
        self.TOKEN_PATH.parent.mkdir(exist_ok=True, parents=True)

        # Load token from pickle file if it exists
        if self.TOKEN_PATH.exists():
            with open(self.TOKEN_PATH, "rb") as token:
                creds = pickle.load(token)

        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Create OAuth flow - using client secrets
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": CLIENT_ID,
                            "client_secret": CLIENT_SECRET,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "redirect_uris": [
                                "http://localhost",
                                "urn:ietf:wg:oauth:2.0:oob",
                            ],
                        }
                    },
                    self.SCOPES,
                )

                # Run the OAuth flow
                creds = flow.run_local_server(port=0)

                # Save credentials for future use
                with open(self.TOKEN_PATH, "wb") as token:
                    pickle.dump(creds, token)

        # Build the service object
        service = build("tasks", "v1", credentials=creds)
        return service

    def _get_task_list_id(self) -> str:
        """Get the ID of the task list to use, creating it if needed"""
        if self.task_list_id:
            return self.task_list_id

        # List all task lists
        results = self.service.tasklists().list().execute()
        task_lists = results.get("items", [])

        # Find the desired task list
        for task_list in task_lists:
            if task_list["title"] == self.task_list_name:
                self.task_list_id = task_list["id"]
                return self.task_list_id

        # If no task list was found, create a new one
        new_list = (
            self.service.tasklists()
            .insert(body={"title": self.task_list_name})
            .execute()
        )

        self.task_list_id = new_list["id"]
        return self.task_list_id

    def fetch_tasks(self) -> List[Task]:
        """Fetch all tasks from Google Tasks"""
        task_list_id = self._get_task_list_id()
        results = self.service.tasks().list(tasklist=task_list_id).execute()
        tasks = []

        for item in results.get("items", []):
            try:
                task = Task.from_google(item)
                tasks.append(task)
            except Exception as e:
                print(f"Error processing Google task {item.get('id')}: {e}")

        return tasks

    def create_task(self, task: Task) -> Task:
        """Create a new task in Google Tasks"""
        task_list_id = self._get_task_list_id()
        task_data = task.to_google_task()

        # Create the task
        result = (
            self.service.tasks().insert(tasklist=task_list_id, body=task_data).execute()
        )

        # Update task with Google ID
        task.google_id = result["id"]
        if "updated" in result:
            task.last_edited_time = datetime.fromisoformat(
                result["updated"].replace("Z", "+00:00")
            )

        return task

    def update_task(self, task: Task) -> Task:
        """Update an existing task in Google Tasks"""
        if not task.google_id:
            raise ValueError("Cannot update task without a Google ID")

        task_list_id = self._get_task_list_id()
        task_data = task.to_google_task()

        # Update the task
        result = (
            self.service.tasks()
            .update(tasklist=task_list_id, task=task.google_id, body=task_data)
            .execute()
        )

        # Update last edited time
        if "updated" in result:
            task.last_edited_time = datetime.fromisoformat(
                result["updated"].replace("Z", "+00:00")
            )

        return task

    def get_task_by_id(self, google_id: str) -> Optional[Task]:
        """Get a task by its Google ID"""
        task_list_id = self._get_task_list_id()

        try:
            result = (
                self.service.tasks()
                .get(tasklist=task_list_id, task=google_id)
                .execute()
            )

            return Task.from_google(result)
        except Exception as e:
            print(f"Error retrieving Google task: {e}")
            return None
