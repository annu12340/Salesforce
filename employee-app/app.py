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

# Monitor messages in central_case channel
@app.message()
def handle_central_case_messages(message, say, client):
    # Check if the message is from the central_case channel
    if message.get("channel") == os.environ.get("CENTRAL_CASE_CHANNEL_ID"):
        # Parse the message content
        msg_text = message.get("text", "")
        user_id = message.get("user")
        timestamp = message.get("ts")
        
        # Create interactive buttons for team hand-off
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Case from <@{user_id}>*:\n{msg_text}"
                }
            },
            {
                "type": "actions",
                "block_id": f"handoff_buttons_{timestamp}",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Hand-off to Support"},
                        "value": f"support_{timestamp}",
                        "action_id": "handoff_support"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Hand-off to Sales"},
                        "value": f"sales_{timestamp}",
                        "action_id": "handoff_sales"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Hand-off to Engineering"},
                        "value": f"engineering_{timestamp}",
                        "action_id": "handoff_engineering"
                    }
                ]
            }
        ]
        
        # Send response as a thread to the original message
        say(blocks=blocks, thread_ts=timestamp)

# Monitor messages in new_leads channel
@app.message()
def handle_new_leads_messages(message, say):
    # Check if the message is from the new_leads channel
    if message.get("channel") == os.environ.get("NEW_LEADS_CHANNEL_ID"):
        # Process new leads messages
        user_id = message.get("user")
        timestamp = message.get("ts")
        # Send response as a thread to the original message
        say(f"New lead received from <@{user_id}>! Processing...", thread_ts=timestamp)

# Handle button actions for team hand-offs
@app.action(["handoff_support", "handoff_sales", "handoff_engineering"])
def handle_handoff_action(ack, body, client):
    # Acknowledge the button click
    ack()
    
    # Extract information
    user_id = body["user"]["id"]
    action_id = body["actions"][0]["action_id"]
    value = body["actions"][0]["value"]
    
    # Get original message timestamp
    timestamp = value.split("_")[1]
    
    # Determine target channel based on action
    target_channel = ""
    team_name = ""
    
    if action_id == "handoff_support":
        target_channel = os.environ.get("SUPPORT_CHANNEL_ID")
        team_name = "Support"
    elif action_id == "handoff_sales":
        target_channel = os.environ.get("SALES_CHANNEL_ID")
        team_name = "Sales"
    elif action_id == "handoff_engineering":
        target_channel = os.environ.get("ENGINEERING_CHANNEL_ID")
        team_name = "Engineering"
    
    # Get the original message from the central_case channel
    original_msg_result = client.conversations_history(
        channel=os.environ.get("CENTRAL_CASE_CHANNEL_ID"),
        inclusive=True,
        latest=timestamp,
        limit=1
    )
    
    if original_msg_result["ok"] and original_msg_result["messages"]:
        original_message = original_msg_result["messages"][0]["text"]
        original_user = original_msg_result["messages"][0].get("user", "Unknown")
        
        # Share to target channel as a new message but include context
        client.chat_postMessage(
            channel=target_channel,
            text=f"*Case handed off by <@{user_id}> to {team_name} team*\n\nOriginal message from <@{original_user}>:\n{original_message}"
        )
        
        # Update the reply in the thread to show it was handed off
        client.chat_update(
            channel=os.environ.get("CENTRAL_CASE_CHANNEL_ID"),
            ts=body["message"]["ts"],
            text=f"Case has been handed off to {team_name} team by <@{user_id}>",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"✅ Case has been handed off to *{team_name}* team by <@{user_id}>"
                    }
                }
            ]
        )
        
        # Also add a confirmation to the original thread
        client.chat_postMessage(
            channel=os.environ.get("CENTRAL_CASE_CHANNEL_ID"),
            thread_ts=timestamp,
            text=f"This case has been handed off to the *{team_name}* team by <@{user_id}>."
        )

# Error handler
@app.error
def handle_errors(error):
    print(f"Error: {error}")

if __name__ == "__main__":
    handler = SocketModeHandler(app_token=os.environ.get("SLACK_APP_TOKEN"), app=app)
    handler.start() 