"""
Fixed position management module using correct Extended Exchange API.
"""
import logging
import httpx
from typing import Dict
from config import Config

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
                    if float(pos["size"]) != 0:
                        positions[pos["market"]] = {
                            "size": float(pos["size"]),
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
        """Check if positions are delta neutral (long pair + short pair)."""
        has_long = Config.LONG_PAIR in positions and positions[Config.LONG_PAIR]["side"] == "LONG"
        has_short = Config.SHORT_PAIR in positions and positions[Config.SHORT_PAIR]["side"] == "SHORT"
        
        return has_long and has_short
    
    def has_positions(self, positions: Dict) -> bool:
        """Check if there are any open positions."""
        return len(positions) > 0
