import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Slack API tokens
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")

# Channel IDs
CENTRAL_CASE_CHANNEL_ID = os.environ.get("CENTRAL_CASE_CHANNEL_ID")
NEW_LEADS_CHANNEL_ID = os.environ.get("NEW_LEADS_CHANNEL_ID")
SUPPORT_CHANNEL_ID = os.environ.get("SUPPORT_CHANNEL_ID")
SALES_CHANNEL_ID = os.environ.get("SALES_CHANNEL_ID")
ENGINEERING_CHANNEL_ID = os.environ.get("ENGINEERING_CHANNEL_ID")

# App configuration
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO") 