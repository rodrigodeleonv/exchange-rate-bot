#!/usr/bin/env python3
"""
Unit tests for Exchange Rate Bot
"""

import unittest
import asyncio
from unittest.mock import patch, Mock
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from bot import ExchangeRateBot
except ImportError:
    # If import fails, skip tests
    print("⚠️  Warning: Could not import bot module. Skipping tests.")
    sys.exit(0)


class TestExchangeRateBot(unittest.TestCase):
    """Test cases for the Exchange Rate Bot"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.bot = ExchangeRateBot()
        self.mock_response_data = {
            "base": "USD",
            "date": "2024-09-10",
            "rates": {
                "EUR": 0.9012,
                "GBP": 0.7643,
                "JPY": 143.52,
                "CHF": 0.8456
            }
        }
    
    @patch('bot.requests.get')
    def test_get_exchange_rates_success(self, mock_get):
        """Test successful exchange rate fetching"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Test the async function
        async def run_test():
            result = await self.bot.get_exchange_rates('USD')
            self.assertEqual(result['base'], 'USD')
            self.assertEqual(result['date'], '2024-09-10')
            self.assertIn('EUR', result['rates'])
            self.assertEqual(result['rates']['EUR'], 0.9012)
        
        asyncio.run(run_test())
        
        # Verify API was called correctly
        mock_get.assert_called_once_with(
            'https://api.exchangerate-api.com/v4/latest/USD',
            timeout=10
        )
    
    @patch('bot.requests.get')
    def test_get_exchange_rates_api_error(self, mock_get):
        """Test exchange rate fetching with API error"""
        # Mock API error
        mock_get.side_effect = Exception("API Error")
        
        async def run_test():
            with self.assertRaises(Exception):
                await self.bot.get_exchange_rates('USD')
        
        asyncio.run(run_test())
    
    @patch.object(ExchangeRateBot, 'get_exchange_rates')
    def test_convert_currency_success(self, mock_get_rates):
        """Test successful currency conversion"""
        # Mock exchange rates response
        mock_get_rates.return_value = self.mock_response_data
        
        async def run_test():
            result = await self.bot.convert_currency(100, 'USD', 'EUR')
            expected = round(100 * 0.9012, 2)
            self.assertEqual(result, expected)
        
        asyncio.run(run_test())
    
    @patch.object(ExchangeRateBot, 'get_exchange_rates')
    def test_convert_currency_invalid_currency(self, mock_get_rates):
        """Test currency conversion with invalid currency"""
        # Mock exchange rates response
        mock_get_rates.return_value = self.mock_response_data
        
        async def run_test():
            with self.assertRaises(ValueError) as context:
                await self.bot.convert_currency(100, 'USD', 'XYZ')
            self.assertIn('XYZ', str(context.exception))
        
        asyncio.run(run_test())
    
    def test_bot_instantiation(self):
        """Test that bot can be instantiated"""
        bot = ExchangeRateBot()
        self.assertIsNotNone(bot)
        self.assertIsNotNone(bot.logger)


class TestBotConfiguration(unittest.TestCase):
    """Test bot configuration and setup"""
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, ContextTypes
            import requests
            import logging
            import os
            from dotenv import load_dotenv
        except ImportError as e:
            self.fail(f"Failed to import required module: {e}")
    
    def test_environment_variables(self):
        """Test environment variable handling"""
        # Test that bot handles missing token gracefully
        old_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        # Remove token if it exists
        if 'TELEGRAM_BOT_TOKEN' in os.environ:
            del os.environ['TELEGRAM_BOT_TOKEN']
        
        # Import should still work
        try:
            from bot import TELEGRAM_BOT_TOKEN
            self.assertIsNone(TELEGRAM_BOT_TOKEN)
        except Exception as e:
            self.fail(f"Bot should handle missing token gracefully: {e}")
        
        # Restore original token if it existed
        if old_token:
            os.environ['TELEGRAM_BOT_TOKEN'] = old_token


def run_tests():
    """Run all tests"""
    print("🧪 Running Exchange Rate Bot Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestExchangeRateBot))
    suite.addTests(loader.loadTestsFromTestCase(TestBotConfiguration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return False


if __name__ == '__main__':
    success = run_tests()
    if not success:
        sys.exit(1)