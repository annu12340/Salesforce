import logging
from slack_bolt.app.async_app import AsyncApp
import config

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, app: AsyncApp, case_processor, lead_processor):
        self.app = app
        self.case_processor = case_processor
        self.lead_processor = lead_processor
        self.register_handlers()

    def register_handlers(self):
        @self.app.event("message")
        async def handle_message(event, say, client):
            print("entered handle message")
            # Skip bot messages and message subtypes
            if event.get("subtype") == "bot_message" or event.get("subtype") is not None:
                return

            channel_id = event.get("channel")
            text = event.get("text", "")
            user_id = event.get("user")
            timestamp = event.get("ts")
            thread_ts = event.get("thread_ts", timestamp)  # Use parent thread ts if it exists
            
            logger.info(f"Received message in channel {channel_id} from user {user_id}")
            
            # Handle messages in central_case channel
            if channel_id == config.CENTRAL_CASE_CHANNEL_ID:
                logger.info(f"Processing message in central_case channel: {text[:20]}...")
                await self.case_processor.handle_case(text, user_id, timestamp, thread_ts, say, client)
                
            # Handle messages in new_leads channel    
            elif channel_id == config.NEW_LEADS_CHANNEL_ID:
                logger.info(f"Processing message in new_leads channel: {text[:20]}...")
                await self.lead_processor.handle_lead(user_id, timestamp, thread_ts, say)

        @self.app.event("app_mention")
        async def handle_mentions(event, say):
            logger.info(f"App mentioned by {event.get('user')}")
            await say(f"Thanks for mentioning me! How can I assist you?") 