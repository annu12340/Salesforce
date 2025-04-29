import logging
import config

logger = logging.getLogger(__name__)

class TeamService:
    def __init__(self):
        self.team_channels = {
            "support": config.SUPPORT_CHANNEL_ID,
            "sales": config.SALES_CHANNEL_ID,
            "engineering": config.ENGINEERING_CHANNEL_ID,
            "iam": config.IAM_CHANNEL_ID
        }
        
    def get_team_channel(self, team_name):
        """Get the channel ID for a team name"""
        return self.team_channels.get(team_name.lower())
        
    def normalize_team_name(self, team_name):
        """Convert team name to a format suitable for action IDs"""
        return team_name.lower().replace(' ', '_')
        
    async def route_to_team(self, case_data, user_id, thread_ts, say, client):
        """Route a case to a specific team channel"""
        team = case_data['team']
        target_channel = self.get_team_channel(team)
        
        if not target_channel:
            logger.error(f"No channel found for team {team}")
            await say(
                text=f"⚠️ Failed to route case. Could not find channel for team {team}.",
                thread_ts=thread_ts
            )
            return False
            
        # Forward the case to the team channel
        await client.chat_postMessage(
            channel=target_channel,
            text=f"*Case #{case_data['case_number']} from <@{user_id}>*\n\n"
                 f"*Team:* {team}\n"
                 f"*Confidence:* {case_data['confidence']}%\n"
                 f"*Summary:* {case_data['summary']}\n\n"
        )
        
        # Confirm in the original thread
        await say(
            text=f"✅ This case has been routed to *{team}* with {case_data['confidence']}% confidence.",
            thread_ts=thread_ts
        )
        
        return True
        
    async def update_handoff_status(self, team_name, user_id, timestamp, body, client):
        """Update the UI to show handoff status"""
        # Update the status with loading indicator
        await client.chat_update(
            channel=config.CENTRAL_CASE_CHANNEL_ID,
            ts=body["message"]["ts"],
            text=f":hourglass: Processing hand-off to {team_name} team...",
        )
        
        # Get the original message from the central_case channel
        original_msg_result = await client.conversations_history(
            channel=config.CENTRAL_CASE_CHANNEL_ID,
            inclusive=True,
            latest=timestamp,
            limit=1
        )
        
        if original_msg_result["ok"] and original_msg_result["messages"]:
            original_message = original_msg_result["messages"][0]["text"]
            
            # Share to target channel as a new message but include context
            target_channel = self.get_team_channel(team_name)
            if target_channel:
                await client.chat_postMessage(
                    channel=target_channel,
                    text=f"*Case handed off by <@{user_id}> to {team_name} team*\n\n{original_message}"
                )
            
            # Update the reply in the thread to show it was handed off
            await client.chat_update(
                channel=config.CENTRAL_CASE_CHANNEL_ID,
                ts=body["message"]["ts"],
                text=f"Case has been handed off to {team_name} team by <@{user_id}>",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f":white_check_mark: Case has been handed off to *{team_name}* team by <@{user_id}>"
                        }
                    }
                ]
            )
            
            
        return False 