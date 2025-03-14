import os
from dotenv import load_dotenv

# Loading the environment variables from the .env file
load_dotenv()

# Notion Credentials
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Google Credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Basic Validation
if not all([NOTION_API_KEY, NOTION_DATABASE_ID, CLIENT_ID, CLIENT_SECRET]):
    raise ValueError("Please set all required environment variables in the .env file.")
