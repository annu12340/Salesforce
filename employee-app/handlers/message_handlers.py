import logging
from slack_bolt.app.async_app import AsyncApp
from .events.message_events import MessageEvents
from .actions.runbook_actions import RunbookActions

logger = logging.getLogger(__name__)

class MessageHandlers:
    def __init__(self, app: AsyncApp, case_processor, agent_service):
        self.app = app
        self.case_processor = case_processor
        self.agent_service = agent_service
        
        # Initialize all handler classes
        self.message_events = MessageEvents(app, case_processor, agent_service)
        self.runbook_actions = RunbookActions(app, case_processor, agent_service)
        
        self.register_handlers()

    def register_handlers(self):
        # Register all handlers
        self.message_events.register_handlers()
        self.runbook_actions.register_handlers()
