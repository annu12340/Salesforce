# Employee App for Slack

This Slack app monitors specific channels and provides interactive functionality for handling cases and leads.

## Features

- Monitors `central_case` and `new_leads` channels
- Responds to messages in `central_case` with interactive buttons for team hand-off
- Allows cases to be directed to different teams (Support, Sales, Engineering)
- Processes new leads messages
- Integrates with Salesforce AgentForce API for AI-powered case handling

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

# Logging
LOG_LEVEL=INFO
DEBUG=false

# AgentForce API Settings (required for AgentForce integration)
SALESFORCE_DOMAIN_URL=your-domain.my.salesforce.com
SALESFORCE_CONSUMER_KEY=your-consumer-key
SALESFORCE_CONSUMER_SECRET=your-consumer-secret
SALESFORCE_DEFAULT_AGENT_ID=your-default-agent-id
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

## Usage

### Message Format Conventions

The app responds differently based on the message format:

1. **AgentForce Queries**: Messages starting with "agentforce" will be processed by the AgentForce AI.
   ```
   agentforce What's the status of case #12345?
   ```

2. **New Cases**: Only messages starting with "New cases" will be processed as structured cases.
   ```
   New cases
   Case number: 12345
   Summary: Customer is having trouble logging in
   Team: Support
   Confidence: 80%
   ```

3. **Other Messages**: All other messages will be treated as generic cases with standard team options.

### Standard Case Format

To create a structured case, format your message like this:

```
New cases
Case number: 12345
Summary: Customer is having trouble logging in
Team: Support
Confidence: 80%
```

If confidence is ≥ 90%, the case will be automatically routed to the specified team.
If confidence is < 90%, the app will display handoff buttons with the suggested team highlighted.

### Using AgentForce

To process a case with AgentForce, you can either:

1. Start your message with `agentforce` followed by your query:
   ```
   agentforce What's the status of case #12345?
   ```

2. Include `Bot: agentforce` in your structured case message:
   ```
   New cases
   Case number: 12345
   Summary: Customer is having trouble logging in
   Team: Support
   Confidence: 80%
   Bot: agentforce
   ```

3. Click the "Process with AgentForce" button on any case

AgentForce will provide an AI-powered response that is shared in the thread and with the assigned team.

## Troubleshooting

If the bot is not responding to messages, check:

1. The bot has been invited to the channels it needs to monitor
2. The channel IDs in the environment variables are correct
3. The bot has the necessary permissions (scopes)
4. Socket Mode is enabled and the app is running
5. For AgentForce functionality, ensure the Salesforce API credentials are correctly configured

## Dependencies

See `requirements.txt` for all dependencies. 