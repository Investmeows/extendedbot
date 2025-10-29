"""
Extended Exchange SDK client using the official Python SDK.
"""
import time
import logging
from typing import Dict, List, Optional, Any
from config import Config

logger = logging.getLogger(__name__)

class ExtendedSDKClient:
    """Client using the official Extended Exchange Python SDK."""
    
    def __init__(self):
        # Import the SDK here to handle import errors gracefully
        try:
            from x10.perpetual.trading_client.trading_client import PerpetualTradingClient
            from x10.perpetual.trading_client.trading_client import EndpointConfig
            from x10.perpetual.configuration import StarknetDomain
            
            # Create Starknet domain for MAINNET
            starknet_domain = StarknetDomain(
                name="Perpetuals",
                version="v0",
                chain_id="SN_MAIN",  # Mainnet chain ID
                revision="1"
            )
            
            # Create endpoint configuration for MAINNET
            config = EndpointConfig(
                chain_rpc_url="https://rpc.starknet.io",  # Mainnet RPC
                api_base_url="https://api.starknet.extended.exchange/api/v1",  # Mainnet API
                stream_url="wss://api.starknet.extended.exchange/stream.extended.exchange/v1",  # Mainnet WebSocket
                onboarding_url="https://api.starknet.extended.exchange",  # Mainnet onboarding
                signing_domain="extended.exchange",  # Mainnet signing domain
                collateral_asset_contract="",  # Will be filled by SDK
                asset_operations_contract="",  # Will be filled by SDK
                collateral_asset_on_chain_id="",  # Will be filled by SDK
                collateral_decimals=6,
                collateral_asset_id="0x1",
                starknet_domain=starknet_domain
            )
            
            # Create Stark account
            from x10.perpetual.accounts import StarkPerpetualAccount
            
            # Create Stark account with both private and public keys
            stark_account = StarkPerpetualAccount(
                vault=Config.L2_VAULT,
                private_key=Config.L2_KEY,
                public_key=Config.L2_PUBLIC_KEY,
                api_key=Config.API_KEY
            )
            
            # Initialize the SDK client
            self.client = PerpetualTradingClient(
                endpoint_config=config,
                stark_account=stark_account
            )
            
            logger.info("Extended Exchange SDK client initialized successfully")
            
        except ImportError as e:
            logger.error(f"Failed to import Extended Exchange SDK: {e}")
            logger.error("Please install the SDK: pip install x10-python-trading-starknet")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize SDK client: {e}")
            raise
    
    def get_fees(self) -> Dict:
        """Get current trading fees."""
        try:
            import asyncio
            # Run the async method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.client.account.get_fees(market_names=["BTC-USD", "ETH-USD"])
            )
            loop.close()
            return result.data if hasattr(result, 'data') else result
        except Exception as e:
            logger.error(f"Failed to get fees: {e}")
            raise
    
    def get_positions(self) -> List[Dict]:
        """Get current positions."""
        try:
            return self.client.account.get_positions()
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            raise
    
    def get_leverage(self, symbol: str) -> Dict:
        """Get current leverage for a symbol."""
        try:
            return self.client.account.get_leverage(symbol)
        except Exception as e:
            logger.error(f"Failed to get leverage: {e}")
            raise
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """Set leverage for a symbol."""
        try:
            return self.client.account.set_leverage(symbol, leverage)
        except Exception as e:
            logger.error(f"Failed to set leverage: {e}")
            raise
    
    def get_orderbook(self, symbol: str) -> Dict:
        """Get orderbook for a symbol."""
        try:
            # Use markets_info instead of info for orderbook
            return self.client.markets_info.get_markets(symbol)
        except Exception as e:
            logger.error(f"Failed to get orderbook: {e}")
            raise
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place an order using the SDK."""
        try:
            return self.client.place_order(order_data)
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            raise
    
    def cancel_all_orders(self) -> Dict:
        """Cancel all open orders (dead man's switch)."""
        try:
            return self.client.orders.mass_cancel()
        except Exception as e:
            logger.error(f"Failed to cancel all orders: {e}")
            raise
    
    def get_mark_price(self, symbol: str) -> float:
        """Get current mark price for a symbol."""
        try:
            orderbook = self.get_orderbook(symbol)
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            
            if not bids or not asks:
                raise ValueError(f"No market data available for {symbol}")
            
            # Calculate mark price as midpoint
            best_bid = float(bids[0][0])
            best_ask = float(asks[0][0])
            return (best_bid + best_ask) / 2
            
        except Exception as e:
            logger.error(f"Failed to get mark price: {e}")
            raise
    
    def create_market_order(self, symbol: str, side: str, quantity: float, 
                          reduce_only: bool = False) -> Dict:
        """Create a market-like order using limit-IOC."""
        try:
            # Get current market data
            orderbook = self.get_orderbook(symbol)
            if side.upper() == "BUY":
                price = float(orderbook["asks"][0][0]) * (1 + Config.PRICE_BUFFER)
            else:
                price = float(orderbook["bids"][0][0]) * (1 - Config.PRICE_BUFFER)
            
            # Get fees
            fees = self.get_fees()
            taker_fee = fees.get("takerFee", 0.00025)  # Default 0.025%
            
            # Calculate expiry timestamp
            expiry_time = int(time.time() + (Config.ORDER_EXPIRY_DAYS * 24 * 60 * 60)) * 1000
            
            order_data = {
                "symbol": symbol,
                "side": side.upper(),
                "type": "LIMIT",
                "quantity": str(quantity),
                "price": str(price),
                "timeInForce": "IOC",
                "reduceOnly": reduce_only,
                "fee": str(taker_fee),
                "expiryEpochMillis": expiry_time,
                "clientId": "extended-bot"
            }
            
            return order_data
            
        except Exception as e:
            logger.error(f"Failed to create market order: {e}")
            raise
