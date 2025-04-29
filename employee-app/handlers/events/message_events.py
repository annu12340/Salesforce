import logging
import config
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class MessageEvents(BaseHandler):
    def register_handlers(self):
        @self.app.event("app_mention")
        async def app_mentioned(event, say, client):
            print("app mentioned")
            
        @self.app.event("channel_created")
        async def handle_channel_created_events(body, logger):
            print("channel created")
        
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
            
            # Handle messages that start with "agentforce"
            print("text",text)
            if text.startswith("<@U08N6BDLBKR>"):
                logger.info("Message starts with 'agentforce', forwarding to AgentForce API")
                return
            print("channel_id",channel_id)
            # Handle messages in central_case channel
            if channel_id == config.CENTRAL_CASE_CHANNEL_ID:
                logger.info(f"Processing message in central_case channel: {text[:20]}...")
                await self.case_processor.handle_case(text, user_id, timestamp, thread_ts, say, client)
                return
            
            elif channel_id in [config.SUPPORT_CHANNEL_ID, config.SALES_CHANNEL_ID, config.ENGINEERING_CHANNEL_ID, config.IAM_CHANNEL_ID]:
                logger.info(f"Processing message in team channel: {text[:20]}...")
                # Add runbook button for team channels
                await say(
                    text="Would you like to fetch  a runbook for this case?",
                    thread_ts=thread_ts,
                    blocks=[
                        {
                            "type": "actions",
                            "block_id": f"runbook_buttons_{timestamp}",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {"type": "plain_text", "text": "Fetch runbook"},
                                    "value": f"runbook_{timestamp}",
                                    "action_id": "fetch_runbook"
                                }
                            ]
                        }
                    ]
                ) 