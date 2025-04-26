import logging
import re
import config

logger = logging.getLogger(__name__)

class ChannelService:
    def __init__(self):
        # Map of team names to their channel IDs (will be populated as needed)
        self.team_channels = {
            "Support": config.SUPPORT_CHANNEL_ID,
            "Sales": config.SALES_CHANNEL_ID,
            "Engineering": config.ENGINEERING_CHANNEL_ID
        }
    
    def normalize_team_name(self, team_name):
        """Normalize team name to be used as a channel name"""
        # Convert to lowercase, remove special chars, replace spaces with dashes
        normalized = re.sub(r'[^a-zA-Z0-9\s]', '', team_name.lower())
        normalized = normalized.replace(' ', '-')
        return normalized
    
    def get_team_channel_id(self, team_name):
        """Get channel ID for a team, returns None if not found"""
        # Check exact match
        if team_name in self.team_channels:
            return self.team_channels[team_name]
        
        # Try some common variations
        team_variations = [
            team_name,
            team_name.lower(),
            team_name.upper(),
            team_name.title()
        ]
        
        for variation in team_variations:
            if variation in self.team_channels:
                return self.team_channels[variation]
        
        return None
    
    async def ensure_team_channel_exists(self, client, team_name):
        """
        Ensure a channel exists for the given team.
        If not, create it and update the mapping.
        
        Returns the channel ID.
        """
        channel_id = self.get_team_channel_id(team_name)
        if channel_id:
            logger.info(f"Found existing channel for team {team_name}: {channel_id}")
            return channel_id
        
        # Create a new channel for this team
        channel_name = self.normalize_team_name(team_name)
        try:
            logger.info(f"Creating new channel for team {team_name} with name: {channel_name}")
            result = await client.conversations_create(
                name=channel_name,
                is_private=False
            )
            
            if result["ok"]:
                new_channel_id = result["channel"]["id"]
                # Save the channel ID for future reference
                self.team_channels[team_name] = new_channel_id
                logger.info(f"Created new channel for team {team_name}: {new_channel_id}")
                return new_channel_id
            else:
                logger.error(f"Failed to create channel for team {team_name}: {result.get('error')}")
                return None
        except Exception as e:
            logger.exception(f"Error creating channel for team {team_name}: {e}")
            return None 