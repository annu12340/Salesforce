import logging
import re
from slack_bolt.app.async_app import AsyncApp
import config

logger = logging.getLogger(__name__)

class ActionHandlers:
    def __init__(self, app: AsyncApp, handoff_processor):
        self.app = app
        self.handoff_processor = handoff_processor
        self.register_handlers()

    def register_handlers(self):
        # Register standard team handoff actions
        @self.app.action("handoff_support")
        @self.app.action("handoff_sales")
        @self.app.action("handoff_engineering")
        async def handle_standard_handoff_action(ack, body, client):
            await ack()
            logger.info(f"Received standard button click: {body['actions'][0]['action_id']}")
            
            # Extract information
            user_id = body["user"]["id"]
            action_id = body["actions"][0]["action_id"]
            value = body["actions"][0]["value"]
            
            # Get original message timestamp
            timestamp = value.split("_")[1]
            
            # Process the hand-off
            await self.handoff_processor.process_handoff(action_id, user_id, timestamp, body, client)
        
        # Register dynamic team handoff action pattern
        @self.app.action(re.compile("handoff_.*"))
        async def handle_dynamic_handoff_action(ack, body, client):
            await ack()
            action_id = body["actions"][0]["action_id"]
            
            # Skip the standard teams which are handled by the specific handlers
            if action_id in ["handoff_support", "handoff_sales", "handoff_engineering"]:
                return
                
            logger.info(f"Received dynamic team button click: {action_id}")
            
            # Extract information
            user_id = body["user"]["id"]
            value = body["actions"][0]["value"]
            
            # Get original message timestamp
            timestamp = value.split("_")[1]
            
            # Process the hand-off
            await self.handoff_processor.process_handoff(action_id, user_id, timestamp, body, client)

        @self.app.error
        async def handle_errors(error):
            logger.error(f"Error: {error}") 