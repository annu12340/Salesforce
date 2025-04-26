import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Event handler for messages
@app.message("hello")
def message_hello(message, say):
    user = message['user']
    say(f"Hi there, <@{user}>!")

# Command handler for /support
@app.command("/support")
def handle_support_command(ack, body, say):
    ack()
    user_id = body["user_id"]
    say(f"<@{user_id}> How can I help you today?")

# Event handler for app mentions
@app.event("app_mention")
def handle_mentions(event, say):
    say(f"Thanks for mentioning me! How can I assist you?")

# Error handler
@app.error
def handle_errors(error):
    print(f"Error: {error}")

if __name__ == "__main__":
    handler = SocketModeHandler(app_token=os.environ.get("SLACK_APP_TOKEN"), app=app)
    handler.start() 