import logging
import re
from slack_bolt.app.async_app import AsyncApp
import config

logger = logging.getLogger(__name__)

class ActionHandlers:
    def __init__(self, app: AsyncApp, handoff_processor, case_processor):
        self.app = app
        self.handoff_processor = handoff_processor
        self.case_processor = case_processor
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
            
        # Register AgentForce processing action
        @self.app.action("process_agentforce")
        async def handle_agentforce_action(ack, body, client):
            await ack()
            logger.info(f"Received AgentForce processing request")
            
            # Extract information
            user_id = body["user"]["id"]
            value = body["actions"][0]["value"]
            
            # Get original message timestamp
            timestamp = value.split("_")[1]
            
            # Update the message to show processing status
            try:
                # First, get the original message
                original_msg_result = await client.conversations_history(
                    channel=config.CENTRAL_CASE_CHANNEL_ID,
                    inclusive=True,
                    latest=timestamp,
                    limit=1
                )
                
                if original_msg_result["ok"] and original_msg_result["messages"]:
                    original_message = original_msg_result["messages"][0]["text"]
                    original_user = original_msg_result["messages"][0].get("user", "Unknown")
                    
                    # Update the UI to show processing
                    await client.chat_update(
                        channel=config.CENTRAL_CASE_CHANNEL_ID,
                        ts=body["message"]["ts"],
                        text=f"Processing with AgentForce...",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f":hourglass: Processing case with AgentForce..."
                                }
                            }
                        ]
                    )
                    
                    # Create a synthetic case data object for AgentForce
                    # (For cases where the original message wasn't in the structured format)
                    case_data = {
                        'case_number': 'AUTO-' + timestamp.replace('.', ''),
                        'summary': original_message[:100] + ('...' if len(original_message) > 100 else ''),
                        'team': 'Support',  # Default to Support team
                        'confidence': 50,   # Default confidence level
                        'bot': 'agentforce'
                    }
                    
                    # Process through AgentForce
                    await self.case_processor.process_agentforce_case(
                        case_data, 
                        original_message, 
                        user_id, 
                        timestamp, 
                        lambda **kwargs: client.chat_postMessage(
                            channel=config.CENTRAL_CASE_CHANNEL_ID, 
                            **kwargs
                        ),
                        client
                    )
                    
                    # Update the original UI to show completion
                    await client.chat_update(
                        channel=config.CENTRAL_CASE_CHANNEL_ID,
                        ts=body["message"]["ts"],
                        text=f"Case processed with AgentForce",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f":white_check_mark: Case has been processed with AgentForce"
                                }
                            }
                        ]
                    )
            except Exception as e:
                logger.exception(f"Error processing with AgentForce: {e}")
                # Update UI to show error
                await client.chat_update(
                    channel=config.CENTRAL_CASE_CHANNEL_ID,
                    ts=body["message"]["ts"],
                    text=f"Error processing with AgentForce",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f":x: Error processing with AgentForce: {str(e)}"
                            }
                        }
                    ]
                )

        @self.app.error
        async def handle_errors(error):
            logger.error(f"Error: {error}") 