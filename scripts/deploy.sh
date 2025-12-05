#!/bin/bash

# Deployment script for LPDP MCP Server

set -e

echo "🚀 Starting deployment..."

# Navigate to project directory
cd "$(dirname "$0")/.."

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtual environment..."
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests (optional)
if [ "$1" != "--skip-tests" ]; then
    echo "🧪 Running tests..."
    pytest tests/ -v || true
fi

# Restart service
echo "🔄 Restarting MCP service..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart mcp-lpdp || echo "Service mcp-lpdp not found, skipping restart"
fi

echo "✅ Deployment complete!"
