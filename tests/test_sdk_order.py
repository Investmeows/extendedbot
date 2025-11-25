"""
Test SDK order placement
"""
import asyncio
import logging
from decimal import Decimal
from src.clients.extended_sdk_client import ExtendedSDKClient
from x10.perpetual.orders import OrderSide, TimeInForce

logging.basicConfig(level=logging.INFO)

async def test_order():
    try:
        client = ExtendedSDKClient()
        
        # Try to place a simple order using SDK
        result = await client.client.place_order(
            market_name="BTC-USD",
            amount_of_synthetic=Decimal("0.001"),
            price=Decimal("100000"),
            side=OrderSide.BUY,
            time_in_force=TimeInForce.IOC
        )
        
        print(f"Order result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_order())
