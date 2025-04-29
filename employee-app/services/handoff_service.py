import logging
import config
from .team_service import TeamService

logger = logging.getLogger(__name__)

class HandoffService:
    def __init__(self):
        self.team_service = TeamService()

    async def process_handoff(self, action_id, user_id, timestamp, body, client):
        """Process the hand-off action from button click"""
        try:
            # Determine target channel based on action
            team_name = ""
            
            # Check if this is a standard team or dynamic team
            if action_id.startswith("handoff_"):
                team_id = action_id.replace("handoff_", "")
                
                # Handle standard teams
                if team_id == "support":
                    team_name = "Support"
                elif team_id == "sales":
                    team_name = "Sales"
                elif team_id == "engineering":
                    team_name = "Engineering"
                else:
                    # This is a dynamic team, try to extract the team name from the button text
                    button_text = body["actions"][0].get("text", {}).get("text", "")
                    if button_text.startswith("Hand-off to "):
                        team_name = button_text.replace("Hand-off to ", "")
  
            if not team_name:
                logger.error(f"No team name found for action {action_id}")
                await client.chat_postMessage(
                    channel=config.CENTRAL_CASE_CHANNEL_ID,
                    thread_ts=timestamp,
                    text="⚠️ Failed to hand off the case. Could not determine the target team."
                )
                return
            
            logger.info(f"Handling hand-off to {team_name}")
            
            # Use TeamService to handle the handoff
            await self.team_service.update_handoff_status(team_name, user_id, timestamp, body, client)
            
        except Exception as e:
            logger.exception(f"Error during hand-off process: {e}") 