import logging

logger = logging.getLogger(__name__)

class LeadService:
    def __init__(self):
        pass
        
    async def handle_lead(self, user_id, timestamp, thread_ts, say):
        """Handle messages in the new_leads channel"""
        try:
            logger.info(f"Processing new lead from user {user_id}")
            await say(f"New lead received from <@{user_id}>! Processing...", thread_ts=thread_ts)
            logger.info("New lead response sent successfully")
        except Exception as e:
            logger.exception(f"Error processing new lead: {e}") 