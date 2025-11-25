"""
Fixed position management module using correct Extended Exchange API.
"""
import logging
import httpx
from typing import Dict
from src.config import Config

logger = logging.getLogger(__name__)

class PositionManager:
    """Handles position tracking using correct Extended Exchange API."""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.headers = {
            "X-Api-Key": Config.API_KEY,
            "User-Agent": Config.USER_AGENT
        }
    
    def get_current_positions(self) -> Dict:
        """Get current position status using correct API endpoint."""
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    f"{self.base_url}/user/positions",
                    headers=self.headers
                )
                resp.raise_for_status()
                
                positions_data = resp.json()["data"]
                positions = {}
                
                for pos in positions_data:
                    size = float(pos["size"])
                    # Only include positions with meaningful size (absolute value > 0.00001)
                    # This filters out zero positions and rounding errors
                    if abs(size) > 0.00001:
                        positions[pos["market"]] = {
                            "size": size,
                            "side": pos["side"],
                            "unrealized_pnl": float(pos["unrealisedPnl"]),
                            "mark_price": float(pos["markPrice"]),
                            "leverage": float(pos["leverage"])
                        }
                
                return positions
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return {}
    
    def is_delta_neutral(self, positions: Dict) -> bool:
        """
        Check if positions are delta neutral (long pair + short pair).
        
        Validates:
        1. Exactly two positions (LONG_PAIR and SHORT_PAIR only)
        2. LONG_PAIR has side "LONG" with meaningful size
        3. SHORT_PAIR has side "SHORT" with meaningful size
        """
        if not positions:
            return False
        
        long_pair = Config.LONG_PAIR
        short_pair = Config.SHORT_PAIR
        expected_markets = {long_pair, short_pair}
        actual_markets = set(positions.keys())
        
        # Must have exactly the two expected positions (no more, no less)
        if actual_markets != expected_markets:
            logger.debug(f"Market mismatch: expected {expected_markets}, got {actual_markets}")
            return False
        
        # Validate long position
        long_pos = positions.get(long_pair)
        has_long = (
            long_pos is not None and
            long_pos["side"].upper() == "LONG" and
            abs(long_pos["size"]) > 0.00001
        )
        
        # Validate short position
        short_pos = positions.get(short_pair)
        has_short = (
            short_pos is not None and
            short_pos["side"].upper() == "SHORT" and
            abs(short_pos["size"]) > 0.00001
        )
        
        is_valid = has_long and has_short
        
        if not is_valid:
            logger.debug(f"Delta neutral validation failed: long={has_long}, short={has_short}")
            logger.debug(f"Positions: {positions}")
        
        return is_valid
    
    def has_positions(self, positions: Dict) -> bool:
        """Check if there are any open positions."""
        return len(positions) > 0
