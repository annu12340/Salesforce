import logging
import config
from .channel_service import ChannelService

logger = logging.getLogger(__name__)

class HandoffService:
    def __init__(self):
        self.channel_service = ChannelService()
        
    async def process_handoff(self, action_id, user_id, timestamp, body, client):
        """Process the hand-off action from button click"""
        try:
            # Determine target channel based on action
            target_channel = ""
            team_name = ""
            
            # Check if this is a standard team or dynamic team
            if action_id.startswith("handoff_"):
                team_id = action_id.replace("handoff_", "")
                
                # Handle standard teams
                if team_id == "support":
                    target_channel = config.SUPPORT_CHANNEL_ID
                    team_name = "Support"
                elif team_id == "sales":
                    target_channel = config.SALES_CHANNEL_ID
                    team_name = "Sales"
                elif team_id == "engineering":
                    target_channel = config.ENGINEERING_CHANNEL_ID
                    team_name = "Engineering"
                else:
                    # This is a dynamic team, try to extract the team name from the button text
                    button_text = body["actions"][0].get("text", {}).get("text", "")
                    if button_text.startswith("Hand-off to "):
                        team_name = button_text.replace("Hand-off to ", "")
                        
                        # Ensure channel exists for this team
                        target_channel = await self.channel_service.ensure_team_channel_exists(client, team_name)
                        
                        if not target_channel:
                            # Failed to get/create channel
                            await client.chat_postMessage(
                                channel=config.CENTRAL_CASE_CHANNEL_ID,
                                thread_ts=timestamp,
                                text=f"⚠️ Failed to hand off to team '{team_name}'. The channel could not be created or found."
                            )
                            return
            
            if not target_channel or not team_name:
                logger.error(f"No target channel found for action {action_id}")
                await client.chat_postMessage(
                    channel=config.CENTRAL_CASE_CHANNEL_ID,
                    thread_ts=timestamp,
                    text="⚠️ Failed to hand off the case. Could not determine the target team."
                )
                return
            
            logger.info(f"Handling hand-off to {team_name} channel {target_channel}")
            
            # Update the status with loading indicator
            initial_update = await client.chat_update(
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
                original_user = original_msg_result["messages"][0].get("user", "Unknown")
                
                logger.info(f"Found original message: {original_message[:20]}...")
                
                # Share to target channel as a new message but include context
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
                
                # Also add a confirmation to the original thread
                await client.chat_postMessage(
                    channel=config.CENTRAL_CASE_CHANNEL_ID,
                    thread_ts=timestamp,
                    text=f"This case has been handed off to the *{team_name}* team by <@{user_id}>."
                )
                
                logger.info("Hand-off completed successfully")
        except Exception as e:
            logger.exception(f"Error during hand-off process: {e}") 