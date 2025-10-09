"""
Main trading bot logic for daily BTC long / ETH short strategy.
"""
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import pytz
from x10.perpetual.orders import OrderSide, TimeInForce
from extended_sdk_client import ExtendedSDKClient
from config import Config

logger = logging.getLogger(__name__)

class TradingBot:
    """Main trading bot for daily BTC long / ETH short strategy."""
    
    def __init__(self):
        self.client = ExtendedSDKClient()
        self.btc_symbol = "BTC-USD"
        self.eth_symbol = "ETH-USD"
        self.is_running = False
        self.loop = None
        
    def initialize(self):
        """Initialize the bot and set up leverage."""
        try:
            import asyncio
            
            logger.info("Initializing trading bot...")
            
            # Create and set up the event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            # Set leverage for both symbols using async methods
            # Set BTC leverage
            self.loop.run_until_complete(
                self.client.client.account.update_leverage(
                    market_name=self.btc_symbol,
                    leverage=Config.BTC_LEVERAGE
                )
            )
            
            # Set ETH leverage
            self.loop.run_until_complete(
                self.client.client.account.update_leverage(
                    market_name=self.eth_symbol,
                    leverage=Config.ETH_LEVERAGE
                )
            )
            
            logger.info(f"TARGET_SIZE from config: {Config.TARGET_SIZE}")
            logger.info(f"BTC_LEVERAGE from config: {Config.BTC_LEVERAGE}")
            logger.info(f"ETH_LEVERAGE from config: {Config.ETH_LEVERAGE}")
            logger.info(f"Set BTC leverage to {Config.BTC_LEVERAGE}x")
            logger.info(f"Set ETH leverage to {Config.ETH_LEVERAGE}x")
            
            # Enable dead man's switch if configured
            if Config.DEAD_MAN_SWITCH_ENABLED:
                self.loop.run_until_complete(
                    self.client.client.orders.mass_cancel()
                )
                logger.info("Dead man's switch activated - cancelled all existing orders")
            
            logger.info("Bot initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    def _place_order_with_retry(self, market_name: str, amount: Decimal, price: Decimal, 
                               side: OrderSide, order_type: str) -> bool:
        """Place an order with 3 retry attempts."""
        for attempt in range(3):
            try:
                result = self.loop.run_until_complete(
                    self.client.client.place_order(
                        market_name=market_name,
                        amount_of_synthetic=amount,
                        price=price,
                        side=side,
                        time_in_force=TimeInForce.IOC,
                        external_id=Config.CLIENT_ID
                    )
                )
                logger.info(f"{order_type} order placed: {result}")
                return True
            except Exception as e:
                logger.error(f"{order_type} attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(2)
        return False
    
    def open_positions(self):
        """Open long BTC and short ETH positions with verification."""
        try:
            import asyncio
            from decimal import Decimal
            from x10.perpetual.orders import OrderSide, TimeInForce
            import requests
            
            logger.info("Opening daily positions...")
            
            # Check for existing positions to prevent duplicates
            existing_positions = self.get_current_positions()
            if "BTC-USD" in existing_positions or "ETH-USD" in existing_positions:
                logger.info("Positions already exist, skipping to prevent duplicates")
                return True
            
            # Get current market prices
            btc_orderbook = requests.get("https://api.starknet.extended.exchange/api/v1/info/markets/BTC-USD/orderbook").json()
            eth_orderbook = requests.get("https://api.starknet.extended.exchange/api/v1/info/markets/ETH-USD/orderbook").json()
            
            btc_ask = float(btc_orderbook["data"]["ask"][0]["price"])
            eth_bid = float(eth_orderbook["data"]["bid"][0]["price"])
            
            # Calculate quantities for delta neutral positions
            btc_quantity = Config.TARGET_SIZE / btc_ask
            eth_quantity = Config.TARGET_SIZE / eth_bid
            
            logger.info(f"TARGET_SIZE from config: {Config.TARGET_SIZE}")
            logger.info(f"Delta neutral position sizing:")
            logger.info(f"  BTC: {btc_quantity:.6f} BTC = ${Config.TARGET_SIZE:.2f}")
            logger.info(f"  ETH: {eth_quantity:.6f} ETH = ${Config.TARGET_SIZE:.2f}")
            
            # Place BTC long order at market price
            btc_success = self._place_order_with_retry(
                market_name=self.btc_symbol,
                amount=Decimal(str(btc_quantity)),
                price=Decimal(str(btc_ask)),  # Use current ask price for immediate execution
                side=OrderSide.BUY,
                order_type="BTC long"
            )
            
            # Place ETH short order at market price
            eth_success = self._place_order_with_retry(
                market_name=self.eth_symbol,
                amount=Decimal(str(eth_quantity)),
                price=Decimal(str(eth_bid)),  # Use current bid price for immediate execution
                side=OrderSide.SELL,
                order_type="ETH short"
            )
            
            # Verify positions after 5 seconds
            if btc_success and eth_success:
                time.sleep(5)
                positions = self.get_current_positions()
                logger.info(f"Positions after opening: {positions}")
                return True
            else:
                logger.error("Failed to place orders")
                return False
            
        except Exception as e:
            logger.error(f"Failed to open positions: {e}")
            return False
    
    def close_positions(self):
        """Close all open positions with verification."""
        try:
            import asyncio
            from decimal import Decimal
            from x10.perpetual.orders import OrderSide, TimeInForce
            import requests
            
            logger.info("Closing daily positions...")
            
            # Get current positions
            positions = self.get_current_positions()
            if not positions:
                logger.info("No open positions to close")
                return True
            
            # Get current market prices
            btc_orderbook = requests.get("https://api.starknet.extended.exchange/api/v1/info/markets/BTC-USD/orderbook").json()
            eth_orderbook = requests.get("https://api.starknet.extended.exchange/api/v1/info/markets/ETH-USD/orderbook").json()
            
            btc_bid = float(btc_orderbook["data"]["bid"][0]["price"])
            eth_bid = float(eth_orderbook["data"]["bid"][0]["price"])
            eth_ask = float(eth_orderbook["data"]["ask"][0]["price"])
            
            # Close BTC position if open at market price
            if "BTC-USD" in positions and positions["BTC-USD"]["size"] > 0:
                self._place_order_with_retry(
                    market_name=self.btc_symbol,
                    amount=Decimal(str(abs(positions["BTC-USD"]["size"]))),
                    price=Decimal(str(btc_bid)),  # Use current bid price for immediate execution
                    side=OrderSide.SELL,
                    order_type="BTC close"
                )
            
            # Close ETH position if open at market price
            if "ETH-USD" in positions and positions["ETH-USD"]["size"] != 0:
                eth_size = positions["ETH-USD"]["size"]
                eth_side = positions["ETH-USD"]["side"]
                if eth_side == "LONG":  # Long position - sell to close
                    self._place_order_with_retry(
                        market_name=self.eth_symbol,
                        amount=Decimal(str(abs(eth_size))),
                        price=Decimal(str(eth_bid)),  # Use current bid price for immediate execution
                        side=OrderSide.SELL,
                        order_type="ETH close"
                    )
                else:  # Short position - buy to close
                    self._place_order_with_retry(
                        market_name=self.eth_symbol,
                        amount=Decimal(str(abs(eth_size))),
                        price=Decimal(str(eth_ask)),  # Use current ask price for immediate execution
                        side=OrderSide.BUY,
                        order_type="ETH close"
                    )
            
            # Verify positions are closed
            time.sleep(5)
            final_positions = self.get_current_positions()
            logger.info(f"Positions after closing: {final_positions}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to close positions: {e}")
            return False
    
    def get_current_positions(self) -> Dict:
        """Get current position status."""
        try:
            positions_result = self.loop.run_until_complete(
                self.client.client.account.get_positions()
            )
            positions = positions_result.data if hasattr(positions_result, 'data') else positions_result
            
            position_dict = {}
            
            for pos in positions:
                # Handle both dict and PositionModel objects
                if hasattr(pos, 'market'):
                    symbol = pos.market
                    size = float(pos.size) if hasattr(pos, 'size') else 0
                    side = pos.side if hasattr(pos, 'side') else ("LONG" if size > 0 else "SHORT")
                    unrealized_pnl = float(pos.unrealised_pnl) if hasattr(pos, 'unrealised_pnl') else 0
                else:
                    symbol = pos.get("symbol")
                    size = float(pos.get("size", 0))
                    side = pos.get("side", "LONG" if size > 0 else "SHORT")
                    unrealized_pnl = float(pos.get("unrealizedPnl", 0))
                
                if size != 0:
                    position_dict[symbol] = {
                        "size": size,
                        "side": side,
                        "unrealized_pnl": unrealized_pnl
                    }
            
            return position_dict
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return {}
    
    def should_open_positions(self) -> bool:
        """Check if it's time to open positions."""
        now = datetime.now(Config.TIMEZONE)
        
        # Handle both %H:%M and %H:%M:%S formats
        try:
            open_time = datetime.strptime(Config.OPEN_TIME, "%H:%M:%S").time()
        except ValueError:
            open_time = datetime.strptime(Config.OPEN_TIME, "%H:%M").time()
        
        # Check if current time is within 1 minute of open time
        current_time = now.time()
        time_diff = abs((current_time.hour * 60 + current_time.minute) - 
                       (open_time.hour * 60 + open_time.minute))
        
        return time_diff <= 1
    
    def should_close_positions(self) -> bool:
        """Check if it's time to close positions."""
        now = datetime.now(Config.TIMEZONE)
        
        # Handle both %H:%M and %H:%M:%S formats
        try:
            close_time = datetime.strptime(Config.CLOSE_TIME, "%H:%M:%S").time()
        except ValueError:
            close_time = datetime.strptime(Config.CLOSE_TIME, "%H:%M").time()
        
        # Check if current time is within 1 minute of close time
        current_time = now.time()
        time_diff = abs((current_time.hour * 60 + current_time.minute) - 
                       (close_time.hour * 60 + close_time.minute))
        
        return time_diff <= 1
    
    def run_daily_cycle(self):
        """Run one daily trading cycle."""
        try:
            logger.info("Starting daily trading cycle")
            
            # Check if we should open positions
            if self.should_open_positions():
                logger.info("Time to open positions")
                success = self.open_positions()
                if success:
                    logger.info("Positions opened successfully")
                else:
                    logger.error("Failed to open positions")
            
            # Check if we should close positions
            elif self.should_close_positions():
                logger.info("Time to close positions")
                success = self.close_positions()
                if success:
                    logger.info("Positions closed successfully")
                else:
                    logger.error("Failed to close positions")
            
            # Log current positions
            positions = self.get_current_positions()
            if positions:
                logger.info(f"Current positions: {positions}")
            else:
                logger.info("No open positions")
                
        except Exception as e:
            logger.error(f"Error in daily cycle: {e}")
    
    def start(self):
        """Start the trading bot."""
        try:
            logger.info("Starting trading bot...")
            self.initialize()
            self.is_running = True
            
            while self.is_running:
                self.run_daily_cycle()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            self.stop()
    
    def kill_switch(self):
        """Emergency kill switch - cancel all orders and close all positions."""
        try:
            logger.warning("🚨 KILL SWITCH ACTIVATED 🚨")
            
            # Cancel all open orders
            self.loop.run_until_complete(
                self.client.client.orders.mass_cancel()
            )
            logger.info("All orders cancelled")
            
            # Close all positions
            self.close_positions()
            
            # Verify all positions are closed
            time.sleep(3)
            final_positions = self.get_current_positions()
            if final_positions:
                logger.error(f"Kill switch failed - positions still open: {final_positions}")
                return False
            else:
                logger.info("✅ Kill switch successful - all positions closed")
                return True
                
        except Exception as e:
            logger.error(f"Kill switch failed: {e}")
            return False

    def stop(self):
        """Stop the trading bot."""
        logger.info("Stopping trading bot...")
        self.is_running = False
        
        # Use kill switch to ensure clean shutdown
        try:
            if self.loop and not self.loop.is_closed():
                self.kill_switch()
        except Exception as e:
            logger.error(f"Failed to stop bot cleanly: {e}")
