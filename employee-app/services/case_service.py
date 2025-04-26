import logging
import config
from .case_parser import CaseParser
from .channel_service import ChannelService
from .agent_service import AgentForceService

logger = logging.getLogger(__name__)

class CaseService:
    def __init__(self):
        self.case_parser = CaseParser()
        self.channel_service = ChannelService()
        self.agent_service = AgentForceService()
        
    async def handle_case(self, text, user_id, timestamp, thread_ts, say, client=None):
        """Handle messages in the central_case channel"""
        try:
            # Check message prefixes first
            text_lower = text.lower().strip()
            
            # Handle messages that start with "agentforce"
            if text_lower.startswith("agentforce"):
                logger.info("Message starts with 'agentforce', forwarding to AgentForce API")
                # Create a simple case data object for AgentForce
                case_data = {
                    'case_number': f'AF-{timestamp.replace(".", "")}',
                    'summary': text[10:].strip(),  # Remove "agentforce" prefix
                    'team': 'Support',  # Default team
                    'confidence': 75,   # Default confidence
                    'bot': 'agentforce'
                }
                return await self.process_agentforce_case(case_data, text, user_id, thread_ts, say, client)
            
            # Only process case messages that start with "New cases"
            if not text_lower.startswith("new cases"):
                logger.info("Message doesn't start with 'New cases', skipping case processing")
                return await self.handle_generic_case(text, user_id, timestamp, thread_ts, say)
                
            # Message starts with "New cases", proceed with regular case handling
            logger.info("Processing message starting with 'New cases'")
            
            # Parse the case text
            case_data = self.case_parser.parse_case_text(text)
            
            if not case_data:
                # If parsing failed, use the original handler
                logger.info("Text does not match case format, using default response")
                return await self.handle_generic_case(text, user_id, timestamp, thread_ts, say)
               
            # Check if this is a request for AgentForce via bot field
            if case_data.get('bot', '').lower() == 'agentforce':
                logger.info("AgentForce bot specified in case data, forwarding to AgentForce API")
                return await self.process_agentforce_case(case_data, text, user_id, thread_ts, say, client)
            
            # Check confidence threshold
            if case_data['confidence'] >= 90:
                # High confidence, auto-route to team
                logger.info(f"High confidence case ({case_data['confidence']}%), auto-routing to {case_data['team']}")
                await self.auto_route_to_team(case_data, user_id, text, thread_ts, say, client)
            else:
                # Lower confidence, show handoff buttons
                logger.info(f"Lower confidence case ({case_data['confidence']}%), showing handoff buttons")
                await self.show_handoff_options(case_data, text, user_id, timestamp, thread_ts, say)
                
            return True
            
        except Exception as e:
            logger.exception(f"Error handling case: {e}")
            # Fallback to generic handler on error
            return await self.handle_generic_case(text, user_id, timestamp, thread_ts, say)
    

    async def auto_route_to_team(self, case_data, user_id, original_text, thread_ts, say, client):
        """Automatically route a high-confidence case to the appropriate team"""
        if not client:
            logger.error("Client is required for auto-routing but was not provided")
            await say(text=f"Error: Unable to auto-route case. Client not available.", thread_ts=thread_ts)
            return False
        
        team_name = case_data['team']
        # Ensure the team channel exists
        team_channel_id = await self.channel_service.ensure_team_channel_exists(client, team_name)
        
        if not team_channel_id:
            # Channel creation failed, notify in thread
            await say(
                text=f"⚠️ Unable to auto-route to team '{team_name}'. Please use manual handoff.",
                thread_ts=thread_ts
            )
            # Fall back to showing handoff options
            await self.show_handoff_options(case_data, original_text, user_id, thread_ts, thread_ts, say)
            return False
        
        # Forward the case to the team channel
        await client.chat_postMessage(
            channel=team_channel_id,
            text=f"*Auto-routed Case #{case_data['case_number']} from <@{user_id}>*\n\n"
                 f"*Team:* {team_name}\n"
                 f"*Confidence:* {case_data['confidence']}%\n"
                 f"*Summary:* {case_data['summary']}\n\n"
                 f"*Original Message:*\n{original_text}"
        )
        
        # Confirm in the original thread
        await say(
            text=f"✅ This case has been automatically routed to *{team_name}* with {case_data['confidence']}% confidence.",
            thread_ts=thread_ts
        )
        
        return True
        
    async def show_handoff_options(self, case_data, text, user_id, timestamp, thread_ts, say):
        """Show handoff buttons for a case with team recommendation"""
        team_name = case_data['team']
        
        # Create interactive buttons for team hand-off with the suggested team highlighted
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Case #{case_data['case_number']} from <@{user_id}>*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:* {case_data['summary']}\n*Suggested Team:* {team_name} (Confidence: {case_data['confidence']}%)"
                }
            },
            {
                "type": "actions",
                "block_id": f"handoff_buttons_{timestamp}",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text", 
                            "text": f"Hand-off to {team_name}"
                        },
                        "style": "primary",  # Highlight the suggested team
                        "value": f"{self.normalize_team_name(team_name)}_{timestamp}",
                        "action_id": f"handoff_{self.normalize_team_name(team_name)}"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Hand-off to Support"},
                        "value": f"support_{timestamp}",
                        "action_id": "handoff_support"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Hand-off to Sales"},
                        "value": f"sales_{timestamp}",
                        "action_id": "handoff_sales"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Hand-off to Engineering"},
                        "value": f"engineering_{timestamp}",
                        "action_id": "handoff_engineering"
                    }
                ]
            }
        ]
        
        # If this is a case that could use AgentForce, add that option
        bot_name = case_data.get('bot', '')
        if not bot_name:
            # Add an AgentForce button if no bot was specified
            blocks[2]["elements"].append({
                "type": "button",
                "text": {"type": "plain_text", "text": "Process with AgentForce"},
                "value": f"agentforce_{timestamp}",
                "action_id": "process_agentforce"
            })
        
        # Remove duplicate buttons if team already exists in our standard options
        normalized_team = self.normalize_team_name(team_name).lower()
        standard_teams = ["support", "sales", "engineering"]
        
        if normalized_team in standard_teams:
            # Remove the standard button that matches the suggested team
            blocks[2]["elements"] = [
                button for button in blocks[2]["elements"] 
                if not (button.get("action_id") == f"handoff_{normalized_team}" and 
                        button != blocks[2]["elements"][0])  # Keep the primary button
            ]
        
        # Send response as a thread to the original message
        logger.info(f"Sending case blocks with suggested team {team_name} in thread {thread_ts}")
        await say(blocks=blocks, thread_ts=thread_ts)
        logger.info("Case response sent successfully")
    
    def normalize_team_name(self, team_name):
        """Convert team name to a format suitable for action IDs"""
        return team_name.lower().replace(' ', '_')
        
    async def handle_generic_case(self, text, user_id, timestamp, thread_ts, say):
        """Handle generic (non-structured) case messages"""
        try:
            # Create standard interactive buttons for team hand-off
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Case from <@{user_id}>*:\n{text}"
                    }
                },
                {
                    "type": "actions",
                    "block_id": f"handoff_buttons_{timestamp}",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Hand-off to Support"},
                            "value": f"support_{timestamp}",
                            "action_id": "handoff_support"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Hand-off to Sales"},
                            "value": f"sales_{timestamp}",
                            "action_id": "handoff_sales"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Hand-off to Engineering"},
                            "value": f"engineering_{timestamp}",
                            "action_id": "handoff_engineering"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Process with AgentForce"},
                            "value": f"agentforce_{timestamp}",
                            "action_id": "process_agentforce"
                        }
                    ]
                }
            ]
            
            # Send response as a thread to the original message
            logger.info(f"Sending standard case response blocks in thread {thread_ts}")
            await say(blocks=blocks, thread_ts=thread_ts)
            logger.info("Standard case response sent successfully")
            return True
        except Exception as e:
            logger.exception(f"Error sending standard case response: {e}")
            return False 