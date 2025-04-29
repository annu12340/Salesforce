import logging
import asyncio
from ..base_handler import BaseHandler

logger = logging.getLogger(__name__)

class RunbookActions(BaseHandler):
    def register_handlers(self):
        @self.app.action("execute_runbook")
        async def handle_runbook_execution(ack, body, client):
            await ack()
            logger.info("Received runbook execution request")
            
            # Extract information
            user_id = body["user"]["id"]
            value = body["actions"][0]["value"]
            timestamp = value.split("_")[1]
            
            # Update the message to show processing status
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
                    
                    # Update the UI to show processing
                    await client.chat_update(
                        channel=body["channel"]["id"],
                        ts=body["message"]["ts"],
                        text="Fetching and executing runbook...",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": ":hourglass: Fetching and executing runbook..."
                                }
                            }
                        ]
                    )
                    
                    # Mock AgentForce response with commands
                    mock_commands = [
                        "1. Check system logs for errors",
                        "2. Verify database connection",
                        "3. Restart application service",
                        "4. Clear cache",
                        "5. Run system diagnostics"
                    ]
                    
                    # Create initial progress message
                    progress_message = await client.chat_postMessage(
                        channel=body["channel"]["id"],
                        thread_ts=timestamp,
                        text="Starting runbook execution...",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": ":hourglass: Starting runbook execution..."
                                }
                            }
                        ]
                    )
                    
                    # Execute each command with a delay
                    completed_steps = []
                    for i, cmd in enumerate(mock_commands):
                        # Update progress message to show current step
                        progress_text = "\n".join([
                            f":white_check_mark: {step}" for step in completed_steps
                        ] + [
                            f"*:load: {cmd}*"
                        ] + [
                            f":white_circle: {step}" for step in mock_commands[i+1:]
                        ])
                        
                        await client.chat_update(
                            channel=body["channel"]["id"],
                            ts=progress_message["ts"],
                            text=f"Executing step {i+1} of {len(mock_commands)}",
                            blocks=[
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": progress_text
                                    }
                                }
                            ]
                        )
                        
                        await asyncio.sleep(1)  # Simulate command execution time
                        completed_steps.append(cmd)
                    
                    # Update the final progress message
                    await client.chat_update(
                        channel=body["channel"]["id"],
                        ts=progress_message["ts"],
                        text="Runbook execution completed",
                        blocks=[
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": "\n".join([
                                        f":white_check_mark: {step}" for step in completed_steps
                                    ] + ["\n\n:tada: All steps completed successfully!"])
                                }
                            }
                        ]
                    )
            except Exception as e:
                logger.exception(f"Error executing runbook: {e}")
                # Update UI to show error
                await client.chat_update(
                    channel=body["channel"]["id"],
                    ts=body["message"]["ts"],
                    text="Error executing runbook",
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f":x: Error executing runbook: {str(e)}"
                            }
                        }
                    ]
                ) 