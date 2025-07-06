import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration settings for the flight tracker"""
    OPENSKY_USERNAME: Optional[str] = None
    OPENSKY_PASSWORD: Optional[str] = None
    API_BASE_URL: str = "https://opensky-network.org/api"
    REQUEST_TIMEOUT: int = 30
    MIN_REQUEST_INTERVAL: int = 10
    MAX_RETRIES: int = 3
    MCP_SERVER_HOST: str = "localhost"
    MCP_SERVER_PORT: int = 8080
    MCP_PROTOCOL_VERSION: str = "2024-11-05"
    MAX_TRACKED_FLIGHTS: int = 1000
    FLIGHT_EXPIRY_TIME: int = 300
    DEFAULT_REFRESH_INTERVAL: int = 30
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    REGIONS = {
        "north_america": {"min_lat": 25.0, "max_lat": 70.0, "min_lon": -170.0, "max_lon": -50.0},
        "europe": {"min_lat": 35.0, "max_lat": 70.0, "min_lon": -25.0, "max_lon": 50.0},
        "asia": {"min_lat": 10.0, "max_lat": 70.0, "min_lon": 60.0, "max_lon": 180.0},
        "oceania": {"min_lat": -50.0, "max_lat": 10.0, "min_lon": 110.0, "max_lon": 180.0}
    }
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables"""
        config = cls()
        config.OPENSKY_USERNAME = os.getenv('OPENSKY_USERNAME')
        config.OPENSKY_PASSWORD = os.getenv('OPENSKY_PASSWORD')
        config.MCP_SERVER_HOST = os.getenv('MCP_SERVER_HOST', config.MCP_SERVER_HOST)
        config.MCP_SERVER_PORT = int(os.getenv('MCP_SERVER_PORT', config.MCP_SERVER_PORT))
        config.LOG_LEVEL = os.getenv('LOG_LEVEL', config.LOG_LEVEL)
        return config