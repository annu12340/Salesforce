import logging
from slack_bolt.app.async_app import AsyncApp

logger = logging.getLogger(__name__)

class BaseHandler:
    def __init__(self, app: AsyncApp, case_processor, agent_service):
        self.app = app
        self.case_processor = case_processor
        self.agent_service = agent_service 