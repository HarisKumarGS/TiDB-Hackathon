#!/bin/bash

# Installation script for CrashLens Bot - Log Stream Generator
echo "Installing CrashLens Bot dependencies..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    INSTALL_CMD="pip3 install -r requirements.txt"
else
    echo "⚠️  No virtual environment detected."
    echo "   For system-wide installation, you may need to use:"
    echo "   pip3 install -r requirements.txt --user"
    echo "   or create a virtual environment first."
    echo ""
    read -p "Do you want to create a virtual environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Virtual environment created and activated."
        INSTALL_CMD="pip install -r requirements.txt"
    else
        INSTALL_CMD="pip3 install -r requirements.txt --user"
    fi
fi

# Install dependencies from requirements.txt
echo "📦 Installing dependencies from requirements.txt..."
$INSTALL_CMD

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Set up your environment:"
    echo "   ./setup_env.sh"
    echo ""
    echo "2. Configure AWS credentials (optional, for S3 and DynamoDB):"
    echo "   export AWS_ACCESS_KEY_ID='your-aws-access-key'"
    echo "   export AWS_SECRET_ACCESS_KEY='your-aws-secret-key'"
    echo "   export AWS_DEFAULT_REGION='us-east-1'"
    echo "   export S3_BUCKET_NAME='tidb-hackathon-bucket'"
    echo "   export DYNAMODB_TABLE_NAME='tidb-hackathon-crash'"
    echo ""
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "3. Activate virtual environment (if not already active):"
        echo "   source venv/bin/activate"
        echo ""
    fi
    echo "4. Test the installation:"
    echo "   python3 simulate_logs.py paystack_timeout --min-logs 5"
    echo ""
    echo "5. Test the complete workflow:"
    echo "   python3 simulate_logs.py paystack_timeout --min-logs 3"
else
    echo "❌ Failed to install dependencies."
    echo "Try running with --user flag: pip3 install -r requirements.txt --user"
    exit 1
fi
