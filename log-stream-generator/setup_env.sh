#!/bin/bash

# Environment setup script for CrashLens Bot
echo "Setting up environment for CrashLens Bot..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Slack Bot Configuration
# Get your Bot User OAuth Token from Slack (starts with xoxb-...)
SLACK_BOT_TOKEN=your-slack-bot-token-here

# Slack Channel ID (e.g., C1234567890)
SLACK_CHANNEL_ID=your-channel-id-here

# AWS Configuration for S3
# AWS Access Key ID
AWS_ACCESS_KEY_ID=your-aws-access-key-id-here

# AWS Secret Access Key
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key-here

# AWS Region (e.g., us-east-1, us-west-2)
AWS_DEFAULT_REGION=us-east-1

# S3 Bucket Name (optional, defaults to tidb-hackathon-bucket)
S3_BUCKET_NAME=tidb-hackathon-bucket

# DynamoDB Table Name (optional, defaults to tidb-hackathon-crash)
DYNAMODB_TABLE_NAME=tidb-hackathon-crash
EOF
    echo "✅ .env file created. Please update it with your actual Slack credentials."
else
    echo "✅ .env file already exists."
fi

# Load environment variables
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded."
else
    echo "❌ .env file not found. Please create it first."
    exit 1
fi

# Check if required environment variables are set
if [ -z "$SLACK_BOT_TOKEN" ] || [ "$SLACK_BOT_TOKEN" = "your-slack-bot-token-here" ]; then
    echo "❌ SLACK_BOT_TOKEN not set. Please update .env file with your actual token."
    exit 1
fi

if [ -z "$SLACK_CHANNEL_ID" ] || [ "$SLACK_CHANNEL_ID" = "your-channel-id-here" ]; then
    echo "❌ SLACK_CHANNEL_ID not set. Please update .env file with your actual channel ID."
    exit 1
fi

# Check AWS credentials (optional for S3 upload)
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ "$AWS_ACCESS_KEY_ID" = "your-aws-access-key-id-here" ]; then
    echo "⚠️  AWS_ACCESS_KEY_ID not set. S3 upload will fallback to local file generation."
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ "$AWS_SECRET_ACCESS_KEY" = "your-aws-secret-access-key-here" ]; then
    echo "⚠️  AWS_SECRET_ACCESS_KEY not set. S3 upload will fallback to local file generation."
fi

if [ -z "$AWS_DEFAULT_REGION" ] || [ "$AWS_DEFAULT_REGION" = "us-east-1" ]; then
    echo "ℹ️  Using default AWS region: us-east-1"
fi

# Check DynamoDB table name (optional)
if [ -z "$DYNAMODB_TABLE_NAME" ] || [ "$DYNAMODB_TABLE_NAME" = "tidb-hackathon-crash" ]; then
    echo "ℹ️  Using default DynamoDB table: tidb-hackathon-crash"
fi

echo "✅ Environment setup complete!"
echo "You can now run: python simulate_logs.py <scenario>"
