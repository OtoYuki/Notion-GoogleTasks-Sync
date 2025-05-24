# Notion & Google Tasks Two-Way Sync

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Managing tasks across different platforms can be a real headache. I found myself constantly bouncing between Notion, with its powerful database features, and Google Tasks, which I love for its simplicity and integration with the rest of Google's services. I realized I was wasting time and sometimes even missing things because my to-do lists weren't in sync.

That's why I decided to build this tool. It's a personal project born out of a genuine need to bridge that gap and automate the synchronization process. It's been a fun challenge to develop, and I'm excited about how it streamlines my own workflow. My hope is that it can help others as well!

---

## What It Does

This Python application provides a **robust two-way sync** between your Notion database and Google Tasks. This means if you make a change in Notion, it'll show up in Google Tasks, and vice-versa. Your tasks will always be up-to-date, no matter which platform you're using.

### Key Features

* **Two-Way Synchronization:** Changes made in Notion appear in Google Tasks, and vice-versa.
* **Smart Sync Logic:** It intelligently detects new tasks and creates them on the other platform. It also updates existing tasks based on the most recent changes (using `last_edited_time`). It handles task titles, completion statuses, and due dates.
* **Persistent State:** The tool remembers which tasks have been synced to avoid duplicates and ensure consistency across syncs.
* **Google Tasks List Selection:** You can specify which Google Tasks list you want to sync with.
* **Flexible Sync Modes:**
  * **One-Time Sync:** Run a single synchronization pass.
  * **Continuous Sync:** Run the script in the background to periodically sync tasks at a configurable interval.
* **Secure Credential Management:** It uses a `.env` file for API keys, and OAuth tokens are stored locally and securely.
* **Clear Logging:** Provides informative output during the synchronization process.

---

## 🛠️ Tech Stack

* **Python 3.9+**
* **Notion API:** via the `notion-client` library.
* **Google Tasks API:** via the `google-api-python-client` and `google-auth-oauthlib` libraries.
* **Environment Variables:** `python-dotenv` for managing API keys and secrets.
* **Data Handling:** Standard Python libraries for JSON, datetime, and file operations.

---

## 🧠 How It Works

Under the hood, the application does a few things to keep your tasks in sync:

1. **Initialization:** It loads your API keys and client secrets from a `.env` file and sets up connections to both Notion and Google Tasks. For Google Tasks, it uses an OAuth 2.0 flow to securely authenticate, storing tokens locally for future use.
2. **State Management:** A `sync_state.json` file (stored in `~/.notion_google_sync/`) is used to keep track of which Notion pages correspond to which Google Tasks, and when the last successful sync occurred. This helps in identifying new versus existing tasks and prevents redundant operations.
3. **Fetching and Modeling Tasks:** It fetches tasks from both your Notion database and your chosen Google Tasks list. Both Notion pages and Google Tasks are then converted into a common, unified `Task` object defined in `src/models.py`. This makes it much easier to compare and update tasks.
4. **Synchronization Logic (`src/sync.py`):**
    * **Notion to Google:** Each task from Notion is checked. If it's new (not found in the sync state or Google Tasks), it's created in Google Tasks. If it already exists on both platforms, the `last_edited_time` is compared. If the Notion task is newer, the Google Task is updated.
    * **Google to Notion:** Similarly, each task from Google Tasks is checked. If it's new, it's created in Notion. If it exists on both, and the Google Task is newer, the Notion task is updated.
5. **Updating Sync State:** After everything is processed, the `sync_state.json` file is updated with any new mappings and the current timestamp.

---

## 🚀 Getting Started

Here's how you can get this Notion & Google Tasks Sync application up and running on your computer.

### Prerequisites

You'll need a few things set up before you start:

* **Python 3.9 or higher** installed.
* A **Notion account and an integration token**. You can create a Notion integration [here](https://www.notion.so/my-integrations). Once created, make sure to share your target Notion database with your integration.
* Your Notion database should have at least these properties (you can customize these later if you're comfortable with the code):
  * `Task Name` (a Title property)
  * `Status` (a Select property with options like "Tackling", "Dusted" - "Dusted" signifies completion)
  * `Due Date` (a Date property)
* A **Google Cloud Platform project with the Google Tasks API enabled**. You'll need to create OAuth 2.0 credentials (Client ID and Client Secret) for a "Desktop app". Also, ensure these redirect URIs are added to your OAuth 2.0 Client ID in the Google Cloud Console:
  * `http://localhost:8080`
  * `http://127.0.0.1:8080`

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/OtoYuki/Notion-GoogleTasks-Sync.git
    cd notion_google_sync
    ```

2. **Create and activate a virtual environment (highly recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**
    Create a file named `.env` in the root directory of the project (e.g., `/home/sire/notion_google_sync/.env`) and add your credentials:

    ```env
    # filepath: /home/sire/notion_google_sync/.env
    NOTION_API_KEY="your_notion_api_key_here"
    NOTION_DATABASE_ID="your_notion_database_id_here" # The ID of the Notion database you want to sync

    CLIENT_ID="your_google_client_id_here"
    CLIENT_SECRET="your_google_client_secret_here"
    ```

    You can find your `NOTION_DATABASE_ID` from the URL of your Notion database page; it's the long string of characters.

---

## ⚙️ Usage

You'll run the script from your command line using `main.py`.

### First-Time Google Authentication

The very first time you run the script, it will need to authenticate with Google Tasks:

1. A message will appear in your console, possibly attempting to open a browser or providing a URL.
2. Follow the instructions to authorize the application to access your Google Tasks.
3. If a URL is provided, copy and paste it into a browser on any device.
4. After granting permissions, you might be redirected to a `localhost` URL or shown an authorization code.
5. If a code is shown, paste it back into the terminal when prompted.
6. Once authenticated, your credentials will be stored locally in `~/.notion_google_sync/token.pickle` for future use.

### Running the Sync

* **Perform a one-time sync:**

    ```bash
    python main.py --one-time
    ```

* **Run in continuous sync mode (e.g., sync every 10 minutes):**

    ```bash
    python main.py --interval 600
    ```

    The default interval is 300 seconds (5 minutes). You can press `Ctrl+C` to stop continuous sync.

* **Specify a different Google Tasks list:**
    By default, it syncs with a Google Tasks list named "My Tasks". If your list has a different name:

    ```bash
    python main.py --task-list "Your Custom Task List Name"
    ```

### Command-Line Arguments

* `--task-list <NAME>`: Name of the Google Tasks list to sync with (default: "My Tasks").
* `--one-time`: Perform a one-time sync and exit.
* `--interval <SECONDS>`: Sync interval in seconds for continuous mode (default: 300).

---

## 🏗️ Project Structure

Here's a quick look at how the project is organized:

notion_google_sync/
├── .env                  # Stores API keys and secrets (you create this)
├── .gitignore            # Specifies intentionally untracked files
├── README.md             # This file
├── requirements.txt      # Project dependencies
├── main.py               # Main entry point for the application
└── src/
    ├── __init__.py
    ├── config.py         # Loads and validates environment variables
    ├── google_client.py  # Handles Google Tasks API interactions and OAuth
    ├── models.py         # Defines the unified Task data model
    ├── notion_client.py  # Handles Notion API interactions
    └── sync.py           # Contains the core synchronization logic

---

## 💡 Future Ideas

This tool is already quite useful, but I have a few ideas for making it even better down the line:

* **More Granular Property Mapping:** Allowing users to configure custom mappings for more Notion properties, like priority or tags.
* **Deletion Sync:** An option to synchronize deletions (currently, tasks are only created/updated).
* **Better Error Handling:** More robust error handling and retry mechanisms for API calls.
* **Simple Interface:** Maybe a basic graphical or web interface for easier setup and management.
* **Easier Installation:** Packaging the application for simpler installation, perhaps using PyInstaller or Docker.
* **Comprehensive Unit and Integration Tests.**

---

## 🤝 Contributing

This is currently a personal project, but I'm always open to feedback and suggestions! If you have ideas for improvements or run into any issues, please feel free to open an issue on the GitHub repository.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details (if you add one).
