"""
Region registry for managing multiple regions.
"""
from typing import Dict, List, Optional
from app.core.logging import logger


class RegionRegistry:
    """Registry for managing region configurations and data."""
    
    def __init__(self):
        """Initialize the region registry."""
        self._regions = {}
        logger.info("RegionRegistry initialized")
    
    def register_region(self, region_code: str, region_config: Dict) -> None:
        """
        Register a new region.
        
        Args:
            region_code: Unique region identifier
            region_config: Region configuration dictionary
        """
        self._regions[region_code] = region_config
        logger.info(f"Registered region: {region_code}")
    
    def get_region(self, region_code: str) -> Optional[Dict]:
        """
        Get region configuration by code.
        
        Args:
            region_code: Region identifier
            
        Returns:
            Optional[Dict]: Region configuration or None
        """
        return self._regions.get(region_code)
    
    def list_regions(self) -> List[str]:
        """
        List all registered region codes.
        
        Returns:
            List[str]: List of region codes
        """
        return list(self._regions.keys())
    
    def find_region_by_coordinates(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[str]:
        """
        Find which region contains the given coordinates.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Optional[str]: Region code or None if not found
        """
        for code, config in self._regions.items():
            bounds = config.get("coordinates", {}).get("bounds", {})
            if not bounds:
                continue
            
            if (
                bounds.get("south", float("-inf")) <= latitude <= bounds.get("north", float("inf")) and
                bounds.get("west", float("-inf")) <= longitude <= bounds.get("east", float("inf"))
            ):
                return code
        
        return None


# Global registry instance
registry = RegionRegistry()


def initialize_regions():
    """Initialize and register all supported regions."""
    # Import and register regions
    from app.regions.longueuil import REGION_CONFIG as longueuil_config
    
    registry.register_region("LNG", longueuil_config)
    logger.info("All regions initialized")
