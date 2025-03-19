import json
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from pathlib import Path

from .models import Task
from .notion_client import NotionTaskClient
from .google_client import GoogleTaskClient


class TaskSynchronizer:
    """
    Handles synchronization of tasks between Notion and Google Tasks
    """

    # Path to store sync state
    SYNC_STATE_PATH = Path.home() / ".notion_google_sync" / "sync_state.json"

    def __init__(
        self, notion_client: NotionTaskClient, google_client: GoogleTaskClient
    ):
        self.notion_client = notion_client
        self.google_client = google_client
        self.sync_state = self._load_sync_state()

    def _load_sync_state(self) -> Dict:
        """Load sync state from file or create a new one"""
        # Create directory for sync state if it doesn't exist
        self.SYNC_STATE_PATH.parent.mkdir(exist_ok=True, parents=True)

        if self.SYNC_STATE_PATH.exists():
            try:
                with open(self.SYNC_STATE_PATH, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading sync state: {e}")

        # Return empty state if file doesn't exist or there was an error
        return {
            "notion_to_google": {},  # Maps notion_id -> google_id
            "google_to_notion": {},  # Maps google_id -> notion_id
            "last_sync": None,
        }

    def _save_sync_state(self):
        """Save sync state to file"""
        with open(self.SYNC_STATE_PATH, "w") as f:
            json.dump(self.sync_state, f)

    def sync_tasks(self) -> Tuple[int, int, int]:
        """
        Synchronize tasks between Notion and Google Tasks
        Returns counts of tasks created, updated, and failed
        """
        print("Starting synchronization...")

        # Initialize counters
        created = 0
        updated = 0
        failed = 0

        # Fetch tasks from both systems
        notion_tasks = self.notion_client.fetch_tasks()
        google_tasks = self.google_client.fetch_tasks()

        # Create mappings for easier lookup
        notion_tasks_by_id = {
            task.notion_id: task for task in notion_tasks if task.notion_id
        }
        google_tasks_by_id = {
            task.google_id: task for task in google_tasks if task.google_id
        }

        # Process tasks from Notion to Google
        for notion_task in notion_tasks:
            try:
                # Skip tasks without a Notion ID (should never happen)
                if not notion_task.notion_id:
                    continue

                # Check if task is already synced
                google_id = self.sync_state["notion_to_google"].get(
                    notion_task.notion_id
                )

                if google_id and google_id in google_tasks_by_id:
                    # Task exists in both systems, check if update needed
                    google_task = google_tasks_by_id[google_id]

                    # Only update if Notion task is newer
                    if notion_task.last_edited_time and google_task.last_edited_time:
                        if notion_task.last_edited_time > google_task.last_edited_time:
                            # Update Google task with Notion data
                            notion_task.google_id = google_id
                            self.google_client.update_task(notion_task)
                            updated += 1
                    else:
                        # If we can't determine which is newer, update anyway
                        notion_task.google_id = google_id
                        self.google_client.update_task(notion_task)
                        updated += 1
                else:
                    # Task doesn't exist in Google, create it
                    created_task = self.google_client.create_task(notion_task)

                    # Update sync state
                    self.sync_state["notion_to_google"][
                        notion_task.notion_id
                    ] = created_task.google_id
                    self.sync_state["google_to_notion"][
                        created_task.google_id
                    ] = notion_task.notion_id
                    created += 1
            except Exception as e:
                print(
                    f"Error syncing Notion task {notion_task.notion_id} to Google: {e}"
                )
                failed += 1

        # Process tasks from Google to Notion
        for google_task in google_tasks:
            try:
                # Skip tasks without a Google ID (should never happen)
                if not google_task.google_id:
                    continue

                # Check if task is already synced
                notion_id = self.sync_state["google_to_notion"].get(
                    google_task.google_id
                )

                if notion_id and notion_id in notion_tasks_by_id:
                    # Task exists in both systems, check if update needed
                    notion_task = notion_tasks_by_id[notion_id]

                    # Only update if Google task is newer
                    if google_task.last_edited_time and notion_task.last_edited_time:
                        if google_task.last_edited_time > notion_task.last_edited_time:
                            # Update Notion task with Google data
                            google_task.notion_id = notion_id
                            self.notion_client.update_task(google_task)
                            updated += 1
                    else:
                        # If we can't determine which is newer, update anyway
                        google_task.notion_id = notion_id
                        self.notion_client.update_task(google_task)
                        updated += 1
                else:
                    # Task doesn't exist in Notion, create it
                    created_task = self.notion_client.create_task(google_task)

                    # Update sync state
                    self.sync_state["google_to_notion"][
                        google_task.google_id
                    ] = created_task.notion_id
                    self.sync_state["notion_to_google"][
                        created_task.notion_id
                    ] = google_task.google_id
                    created += 1
            except Exception as e:
                print(
                    f"Error syncing Google task {google_task.google_id} to Notion: {e}"
                )
                failed += 1

        # Update last sync time
        self.sync_state["last_sync"] = datetime.now().isoformat()

        # Save sync state
        self._save_sync_state()

        print(
            f"Synchronization completed: {created} created, {updated} updated, {failed} failed"
        )
        return created, updated, failed
