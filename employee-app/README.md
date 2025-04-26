# Employee App for Slack

This Slack app monitors specific channels and provides interactive functionality for handling cases and leads.

## Features

- Monitors `central_case` and `new_leads` channels
- Responds to messages in `central_case` with interactive buttons for team hand-off
- Allows cases to be directed to different teams (Support, Sales, Engineering)
- Processes new leads messages

## Setup

1. Create a Slack app in the [Slack API Console](https://api.slack.com/apps)
2. Enable Socket Mode in your Slack app settings
3. Install the app to your workspace
4. Set up environment variables (see `.env.example`)
5. Run the app: `python app.py`

## Required Environment Variables

Create a `.env` file with the following variables:

```
# Slack API Tokens
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

# Channel IDs
CENTRAL_CASE_CHANNEL_ID=C0123ABCDEF
NEW_LEADS_CHANNEL_ID=C0123GHIJKL
SUPPORT_CHANNEL_ID=C0123MNOPQR
SALES_CHANNEL_ID=C0123STUVWX
ENGINEERING_CHANNEL_ID=C0123YZ1234
```

## Required Slack App Permissions

### Bot Token Scopes

- `channels:history` - Read messages in channels
- `channels:read` - View basic information about channels
- `chat:write` - Send messages as the app
- `groups:history` - Read messages in private channels
- `groups:read` - View basic information about private channels
- `im:history` - Read direct messages
- `im:read` - View basic information about direct messages
- `reactions:write` - Add reactions to messages
- `chat:write.customize` - Send messages as the app with a custom username and avatar

### Event Subscriptions

- `message.channels` - Subscribe to message events in channels
- `app_mention` - Subscribe to app mention events

## Troubleshooting

If the bot is not responding to messages, check:

1. The bot has been invited to the channels it needs to monitor
2. The channel IDs in the environment variables are correct
3. The bot has the necessary permissions (scopes)
4. Socket Mode is enabled and the app is running

## Dependencies

See `requirements.txt` for all dependencies. 