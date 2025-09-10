#!/usr/bin/env python3
"""
Telegram Exchange Rate Bot

A bot that provides current exchange rates and currency conversion.
"""

import os
import logging
import requests
from typing import Dict, Any
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest"

# Common currency codes for easier access
POPULAR_CURRENCIES = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY']


class ExchangeRateBot:
    """Main bot class handling all exchange rate operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def get_exchange_rates(self, base_currency: str = 'USD') -> Dict[str, Any]:
        """
        Fetch exchange rates from the API.
        
        Args:
            base_currency: The base currency code (default: USD)
            
        Returns:
            Dictionary containing exchange rate data
        """
        try:
            url = f"{EXCHANGE_API_URL}/{base_currency.upper()}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching exchange rates: {e}")
            raise
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Convert amount from one currency to another.
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            
        Returns:
            Converted amount
        """
        try:
            # Get rates with from_currency as base
            rates_data = await self.get_exchange_rates(from_currency)
            
            if to_currency.upper() not in rates_data['rates']:
                raise ValueError(f"Currency {to_currency} not supported")
            
            rate = rates_data['rates'][to_currency.upper()]
            converted_amount = amount * rate
            
            return round(converted_amount, 2)
        except Exception as e:
            self.logger.error(f"Error converting currency: {e}")
            raise


# Initialize bot instance
exchange_bot = ExchangeRateBot()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🏦 *Welcome to Exchange Rate Bot!* 🏦

I can help you with current exchange rates and currency conversions.

*Available commands:*
/rates - Get current exchange rates for popular currencies
/convert - Convert between currencies (e.g., /convert 100 USD EUR)
/help - Show this help message

*Example usage:*
• `/rates` - Shows rates for USD, EUR, GBP, etc.
• `/convert 100 USD EUR` - Converts 100 USD to EUR
• `/convert 50 EUR JPY` - Converts 50 EUR to Japanese Yen

Start by trying `/rates` to see current exchange rates!
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🆘 *Exchange Rate Bot Help* 🆘

*Available Commands:*

🔹 `/start` - Welcome message and basic info
🔹 `/rates [currency]` - Get exchange rates
   • `/rates` - Popular currencies vs USD
   • `/rates EUR` - All currencies vs EUR

🔹 `/convert <amount> <from> <to>` - Convert currencies
   • `/convert 100 USD EUR` - Convert 100 USD to EUR
   • `/convert 50 GBP JPY` - Convert 50 GBP to JPY

🔹 `/help` - Show this help message

*Supported currencies:* USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, and many more!

*Tips:*
• Currency codes are case-insensitive (usd = USD)
• All rates are updated in real-time
• Amounts can include decimals (e.g., 123.45)
    """
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown'
    )


async def rates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Get current exchange rates."""
    try:
        # Check if user specified a base currency
        base_currency = 'USD'
        if context.args:
            base_currency = context.args[0].upper()
        
        # Send "typing" action to show bot is working
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Get exchange rates
        rates_data = await exchange_bot.get_exchange_rates(base_currency)
        
        # Format response for popular currencies
        response_lines = [f"💱 *Exchange Rates ({base_currency} base)*\n"]
        response_lines.append(f"📅 Last updated: {rates_data.get('date', 'Unknown')}\n")
        
        # Show rates for popular currencies
        for currency in POPULAR_CURRENCIES:
            if currency != base_currency and currency in rates_data['rates']:
                rate = rates_data['rates'][currency]
                response_lines.append(f"💰 1 {base_currency} = {rate:.4f} {currency}")
        
        # If base currency is not USD, also show USD rate
        if base_currency != 'USD' and 'USD' in rates_data['rates']:
            usd_rate = rates_data['rates']['USD']
            response_lines.append(f"💰 1 {base_currency} = {usd_rate:.4f} USD")
        
        response_text = "\n".join(response_lines)
        
        await update.message.reply_text(
            response_text,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in rates command: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't fetch the exchange rates right now. Please try again later."
        )


async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Convert currency amounts."""
    try:
        # Check if we have the right number of arguments
        if len(context.args) != 3:
            await update.message.reply_text(
                "❌ Invalid format. Use: `/convert <amount> <from_currency> <to_currency>`\n"
                "Example: `/convert 100 USD EUR`",
                parse_mode='Markdown'
            )
            return
        
        amount_str, from_currency, to_currency = context.args
        
        # Validate amount
        try:
            amount = float(amount_str)
            if amount <= 0:
                await update.message.reply_text("❌ Amount must be a positive number.")
                return
        except ValueError:
            await update.message.reply_text("❌ Invalid amount. Please enter a valid number.")
            return
        
        # Send "typing" action to show bot is working
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Perform conversion
        converted_amount = await exchange_bot.convert_currency(
            amount, from_currency, to_currency
        )
        
        # Format response
        response_text = f"""
💱 *Currency Conversion*

💰 {amount:,.2f} {from_currency.upper()}
🔄 
💰 {converted_amount:,.2f} {to_currency.upper()}

📊 Rate: 1 {from_currency.upper()} = {(converted_amount/amount):.6f} {to_currency.upper()}
        """
        
        await update.message.reply_text(
            response_text.strip(),
            parse_mode='Markdown'
        )
        
    except ValueError as e:
        await update.message.reply_text(f"❌ {str(e)}")
    except Exception as e:
        logger.error(f"Error in convert command: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't perform the conversion right now. Please try again later."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)


def main() -> None:
    """Start the bot."""
    # Check if token is provided
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable is not set")
        print("Please create a .env file with your bot token:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return
    
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rates", rates))
    application.add_handler(CommandHandler("convert", convert))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting Exchange Rate Bot...")
    print("🚀 Exchange Rate Bot is starting...")
    print("Press Ctrl+C to stop the bot")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()