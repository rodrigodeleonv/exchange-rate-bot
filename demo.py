#!/usr/bin/env python3
"""
Demo script to showcase Exchange Rate Bot functionality
This script demonstrates the bot's features without requiring a Telegram bot token.
"""

import asyncio
import sys
import os

# Mock data for demonstration (since API might not be accessible in sandbox)
MOCK_EXCHANGE_RATES = {
    "base": "USD",
    "date": "2024-09-10",
    "rates": {
        "EUR": 0.9012,
        "GBP": 0.7643,
        "JPY": 143.52,
        "CHF": 0.8456,
        "CAD": 1.3598,
        "AUD": 1.4721,
        "CNY": 7.1234,
        "BRL": 5.4321,
        "INR": 83.2456,
        "KRW": 1342.15,
        "MXN": 19.8765
    }
}

class MockExchangeRateBot:
    """Mock version of the exchange rate bot for demonstration"""
    
    def __init__(self):
        self.popular_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY']
    
    async def get_exchange_rates(self, base_currency='USD'):
        """Mock exchange rate fetching"""
        if base_currency == 'USD':
            return MOCK_EXCHANGE_RATES
        elif base_currency == 'EUR':
            # Convert USD rates to EUR base
            eur_rate = MOCK_EXCHANGE_RATES['rates']['EUR']
            eur_rates = {}
            for currency, rate in MOCK_EXCHANGE_RATES['rates'].items():
                if currency != 'EUR':
                    eur_rates[currency] = round(rate / eur_rate, 6)
            eur_rates['USD'] = round(1 / eur_rate, 6)
            return {
                "base": "EUR", 
                "date": "2024-09-10",
                "rates": eur_rates
            }
        else:
            raise ValueError(f"Base currency {base_currency} not supported in demo")
    
    async def convert_currency(self, amount, from_currency, to_currency):
        """Mock currency conversion"""
        rates_data = await self.get_exchange_rates(from_currency)
        
        if to_currency.upper() not in rates_data['rates']:
            raise ValueError(f"Currency {to_currency} not supported")
        
        rate = rates_data['rates'][to_currency.upper()]
        converted_amount = amount * rate
        
        return round(converted_amount, 2)

def format_rates_message(base_currency, rates_data, popular_currencies):
    """Format rates message like the real bot"""
    lines = [f"💱 Exchange Rates ({base_currency} base)\n"]
    lines.append(f"📅 Last updated: {rates_data.get('date', 'Unknown')}\n")
    
    for currency in popular_currencies:
        if currency != base_currency and currency in rates_data['rates']:
            rate = rates_data['rates'][currency]
            lines.append(f"💰 1 {base_currency} = {rate:.4f} {currency}")
    
    return "\n".join(lines)

def format_convert_message(amount, from_currency, to_currency, converted_amount):
    """Format conversion message like the real bot"""
    return f"""💱 Currency Conversion

💰 {amount:,.2f} {from_currency.upper()}
🔄 
💰 {converted_amount:,.2f} {to_currency.upper()}

📊 Rate: 1 {from_currency.upper()} = {(converted_amount/amount):.6f} {to_currency.upper()}"""

async def demo_bot_commands():
    """Demonstrate all bot commands"""
    bot = MockExchangeRateBot()
    
    print("🏦 Exchange Rate Bot - Demo Mode")
    print("=" * 50)
    print()
    
    # Demo /start command
    print("🤖 Command: /start")
    print("-" * 30)
    start_message = """🏦 Welcome to Exchange Rate Bot! 🏦

I can help you with current exchange rates and currency conversions.

Available commands:
/rates - Get current exchange rates for popular currencies
/convert - Convert between currencies (e.g., /convert 100 USD EUR)
/help - Show this help message

Example usage:
• /rates - Shows rates for USD, EUR, GBP, etc.
• /convert 100 USD EUR - Converts 100 USD to EUR
• /convert 50 EUR JPY - Converts 50 EUR to Japanese Yen

Start by trying /rates to see current exchange rates!"""
    
    print(start_message)
    print("\n" + "=" * 50 + "\n")
    
    # Demo /rates command
    print("🤖 Command: /rates")
    print("-" * 30)
    try:
        rates_data = await bot.get_exchange_rates('USD')
        message = format_rates_message('USD', rates_data, bot.popular_currencies)
        print(message)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50 + "\n")
    
    # Demo /rates EUR command
    print("🤖 Command: /rates EUR")
    print("-" * 30)
    try:
        rates_data = await bot.get_exchange_rates('EUR')
        message = format_rates_message('EUR', rates_data, bot.popular_currencies)
        print(message)
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50 + "\n")
    
    # Demo /convert commands
    conversions = [
        (100, 'USD', 'EUR'),
        (50, 'EUR', 'JPY'),
        (1000, 'JPY', 'USD'),
        (25.50, 'GBP', 'CAD')
    ]
    
    for amount, from_curr, to_curr in conversions:
        print(f"🤖 Command: /convert {amount} {from_curr} {to_curr}")
        print("-" * 30)
        try:
            converted = await bot.convert_currency(amount, from_curr, to_curr)
            message = format_convert_message(amount, from_curr, to_curr, converted)
            print(message)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 50 + "\n")
    
    # Demo /help command
    print("🤖 Command: /help")
    print("-" * 30)
    help_text = """🆘 Exchange Rate Bot Help 🆘

Available Commands:

🔹 /start - Welcome message and basic info
🔹 /rates [currency] - Get exchange rates
   • /rates - Popular currencies vs USD
   • /rates EUR - All currencies vs EUR

🔹 /convert <amount> <from> <to> - Convert currencies
   • /convert 100 USD EUR - Convert 100 USD to EUR
   • /convert 50 GBP JPY - Convert 50 GBP to JPY

🔹 /help - Show this help message

Supported currencies: USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, and many more!

Tips:
• Currency codes are case-insensitive (usd = USD)
• All rates are updated in real-time
• Amounts can include decimals (e.g., 123.45)"""
    
    print(help_text)
    print("\n" + "=" * 50 + "\n")
    
    print("✨ Demo completed! This bot is ready for deployment.")
    print("📝 To use with real Telegram:")
    print("   1. Get a bot token from @BotFather")
    print("   2. Create .env file with TELEGRAM_BOT_TOKEN=your_token")
    print("   3. Run: python bot.py")

if __name__ == '__main__':
    print("Starting Exchange Rate Bot Demo...")
    print()
    asyncio.run(demo_bot_commands())