#!/bin/bash

# Exchange Rate Bot Startup Script

echo "🏦 Exchange Rate Bot Startup Script"
echo "=================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and configure your bot token:"
    echo "  cp .env.example .env"
    echo "  nano .env  # Edit and add your TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import telegram" &> /dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "🚀 Starting Exchange Rate Bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python3 bot.py