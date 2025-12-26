"""
Order management using Extended Exchange SDK for proper signature handling.
"""
import time
import math
import logging
from typing import Dict, Tuple, List
from src.config import Config

logger = logging.getLogger(__name__)

class OrderManager:
    """Handles order placement using Extended Exchange SDK."""
    
    def __init__(self, sdk_client):
        self.client = sdk_client
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
        """Get current first long pair ask and first short pair bid prices (backward compatibility).
        
        Note: This method is deprecated. Use get_market_prices_for_pairs() instead.
        """
        long_pairs = Config.get_all_long_pairs()
        short_pairs = Config.get_all_short_pairs()
        
        if not long_pairs or not short_pairs:
            raise ValueError(
                "Cannot use get_market_prices(): No pairs configured. "
                "Use get_market_prices_for_pairs() with explicit pair list instead."
            )
        
        long_pair = long_pairs[0]['pair']
        short_pair = short_pairs[0]['pair']
        prices = self.get_market_prices_for_pairs([long_pair, short_pair])
        # Extract ask from long pair and bid from short pair
        long_ask = prices[long_pair][0]
        short_bid = prices[short_pair][1]
        return (long_ask, short_bid)
    
    def get_market_prices_for_pairs(self, pairs: List[str]) -> Dict[str, Tuple[float, float]]:
        """
        Get current ask and bid prices for multiple pairs.
        
        Returns:
            Dict mapping pair name to (ask_price, bid_price) tuple
        """
        try:
            import httpx
            
            prices = {}
            with httpx.Client(timeout=10) as client:
                for pair in pairs:
                    try:
                        resp = client.get(
                            f"https://api.starknet.extended.exchange/api/v1/info/markets/{pair}/orderbook",
                            headers={"User-Agent": "extended-bot/1.0"}
                        )
                        data = resp.json()["data"]
                        ask = float(data["ask"][0]["price"])
                        bid = float(data["bid"][0]["price"])
                        prices[pair] = (ask, bid)
                    except Exception as e:
                        logger.error(f"Failed to get prices for {pair}: {e}")
                        raise
            
            return prices
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
        """Open long and short positions (deprecated wrapper).
        
        This method is kept for backward compatibility but is deprecated.
        Use open_all_positions() directly with pairs from Config.get_all_long_pairs().
        """
        long_pairs = Config.get_all_long_pairs()
        short_pairs = Config.get_all_short_pairs()
        
        if not long_pairs and not short_pairs:
            raise ValueError(
                "No pairs configured. Please set LONG_PAIR1/SHORT_PAIR1 with corresponding *_TARGET_SIZE values."
            )
        
        return self.open_all_positions(long_pairs, short_pairs)
    
    def open_all_positions(self, long_pairs: List[Dict], short_pairs: List[Dict]) -> bool:
        """
        Open positions for all configured long and short pairs.
        
        Args:
            long_pairs: List of {pair: str, target_size: float}
            short_pairs: List of {pair: str, target_size: float}
        
        Returns:
            True if all orders succeeded, False otherwise
        """
        try:
            # Cancel existing orders
            self.cancel_all_orders()
            time.sleep(2)
            
            all_pairs = [p['pair'] for p in long_pairs] + [p['pair'] for p in short_pairs]
            if not all_pairs:
                logger.warning("No pairs configured to open")
                return False
            
            # Get market prices for all pairs
            prices = self.get_market_prices_for_pairs(all_pairs)
            
            # Get precision for all pairs
            precisions = {}
            for pair in all_pairs:
                precisions[pair] = self.get_market_precision(pair)
            
            results = {}
            
            # Open long positions
            for pair_config in long_pairs:
                pair = pair_config['pair']
                target_size = pair_config['target_size']
                
                try:
                    ask, _ = prices[pair]
                    precision = precisions[pair]
                    
                    # Calculate price and quantity
                    price_raw = ask * (1 + self.price_buffer)
                    price = self.quantize(price_raw, float(precision["min_price_change"]))
                    
                    qty_raw = target_size / float(price)
                    min_size = float(precision["min_order_size"])
                    step_size = float(precision["min_order_size_change"])
                    
                    if qty_raw < min_size:
                        qty_raw = min_size
                        logger.warning(f"{pair} quantity too small, using minimum: {qty_raw}")
                    
                    qty = self.quantize(qty_raw, step_size)
                    
                    logger.info(f"Opening LONG: {pair} {qty} @ ${price} (target: ${target_size})")
                    success = self.place_order(pair, "BUY", qty, price)
                    results[pair] = success
                    
                    if not success:
                        logger.error(f"❌ Failed to open LONG position for {pair}")
                        # Retry once
                        time.sleep(2)
                        success = self.place_order(pair, "BUY", qty, price)
                        results[pair] = success
                        if success:
                            logger.info(f"✅ Retry succeeded for {pair}")
                
                except Exception as e:
                    logger.error(f"Failed to open LONG position for {pair}: {e}")
                    results[pair] = False
            
            # Open short positions
            for pair_config in short_pairs:
                pair = pair_config['pair']
                target_size = pair_config['target_size']
                
                try:
                    _, bid = prices[pair]
                    precision = precisions[pair]
                    
                    # Calculate price and quantity
                    price_raw = bid * (1 - self.price_buffer)
                    price = self.quantize(price_raw, float(precision["min_price_change"]))
                    
                    qty_raw = target_size / float(price)
                    min_size = float(precision["min_order_size"])
                    step_size = float(precision["min_order_size_change"])
                    
                    if qty_raw < min_size:
                        qty_raw = min_size
                        logger.warning(f"{pair} quantity too small, using minimum: {qty_raw}")
                    
                    qty = self.quantize(qty_raw, step_size)
                    
                    logger.info(f"Opening SHORT: {pair} {qty} @ ${price} (target: ${target_size})")
                    success = self.place_order(pair, "SELL", qty, price)
                    results[pair] = success
                    
                    if not success:
                        logger.error(f"❌ Failed to open SHORT position for {pair}")
                        # Retry once
                        time.sleep(2)
                        success = self.place_order(pair, "SELL", qty, price)
                        results[pair] = success
                        if success:
                            logger.info(f"✅ Retry succeeded for {pair}")
                
                except Exception as e:
                    logger.error(f"Failed to open SHORT position for {pair}: {e}")
                    results[pair] = False
            
            all_succeeded = all(results.values())
            if not all_succeeded:
                failed = [pair for pair, success in results.items() if not success]
                logger.error(f"❌ Failed to open positions for: {', '.join(failed)}")
            
            return all_succeeded
            
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
            
            # Get all pairs that need to be closed
            pairs_to_close = list(positions.keys())
            if not pairs_to_close:
                return True
            
            # Get market prices for all pairs
            prices = self.get_market_prices_for_pairs(pairs_to_close)
            
            # Close each position
            for pair, position_data in positions.items():
                try:
                    size = abs(position_data["size"])
                    if size <= 0.00001:
                        continue
                    
                    side = position_data["side"]
                    precision = self.get_market_precision(pair)
                    ask, bid = prices[pair]
                    
                    if side.upper() == "LONG":
                        # Long position - sell to close
                        price_raw = bid * (1 - self.price_buffer)
                        price = self.quantize(price_raw, float(precision["min_price_change"]))
                        qty = self.quantize(size, float(precision["min_order_size_change"]))
                        logger.info(f"Closing LONG {pair}: SELL {qty} @ {price}")
                        self.place_order(pair, "SELL", qty, price)
                    else:
                        # Short position - buy to close
                        price_raw = ask * (1 + self.price_buffer)
                        price = self.quantize(price_raw, float(precision["min_price_change"]))
                        qty = self.quantize(size, float(precision["min_order_size_change"]))
                        logger.info(f"Closing SHORT {pair}: BUY {qty} @ {price}")
                        self.place_order(pair, "BUY", qty, price)
                
                except Exception as e:
                    logger.error(f"Failed to close position for {pair}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to close positions: {e}")
            return False
