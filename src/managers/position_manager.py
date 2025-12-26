"""
Fixed position management module using correct Extended Exchange API.
"""
import logging
import httpx
from typing import Dict, Tuple, List
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
    
    def get_position_notional_value(self, position_data: Dict) -> float:
        """Calculate notional value of a position."""
        return abs(position_data["size"]) * position_data["mark_price"]
    
    def validate_position_sizes(self, positions: Dict, expected_pairs: List[Dict]) -> Tuple[bool, Dict]:
        """
        Validate that each position size is within ~1% of target.
        
        Args:
            positions: Current positions from API {market: {size, side, mark_price, ...}}
            expected_pairs: List of {pair: str, target_size: float}
        
        Returns:
            (is_valid: bool, details: Dict with validation results per pair)
        """
        # Edge case: empty expected_pairs means nothing to validate, which is invalid
        if not expected_pairs:
            return False, {}
        
        TOLERANCE = 0.01  # 1%
        results = {}
        
        for pair_config in expected_pairs:
            pair = pair_config['pair']
            target_size = pair_config['target_size']
            position = positions.get(pair)
            
            if not position:
                results[pair] = {'valid': False, 'reason': 'Position not found'}
                continue
            
            # Calculate notional values
            mark_price = position['mark_price']
            actual_notional = self.get_position_notional_value(position)
            target_notional = target_size
            
            # Check tolerance
            if target_notional > 0:
                diff_pct = abs(actual_notional - target_notional) / target_notional
                is_valid = diff_pct <= TOLERANCE
            else:
                # Target size is 0 or invalid
                is_valid = False
                diff_pct = float('inf')
            
            results[pair] = {
                'valid': is_valid,
                'actual_notional': actual_notional,
                'target_notional': target_notional,
                'diff_pct': diff_pct,
                'mark_price': mark_price,
                'position_size': position['size']
            }
        
        all_valid = all(r['valid'] for r in results.values())
        return all_valid, results
    
    def has_positions(self, positions: Dict) -> bool:
        """Check if there are any open positions."""
        return len(positions) > 0
