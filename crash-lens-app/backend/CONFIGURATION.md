# Configuration Guide

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

### Database Configuration
```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@tidb-hackathon-instance.cdgkfoacvf6u.us-east-1.rds.amazonaws.com:5432/crashlens
```

### AWS S3 Configuration (for log file storage)
```bash
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
S3_BUCKET_NAME=tidb-hackathon-bucket
AWS_REGION=us-east-1
```

### Slack Configuration (for notifications)
```bash
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=C09DTJ9K5PW
```

## Setup Instructions

### 1. AWS S3 Setup
1. Create an S3 bucket in your AWS account
2. Create an IAM user with S3 permissions
3. Generate access keys for the IAM user
4. Set the environment variables above

### 2. Slack Setup
1. Create a Slack app in your workspace
2. Add the following OAuth scopes:
   - `chat:write`
   - `channels:read`
3. Install the app to your workspace
4. Copy the Bot User OAuth Token
5. Set the environment variables above

### 3. Fallback Behavior
- If S3 credentials are not configured, logs will be saved locally in a `logs/` directory
- If Slack credentials are not configured, notifications will be skipped
- The API will still work without these services, but with limited functionality

## Testing the Integration

### Check S3 Status
```bash
curl -X GET "http://localhost:8000/api/v1/s3-status"
```

### Check Slack Status
```bash
curl -X GET "http://localhost:8000/api/v1/slack-status"
```

### Test Crash Simulation
```bash
curl -X POST "http://localhost:8000/api/v1/simulate-crash" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "paystack_timeout",
    "repository_id": "your-repo-id",
    "users_impacted": 1000
  }'
```
