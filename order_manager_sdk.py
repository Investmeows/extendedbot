"""
Order management using Extended Exchange SDK for proper signature handling.
"""
import time
import math
import logging
from typing import Dict, Tuple
from config import Config

logger = logging.getLogger(__name__)

class OrderManager:
    """Handles order placement using Extended Exchange SDK."""
    
    def __init__(self, sdk_client):
        self.client = sdk_client
        self.long_pair = Config.LONG_PAIR
        self.short_pair = Config.SHORT_PAIR
        self.price_buffer = Config.PRICE_BUFFER
    
    def quantize(self, value: float, step: float) -> str:
        """Quantize value to market step size."""
        # Use ceiling instead of floor to ensure we don't go below minimum
        q = math.ceil(float(value) / float(step)) * float(step)
        # Round to avoid floating point precision issues
        q = round(q, 10)
        
        # Calculate decimal places from step size
        if step >= 1:
            decimal_places = 0
        else:
            # Count decimal places in step
            step_str = f"{step:.10f}".rstrip('0').rstrip('.')
            if '.' in step_str:
                decimal_places = len(step_str.split('.')[1])
            else:
                decimal_places = 0
        
        return f"{q:.{decimal_places}f}"
    
    def get_market_prices(self) -> Tuple[float, float]:
        """Get current long pair ask and short pair bid prices."""
        try:
            import asyncio
            import httpx
            
            # Use direct API calls for market data
            with httpx.Client(timeout=10) as client:
                # Get long pair orderbook
                long_resp = client.get(
                    f"https://api.starknet.extended.exchange/api/v1/info/markets/{self.long_pair}/orderbook",
                    headers={"User-Agent": "extended-bot/1.0"}
                )
                long_data = long_resp.json()["data"]
                long_ask = float(long_data["ask"][0]["price"])
                
                # Get short pair orderbook
                short_resp = client.get(
                    f"https://api.starknet.extended.exchange/api/v1/info/markets/{self.short_pair}/orderbook",
                    headers={"User-Agent": "extended-bot/1.0"}
                )
                short_data = short_resp.json()["data"]
                short_bid = float(short_data["bid"][0]["price"])
                
                return long_ask, short_bid
        except Exception as e:
            logger.error(f"Failed to get market prices: {e}")
            raise
    
    def place_order(self, market: str, side: str, qty: str, price: str) -> bool:
        """Place a single order using SDK."""
        try:
            import asyncio
            from decimal import Decimal
            from x10.perpetual.orders import OrderSide, TimeInForce
            
            # Convert side to OrderSide enum
            order_side = OrderSide.BUY if side.upper() == "BUY" else OrderSide.SELL
            
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Place order using SDK
            result = loop.run_until_complete(self.client.client.place_order(
                market_name=market,
                amount_of_synthetic=Decimal(qty),
                price=Decimal(price),
                side=order_side,
                time_in_force=TimeInForce.IOC
            ))
            
            if result.status == "OK":
                logger.info(f"Order placed successfully: {market} {side} {qty} @ {price}")
                return True
            else:
                logger.error(f"Order failed: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return False
    
    def cancel_all_orders(self):
        """Cancel all existing orders."""
        try:
            import asyncio
            
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(self.client.client.orders.mass_cancel())
            logger.info("All orders cancelled")
        except Exception as e:
            logger.warning(f"Failed to cancel orders: {e}")
    
    def get_market_precision(self, market: str) -> dict:
        """Get market precision requirements."""
        try:
            import httpx
            
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    f"https://api.starknet.extended.exchange/api/v1/info/markets",
                    headers={"User-Agent": "extended-bot/1.0"},
                    params={"market": market}
                )
                market_data = resp.json()["data"][0]
                
                return {
                    "asset_precision": market_data["assetPrecision"],
                    "min_order_size": market_data["tradingConfig"]["minOrderSize"],
                    "min_order_size_change": market_data["tradingConfig"]["minOrderSizeChange"],
                    "min_price_change": market_data["tradingConfig"]["minPriceChange"]
                }
        except Exception as e:
            logger.error(f"Failed to get market precision: {e}")
            return {"asset_precision": 6, "min_order_size_change": "0.001", "min_price_change": "0.01"}

    def open_delta_neutral_positions(self, target_size: float) -> bool:
        """Open long and short positions for delta neutral strategy."""
        try:
            # Cancel existing orders
            self.cancel_all_orders()
            time.sleep(2)
            
            # Get market precision requirements
            long_precision = self.get_market_precision(self.long_pair)
            short_precision = self.get_market_precision(self.short_pair)
            
            logger.info(f"Long precision: {long_precision}")
            logger.info(f"Short precision: {short_precision}")
            
            # Get market prices
            long_ask, short_bid = self.get_market_prices()
            
            # Calculate quantities and prices with proper precision
            long_price_raw = long_ask * (1 + self.price_buffer)
            short_price_raw = short_bid * (1 - self.price_buffer)
            
            # Quantize prices
            long_price = self.quantize(long_price_raw, float(long_precision["min_price_change"]))
            short_price = self.quantize(short_price_raw, float(short_precision["min_price_change"]))
            
            # Calculate and quantize quantities
            long_qty_raw = target_size / float(long_price)
            short_qty_raw = target_size / float(short_price)
            
            # Ensure minimum order size (use minOrderSize, not minOrderSizeChange)
            long_min_size = float(long_precision["min_order_size"])
            short_min_size = float(short_precision["min_order_size"])
            long_step_size = float(long_precision["min_order_size_change"])
            short_step_size = float(short_precision["min_order_size_change"])
            
            # If calculated quantity is too small, use minimum size
            if long_qty_raw < long_min_size:
                long_qty_raw = long_min_size
                logger.warning(f"BTC quantity too small, using minimum: {long_qty_raw}")
            
            if short_qty_raw < short_min_size:
                short_qty_raw = short_min_size
                logger.warning(f"ETH quantity too small, using minimum: {short_qty_raw}")
            
            long_qty = self.quantize(long_qty_raw, long_step_size)
            short_qty = self.quantize(short_qty_raw, short_step_size)
            
            logger.info(f"Quantized quantities: BTC={long_qty}, ETH={short_qty}")
            
            logger.info(f"Opening: {self.long_pair} {long_qty} @ ${long_price}, {self.short_pair} {short_qty} @ ${short_price}")
            
            # Place both orders
            logger.info(f"Placing BTC order: {self.long_pair} BUY {long_qty} @ {long_price}")
            long_success = self.place_order(self.long_pair, "BUY", long_qty, long_price)
            
            logger.info(f"Placing ETH order: {self.short_pair} SELL {short_qty} @ {short_price}")
            short_success = self.place_order(self.short_pair, "SELL", short_qty, short_price)
            
            logger.info(f"Order results: BTC={long_success}, ETH={short_success}")
            
            # If one order failed, try to retry it
            if not long_success and short_success:
                logger.warning("BTC order failed, retrying...")
                time.sleep(2)
                long_success = self.place_order(self.long_pair, "BUY", long_qty, long_price)
                logger.info(f"BTC retry result: {long_success}")
            
            if not short_success and long_success:
                logger.warning("ETH order failed, retrying...")
                time.sleep(2)
                short_success = self.place_order(self.short_pair, "SELL", short_qty, short_price)
                logger.info(f"ETH retry result: {short_success}")
            
            if not long_success:
                logger.error(f"❌ BTC order failed - only ETH short opened")
            if not short_success:
                logger.error(f"❌ ETH order failed - only BTC long opened")
            
            return long_success and short_success
            
        except Exception as e:
            logger.error(f"Failed to open positions: {e}")
            return False
    
    def close_all_positions(self, positions: Dict) -> bool:
        """Close all open positions."""
        try:
            if not positions:
                logger.info("No positions to close")
                return True
            
            self.cancel_all_orders()
            time.sleep(2)
            
            # Get market prices and precision for closing
            long_ask, short_bid = self.get_market_prices()
            long_precision = self.get_market_precision(self.long_pair)
            short_precision = self.get_market_precision(self.short_pair)
            
            # Close long position
            if self.long_pair in positions and positions[self.long_pair]["size"] > 0:
                long_size = abs(positions[self.long_pair]["size"])
                long_price_raw = long_ask * (1 - self.price_buffer)
                long_price = self.quantize(long_price_raw, float(long_precision["min_price_change"]))
                long_qty = self.quantize(long_size, float(long_precision["min_order_size_change"]))
                
                logger.info(f"Closing BTC: SELL {long_qty} @ {long_price}")
                self.place_order(self.long_pair, "SELL", long_qty, long_price)
            
            # Close short position
            if self.short_pair in positions and positions[self.short_pair]["size"] != 0:
                short_size = abs(positions[self.short_pair]["size"])
                short_side = positions[self.short_pair]["side"]
                
                if short_side == "LONG":
                    # Long position - sell to close
                    short_price_raw = short_bid * (1 - self.price_buffer)
                    short_price = self.quantize(short_price_raw, float(short_precision["min_price_change"]))
                    short_qty = self.quantize(short_size, float(short_precision["min_order_size_change"]))
                    logger.info(f"Closing ETH: SELL {short_qty} @ {short_price}")
                    self.place_order(self.short_pair, "SELL", short_qty, short_price)
                else:
                    # Short position - buy to close
                    short_price_raw = short_bid * (1 + self.price_buffer)
                    short_price = self.quantize(short_price_raw, float(short_precision["min_price_change"]))
                    short_qty = self.quantize(short_size, float(short_precision["min_order_size_change"]))
                    logger.info(f"Closing ETH: BUY {short_qty} @ {short_price}")
                    self.place_order(self.short_pair, "BUY", short_qty, short_price)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to close positions: {e}")
            return False
