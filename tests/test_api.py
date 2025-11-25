"""
Test script to verify Extended Exchange API integration works.
"""
import os
from dotenv import load_dotenv
from src.managers.order_manager import OrderManager
from src.managers.position_manager import PositionManager
from src.config import Config

# Load environment variables
load_dotenv()

def test_api_connection():
    """Test basic API connectivity."""
    print("Testing Extended Exchange API connection...")
    
    try:
        # Test position manager
        pos_manager = PositionManager()
        positions = pos_manager.get_current_positions()
        print(f"✅ Positions API working: {len(positions)} positions found")
        
        # Test order manager market data
        # Note: OrderManager requires an SDK client, so this test may need updating
        from src.clients.extended_sdk_client import ExtendedSDKClient
        sdk_client = ExtendedSDKClient()
        order_manager = OrderManager(sdk_client)
        long_ask, short_bid = order_manager.get_market_prices()
        print(f"✅ Market data API working: {Config.LONG_PAIR} ask=${long_ask:.2f}, {Config.SHORT_PAIR} bid=${short_bid:.2f}")
        
        # Test market precision
        long_config = order_manager.get_market_precision(Config.LONG_PAIR)
        print(f"✅ Market precision API working: {Config.LONG_PAIR} min_price_change={long_config['min_price_change']}")
        
        print("\n🎉 All API tests passed! Bot should work now.")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    test_api_connection()
