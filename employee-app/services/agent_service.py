import logging
import os
import json
import aiohttp
import uuid
import config

logger = logging.getLogger(__name__)

class AgentForceService:
    """Service to interact with the AgentForce API"""
    
    def __init__(self):
        self.domain_url = os.environ.get("SALESFORCE_DOMAIN_URL")
        self.consumer_key = os.environ.get("SALESFORCE_CONSUMER_KEY")
        self.consumer_secret = os.environ.get("SALESFORCE_CONSUMER_SECRET")
        self.access_token = None
        self.sequence_id = 0
        
        # Validate required environment variables
        if not self.domain_url or not self.consumer_key or not self.consumer_secret:
            logger.warning("Missing AgentForce API credentials. Integration will not work.")
        else:
            logger.info(f"AgentForce service initialized with domain: {self.domain_url}")
    
    async def get_access_token(self):
        """Get access token from Salesforce OAuth"""
        logger.info("Getting access token from Salesforce")
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'grant_type': 'client_credentials',
                    'client_id': self.consumer_key,
                    'client_secret': self.consumer_secret
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                async with session.post(
                    f"https://{self.domain_url}/services/oauth2/token",
                    data=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data.get('access_token')
                        logger.info("Successfully retrieved access token")
                        return self.access_token
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to get access token: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.exception(f"Error getting access token: {e}")
            return None
    
    async def create_session(self, agent_id):
        """Create a new session with the specified agent"""
        logger.info(f"Creating session for agent: {agent_id}")
        
        if not self.access_token:
            await self.get_access_token()
            if not self.access_token:
                return None
        
        session_key = str(uuid.uuid4())
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "externalSessionKey": session_key,
                    "instanceConfig": {
                        "endpoint": f"https://{self.domain_url}"
                    },
                    "streamingCapabilities": {
                        "chunkTypes": ["Text"]
                    },
                    "bypassUser": True
                }
                
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.access_token}'
                }
                
                async with session.post(
                    f"https://api.salesforce.com/einstein/ai-agent/v1/agents/{agent_id}/sessions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200 or response.status == 201:
                        data = await response.json()
                        logger.info(f"Successfully created session {data.get('sessionId')}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create session: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.exception(f"Error creating session: {e}")
            return None
    
    async def send_message(self, session_id, message_text):
        """Send a message to an existing session"""
        logger.info(f"Sending message to session: {session_id}")
        
        if not self.access_token:
            await self.get_access_token()
            if not self.access_token:
                return None
        
        self.sequence_id += 1
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "message": {
                        "sequenceId": self.sequence_id,
                        "type": "Text",
                        "text": message_text
                    }
                }
                
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.access_token}'
                }
                
                async with session.post(
                    f"https://api.salesforce.com/einstein/ai-agent/v1/sessions/{session_id}/messages",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200 or response.status == 201:
                        data = await response.json()
                        logger.info(f"Successfully sent message to session {session_id}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send message: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.exception(f"Error sending message: {e}")
            return None
    
    async def process_message(self, text, agent_id=None):
        """Process a message through AgentForce and return the response"""
        if not agent_id:
            # Default agent ID if not specified
            agent_id = os.environ.get("SALESFORCE_AGENT_ID")
            if not agent_id:
                logger.error("No agent ID provided and no default agent ID configured")
                return "Error: AgentForce agent ID not configured"
        
        # Step 1: Create a session
        session_data = await self.create_session(agent_id)
        if not session_data:
            logger.error("Failed to create session with AgentForce")
            return "Failed to connect to AgentForce. Please try again later."
        
        session_id = session_data.get('sessionId')
        
        # Step 2: Send the message
        response_data = await self.send_message(session_id, text)
        if not response_data:
            logger.error("Failed to send message to AgentForce")
            return "Failed to communicate with AgentForce. Please try again later."
        
        logger.info(f"AgentForce response: {response_data}")
        
        # Extract the AI response
        # Check if response_data is a list or has a 'messages' field
        if isinstance(response_data, list):
            messages = response_data
        else:
            messages = response_data.get('messages', [])
            
        if not messages:
            return "No response received from AgentForce."
        
        # Compile all message content
        final_message = ""
        for message in messages:
            if 'message' in message:
                final_message += message.get('message', "")
            elif 'text' in message:
                final_message += message.get('text', "")
        
        if not final_message:
            return "No response content found in the conversation."
            
        return final_message