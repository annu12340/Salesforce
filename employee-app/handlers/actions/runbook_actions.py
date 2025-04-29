import logging
import asyncio
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class RunbookActions(BaseHandler):
    def register_handlers(self):
        @self.app.action("fetch_runbook")
        async def handle_runbook_execution(ack, body, client):
            await ack()
            logger.info("Received runbook fetch request")
            
            # Extract information
            user_id = body["user"]["id"]
            value = body["actions"][0]["value"]
            timestamp = value.split("_")[1]
            
            try:
                # First, get the original message
                original_msg_result = await client.conversations_history(
                    channel=body["channel"]["id"],
                    inclusive=True,
                    latest=timestamp,
                    limit=1
                )
                
                if original_msg_result["ok"] and original_msg_result["messages"]:
                    original_message = original_msg_result["messages"][0]["text"]
                    
                    # Initial loading state
                    loading_states = [
                        ":hourglass_flowing_sand: Analyzing case details...",
                        ":mag: Searching for relevant runbooks...",
                        ":file_folder: Fetching runbook steps...",
                        ":sparkles: Preparing steps for display..."
                    ]
                    
                    # Create initial loading message
                    loading_message = await client.chat_postMessage(
                        channel=body["channel"]["id"],
                        thread_ts=timestamp,
                        text="Fetching runbook steps...",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": loading_states[0]
                                }
                            }
                        ]
                    )
                    
                    # Animate loading states
                    for i, state in enumerate(loading_states[1:], 1):
                        await asyncio.sleep(1)  # Simulate processing time
                        await client.chat_update(
                            channel=body["channel"]["id"],
                            ts=loading_message["ts"],
                            text=f"Fetching runbook steps... ({i+1}/{len(loading_states)})",
                            blocks=[
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": state
                                    }
                                }
                            ]
                        )
                    
                    # Mock runbook steps
                    runbook_steps = [
                        "1. Check system logs for errors",
                        "2. Verify database connection",
                        "3. Restart application service",
                        "4. Clear cache",
                        "5. Run system diagnostics"
                    ]
                    
                    # Create the runbook steps message with better formatting
                    steps_text = "\n".join([
                        f"• {step}" for step in runbook_steps
                    ])
                    
                    # Final message with steps
                    await client.chat_update(
                        channel=body["channel"]["id"],
                        ts=loading_message["ts"],
                        text=".",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": f"*:white_check_mark: Runbook Steps Found*\n\n{steps_text}"
                                }
                            },
                            {
                                "type": "context",
                                "elements": [
                                    {
                                        "type": "mrkdwn",
                                        "text": ":information_source: Found 5 steps in the runbook"
                                    }
                                ]
                            }
                        ]
                    )
    
            except Exception as e:
                logger.exception(f"Error fetching runbook steps: {e}")
                # Update UI to show error with better formatting
                await client.chat_update(
                    channel=body["channel"]["id"],
                    ts=body["message"]["ts"],
                    text="Error fetching runbook steps",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f":x: *Error Fetching Runbook Steps*\n\n{str(e)}"
                            }
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": ":warning: Please try again or contact support if the issue persists"
                                }
                            ]
                        }
                    ]
                ) 