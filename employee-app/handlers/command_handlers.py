import logging
from slack_bolt.app.async_app import AsyncApp

logger = logging.getLogger(__name__)

class CommandHandlers:
    def __init__(self, app: AsyncApp):
        self.app = app
        self.register_handlers()

    def register_handlers(self):
        @self.app.command("/support")
        async def handle_support_command(ack, body, say):
            await ack()
            user_id = body["user_id"]
            logger.info(f"Received /support command from {user_id}")
            await say(f"<@{user_id}> How can I help you today?") 