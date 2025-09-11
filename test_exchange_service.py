"""Test the exchange rate service."""

import asyncio
import logging

from src.services.exchange_rate_service import ExchangeRateService


async def test_service():
    """Test the exchange rate service."""
    logging.basicConfig(level=logging.INFO)
    
    service = ExchangeRateService()
    
    print("🏦 Testing Exchange Rate Service...")
    print("=" * 50)
    
    # Test get_all_rates
    print("\n📊 Getting all rates...")
    rates = await service.get_all_rates()
    for bank, rate in rates.items():
        status = f"Q{rate}" if rate else "❌ Failed"
        print(f"  {bank}: {status}")
    
    # Test get_best_buy_rate
    print("\n🏆 Finding best buy rate...")
    best = await service.get_best_buy_rate()
    if best:
        bank, rate = best
        print(f"  Best rate: {bank} at Q{rate}")
    else:
        print("  ❌ No valid rates found")
    
    # Test compare_rates
    print("\n📈 Comparing rates...")
    comparison = await service.compare_rates()
    if comparison["status"] == "success":
        stats = comparison["statistics"]
        print(f"  Min rate: Q{stats['min_rate']}")
        print(f"  Max rate: Q{stats['max_rate']}")
        print(f"  Average: Q{stats['average_rate']}")
        print(f"  Spread: Q{stats['spread']} ({stats['spread_percentage']}%)")
        
        print("\n💡 Recommendations:")
        for rec in comparison["recommendations"]:
            print(f"  • {rec}")
    else:
        print(f"  ❌ {comparison['message']}")


if __name__ == "__main__":
    asyncio.run(test_service())
