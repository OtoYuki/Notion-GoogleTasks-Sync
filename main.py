import argparse
import sys
import time
from datetime import datetime

from src.notion_client import NotionTaskClient
from src.google_client import GoogleTaskClient
from src.sync import TaskSynchronizer


import logging

logging.basicConfig(level=logging.INFO)


def main():
    """Main entry point for the Notion-Google Tasks synchronization"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Synchronize tasks between Notion and Google Tasks"
    )
    parser.add_argument(
        "--task-list",
        default="My Tasks",
        help="Name of the Google Tasks list to sync with (default: 'My Tasks')",
    )
    parser.add_argument(
        "--one-time",
        action="store_true",
        help="Perform a one-time sync and exit (default: continuous sync)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,  # 5 minutes
        help="Sync interval in seconds (default: 300)",
    )
    args = parser.parse_args()

    try:
        # Initialize clients
        print("Initializing clients...")
        notion_client = NotionTaskClient()
        google_client = GoogleTaskClient(task_list_name=args.task_list)
        # Add after creating clients in main.py
        print("Fetching Notion tasks...")
        notion_tasks = notion_client.fetch_tasks()
        print(f"Found {len(notion_tasks)} tasks in Notion")

        print("Fetching Google tasks...")
        google_tasks = google_client.fetch_tasks()
        print(f"Found {len(google_tasks)} tasks in Google")

        # Create synchronizer
        synchronizer = TaskSynchronizer(notion_client, google_client)

        if args.one_time:
            # Perform one-time sync
            print(
                f"Starting one-time sync at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            synchronizer.sync_tasks()
        else:
            # Continuous sync
            print(f"Starting continuous sync every {args.interval} seconds")
            print("Press Ctrl+C to stop")

            try:
                while True:
                    print(f"Syncing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    synchronizer.sync_tasks()
                    print(f"Next sync in {args.interval} seconds")
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                print("\nSync stopped by user")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
