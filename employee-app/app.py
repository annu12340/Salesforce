import logging
import asyncio
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import config

# Import services
from services.case_service import CaseService
from services.lead_service import LeadService
from services.handoff_service import HandoffService

# Import handlers
from handlers.message_handlers import MessageHandlers
from handlers.command_handlers import CommandHandlers
from handlers.action_handlers import ActionHandlers

# Configure logging
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL),
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SlackBot:
    def __init__(self):
        # Initialize the Slack app
        self.app = AsyncApp(token=config.SLACK_BOT_TOKEN)
        logger.info(f"Initializing bot with Central Case channel: {config.CENTRAL_CASE_CHANNEL_ID}")
        logger.info(f"New Leads channel: {config.NEW_LEADS_CHANNEL_ID}")
        
        # Initialize services
        self.case_service = CaseService()
        self.lead_service = LeadService()
        self.handoff_service = HandoffService()
        
        # Register handlers
        self.message_handlers = MessageHandlers(self.app, self.case_service, self.lead_service)
        self.command_handlers = CommandHandlers(self.app)
        self.action_handlers = ActionHandlers(self.app, self.handoff_service)

    async def start(self):
        """Start the Slack bot with Socket Mode"""
        try:
            handler = AsyncSocketModeHandler(
                app_token=config.SLACK_APP_TOKEN,
                app=self.app
            )
            logger.info("Starting Socket Mode handler...")
            await handler.start_async()
        except Exception as e:
            logger.exception(f"Failed to start app: {e}")

# Run the app
if __name__ == "__main__":
    bot = SlackBot()
    asyncio.run(bot.start()) 