# CrashLens Bot - Log Stream Generator

A comprehensive log simulation tool that generates realistic production logs followed by stack traces for various error scenarios, with automatic Slack notification capabilities.

## Features

- **Realistic Log Generation**: Simulates production logs across multiple services
- **Error Scenarios**: Pre-configured scenarios for common production issues
- **Stack Trace Generation**: Detailed error traces for debugging
- **Slack Integration**: Automatic error notifications sent to Slack channels
- **S3 Upload**: Automatic upload of error logs to AWS S3 bucket
- **DynamoDB Storage**: Automatic creation of crash metadata entries in DynamoDB
- **Log File Generation**: Creates timestamped log files for analysis (with S3 fallback)
- **Error Analysis**: Intelligent error categorization and impact assessment

## Requirements

- Python 3.8 or higher
- pip3 (Python package installer)

## Installation

### Quick Install
```bash
./install.sh
```

### Manual Install
```bash
pip3 install -r requirements.txt
```

### Test Installation
```bash
python3 test_requirements.py
```

## Configuration

### Environment Setup
Run the setup script to configure environment variables:

```bash
./setup_env.sh
```

This will create a `.env` file with the following variables:

### Required Variables
- `SLACK_BOT_TOKEN` - Your Slack bot token (starts with xoxb-...)
- `SLACK_CHANNEL_ID` - Target Slack channel ID (e.g., C1234567890)

### Optional Variables (for AWS services)
- `AWS_ACCESS_KEY_ID` - AWS access key for S3 and DynamoDB
- `AWS_SECRET_ACCESS_KEY` - AWS secret key for S3 and DynamoDB
- `AWS_DEFAULT_REGION` - AWS region (defaults to us-east-1)
- `S3_BUCKET_NAME` - S3 bucket name (defaults to tidb-hackathon-bucket)
- `DYNAMODB_TABLE_NAME` - DynamoDB table name (defaults to tidb-hackathon-crash)

### Manual Configuration
```bash
export SLACK_BOT_TOKEN="xoxb-your-actual-bot-token-here"
export SLACK_CHANNEL_ID="C1234567890"
export AWS_ACCESS_KEY_ID="your-aws-access-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
export S3_BUCKET_NAME="tidb-hackathon-bucket"
export DYNAMODB_TABLE_NAME="tidb-hackathon-crash"
```

## Usage

### Basic Usage
```bash
python3 simulate_logs.py <scenario>
```

### Available Scenarios
- `paystack_timeout` - Payment gateway timeout
- `migration_type_mismatch` - Database migration type error
- `taskq_oversell` - Inventory oversell detection
- `verify_payment_timeout` - Payment verification timeout
- `db_startup_failure` - Database connection failure
- `stripe_signature_error` - Stripe signature verification error

### Examples
```bash
# Run with minimal logs
python3 simulate_logs.py paystack_timeout --min-logs 5

# Run with JSON format
python3 simulate_logs.py db_startup_failure --format json

# Run without jitter
python3 simulate_logs.py stripe_signature_error --no-jitter
```

## Output

The tool generates:
1. **Console Output**: Real-time log simulation to stdout
2. **Error Analysis**: Detailed error information sent to stderr
3. **S3 Upload**: Error logs uploaded to S3 bucket with path `random-uuid/error/random-uuid.log`
4. **DynamoDB Entry**: Crash metadata stored in DynamoDB with `crashId` as partition key
5. **Local Fallback**: If S3 upload fails, logs are saved locally as fallback
6. **Slack Notification**: Rich formatted message sent to configured Slack channel with S3 link

## DynamoDB Schema

The tool creates entries in DynamoDB with the following schema:

| Attribute | Type | Description |
|-----------|------|-------------|
| `crashId` | String | Partition key - UUID of the crash folder |
| `scenario` | String | Error scenario name (e.g., paystack_timeout) |
| `timestamp` | String | ISO timestamp when the crash occurred |
| `s3Url` | String | Full S3 URL to the log file |
| `s3Key` | String | S3 object key path |
| `errorDetails` | Map | Nested object containing error metadata |
| `errorDetails.title` | String | Human-readable error title |
| `errorDetails.description` | String | Detailed error description |
| `errorDetails.severity` | String | Error severity (CRITICAL, HIGH, MEDIUM, LOW) |
| `errorDetails.component` | String | Affected system component |
| `errorDetails.errorType` | String | Type of error (e.g., ConnectTimeout) |
| `usersImpacted` | Number | Estimated number of users affected |
| `status` | String | Crash status (ACTIVE, RESOLVED, etc.) |
| `createdAt` | String | ISO timestamp when record was created |
| `updatedAt` | String | ISO timestamp when record was last updated |

## Dependencies

See `requirements.txt` for the complete list of dependencies:
- `slack-sdk>=3.26.0` - Slack API integration
- `boto3>=1.34.0` - AWS SDK for S3 integration
- `faker>=20.0.0` - Test data generation (for script.py)

## Files

- `simulate_logs.py` - Main simulation script with Slack integration
- `script.py` - Alternative comprehensive simulator
- `requirements.txt` - Python dependencies
- `install.sh` - Installation script
- `setup_env.sh` - Environment setup script
- `test_requirements.py` - Test script to verify installation

## License

This project is part of the TiDB Hackathon and is available under the MIT License.
