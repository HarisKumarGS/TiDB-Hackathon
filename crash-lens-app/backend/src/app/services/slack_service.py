import os
from datetime import datetime
from typing import Dict, Any, Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackService:
    """Service for Slack notifications"""

    def __init__(self):
        self.slack_token = os.environ.get("SLACK_BOT_TOKEN")
        self.channel_id = os.environ.get("SLACK_CHANNEL_ID", "C09DTJ9K5PW")
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Slack client with token"""
        if self.slack_token:
            try:
                self.client = WebClient(token=self.slack_token)
            except Exception as e:
                print(f"Warning: Failed to initialize Slack client: {e}")
                self.client = None
        else:
            print("Warning: SLACK_BOT_TOKEN not found in environment variables")
            self.client = None

    def send_crash_notification(
        self,
        error_details: Dict[str, Any],
        s3_url: str,
        s3_key: str,
        users_impacted: int,
        sample_link: str,
        crash_id: str,
    ) -> bool:
        """
        Send error notification to Slack

        Args:
            error_details: Dictionary containing error information
            s3_url: URL to the log file in S3
            s3_key: S3 key for the log file
            users_impacted: Number of users impacted
            sample_link: Link to sample error details
            crash_id: Unique crash identifier

        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        if not self.client:
            print("❌ Slack client not available")
            return False

        try:
            # Create the message payload
            message = {
                "channel": self.channel_id,
                "text": f"🚨 *{error_details['title']}*",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚨 {error_details['title']}",
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Severity:*\n{error_details['severity']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Component:*\n{error_details['component']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Error Type:*\n{error_details['error_type']}",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Users Impacted:*\n{users_impacted:,}",
                            },
                        ],
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Description:*\n{error_details['description']}",
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Log File:*\n<{s3_url}|{s3_key.split('/')[-1]}>",
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Sample Link:*\n<{sample_link}|View Error Details>",
                            },
                            {"type": "mrkdwn", "text": f"*Crash ID:*\n`{crash_id}`"},
                            {"type": "mrkdwn", "text": f"*Status:*\n`Simulated`"},
                        ],
                    },
                    {"type": "divider"},
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | 🔧 Auto-generated from CrashLens Bot",
                            }
                        ],
                    },
                ],
            }

            # Send the message
            response = self.client.chat_postMessage(**message)

            if response["ok"]:
                print(f"✅ Slack notification sent successfully: {response['ts']}")
                return True
            else:
                print(f"❌ Failed to send Slack notification: {response['error']}")
                return False

        except SlackApiError as e:
            print(f"❌ Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            print(f"❌ Error sending Slack notification: {str(e)}")
            return False

    def send_simple_notification(self, message: str) -> bool:
        """
        Send a simple text message to Slack

        Args:
            message: The message to send

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.client:
            return False

        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id, text=message
            )
            return response["ok"]
        except Exception as e:
            print(f"❌ Error sending simple Slack notification: {str(e)}")
            return False

    def is_available(self) -> bool:
        """Check if Slack service is available and configured"""
        return self.client is not None and bool(self.slack_token)

    def get_channel_info(self) -> dict:
        """Get information about the configured Slack channel"""
        if not self.client:
            return {"available": False, "error": "Slack client not initialized"}

        try:
            response = self.client.conversations_info(channel=self.channel_id)
            return {
                "available": True,
                "channel_id": self.channel_id,
                "channel_name": response["channel"]["name"],
                "status": "accessible",
            }
        except SlackApiError as e:
            return {"available": False, "channel_id": self.channel_id, "error": str(e)}
