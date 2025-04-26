import logging
from slack_bolt.app.async_app import AsyncApp
import config
from services.agent_service import AgentForceService
logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, app: AsyncApp, case_processor, lead_processor, agent_service):
        self.app = app
        self.case_processor = case_processor
        self.lead_processor = lead_processor
        self.agent_service = agent_service
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
            
            # Handle messages that start with "agentforce"
            print("text",text)
            if text.startswith("<@U08N6BDLBKR>"):
                logger.info("Message starts with 'agentforce', forwarding to AgentForce API")
                response = await self.agent_service.process_message(text)
                logger.info(f"AgentForce response: {response}")
                await say(text=response, thread_ts=thread_ts)
                return

            # Handle messages in central_case channel
            if channel_id == config.CENTRAL_CASE_CHANNEL_ID:
                logger.info(f"Processing message in central_case channel: {text[:20]}...")
                await self.case_processor.handle_case(text, user_id, timestamp, thread_ts, say, client)
                return
                
            # Handle messages in new_leads channel    
            elif channel_id == config.NEW_LEADS_CHANNEL_ID:
                logger.info(f"Processing message in new_leads channel: {text[:20]}...")
                await self.lead_processor.handle_lead(user_id, timestamp, thread_ts, say)
                return

            
        # Add support command handler
        @self.app.command("/support")
        async def handle_support_command(ack, body, say):
            await ack()
            user_id = body["user_id"]
            logger.info(f"Received /support command from {user_id}")
            await say(f"<@{user_id}> How can I help you today?")
            
        # Add agentforce command handler
        @self.app.command("/agentforce")
        async def handle_agentforce_command(ack, body, say, client):
            await ack()
            user_id = body["user_id"]
            query = body["text"]
            logger.info(f"Received /agentforce command from {user_id} with query: {query}")
            
            # Create a case data object for AgentForce
            case_data = {
                'case_number': f'CMD-{body["trigger_id"][-8:]}',
                'summary': query,
                'team': 'Support',  # Default team
                'confidence': 75,   # Default confidence
                'bot': 'agentforce'
            }
            
            # Use the case processor to handle this as an AgentForce case
            await self.case_processor.process_agentforce_case(
                case_data, 
                f"agentforce {query}", 
                user_id, 
                None,  # No thread_ts since this is a new message
                say, 
                client
            ) 