import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO, format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)

@dataclass
class FlightData:
    """Flight data structure"""
    icao24: str
    callsign: Optional[str]
    origin_country: str
    time_position: Optional[int]
    last_contact: int
    longitude: Optional[float]
    latitude: Optional[float]
    baro_altitude: Optional[float]
    on_ground: bool
    velocity: Optional[float]
    true_track: Optional[float]
    vertical_rate: Optional[float]
    sensors: Optional[List[int]]
    geo_altitude: Optional[float]
    squawk: Optional[str]
    spi: bool
    position_source: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'icao24': self.icao24,
            'callsign': self.callsign.strip() if self.callsign else None,
            'origin_country': self.origin_country,
            'time_position': self.time_position,
            'last_contact': self.last_contact,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'baro_altitude': self.baro_altitude,
            'on_ground': self.on_ground,
            'velocity': self.velocity,
            'true_track': self.true_track,
            'vertical_rate': self.vertical_rate,
            'geo_altitude': self.geo_altitude,
            'squawk': self.squawk,
            'spi': self.spi,
            'position_source': self.position_source,
            'last_update': datetime.now().isoformat()
        }

class OpenSkyAPIClient:
    """Client for OpenSky Network API"""
    
    def __init__(self, config: Config):
        self.base_url = config.API_BASE_URL
        self.username = config.OPENSKY_USERNAME
        self.password = config.OPENSKY_PASSWORD
        self.session = requests.Session()
        self.min_interval = config.MIN_REQUEST_INTERVAL
        self.timeout = config.REQUEST_TIMEOUT
        self.max_retries = config.MAX_RETRIES
        
        if self.username and self.password:
            self.session.auth = (self.username, self.password)
            
        self.last_request_time = 0
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make rate-limited request to OpenSky API"""
        current_time = time.time()
        if current_time - self.last_request_time < self.min_interval:
            sleep_time = self.min_interval - (current_time - self.last_request_time)
            logger.info(f"Rate limiting: waiting {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}/{endpoint}"
                response = self.session.get(url, params=params, timeout=self.timeout)
                self.last_request_time = time.time()
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    logger.warning("Rate limit exceeded")
                    time.sleep(self.min_interval * (attempt + 1))
                    continue
                else:
                    logger.error(f"API request failed: {response.status_code}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.min_interval * (attempt + 1))
                    continue
                return None
        
        return None
    
    def get_states(self, icao24: Optional[str] = None, 
                   bbox: Optional[tuple] = None) -> List[FlightData]:
        """Get current flight states"""
        params = {}
        
        if icao24:
            params['icao24'] = icao24
        if bbox:
            params['lamin'] = bbox[0]
            params['lamax'] = bbox[1]
            params['lomin'] = bbox[2]
            params['lomax'] = bbox[3]
        
        data = self._make_request("states/all", params)
        
        if not data or 'states' not in data:
            return []
        
        flights = []
        for state in data['states']:
            try:
                flight = FlightData(
                    icao24=state[0],
                    callsign=state[1],
                    origin_country=state[2],
                    time_position=state[3],
                    last_contact=state[4],
                    longitude=state[5],
                    latitude=state[6],
                    baro_altitude=state[7],
                    on_ground=state[8],
                    velocity=state[9],
                    true_track=state[10],
                    vertical_rate=state[11],
                    sensors=state[12],
                    geo_altitude=state[13],
                    squawk=state[14],
                    spi=state[15],
                    position_source=state[16]
                )
                flights.append(flight)
            except (IndexError, TypeError) as e:
                logger.warning(f"Failed to parse flight data: {e}")
                continue
        
        return flights
    
    def get_flights_by_area(self, min_lat: float, max_lat: float, 
                           min_lon: float, max_lon: float) -> List[FlightData]:
        """Get flights in a specific geographic area"""
        bbox = (min_lat, max_lat, min_lon, max_lon)
        return self.get_states(bbox=bbox)
    
    def get_flight_by_icao(self, icao24: str) -> Optional[FlightData]:
        """Get specific flight by ICAO24 code"""
        flights = self.get_states(icao24=icao24)
        return flights[0] if flights else None
    
    def get_flights_by_country(self, country: str) -> List[FlightData]:
        """Get flights by origin country"""
        all_flights = self.get_states()
        return [f for f in all_flights if f.origin_country.lower() == country.lower()]

class FlightTracker:
    """Main flight tracking service"""
    
    def __init__(self, config: Config):
        self.client = OpenSkyAPIClient(config)
        self.tracked_flights = {}
        self.tracking_active = False
        self.config = config
        self.tracking_task = None
        
    async def start_tracking(self, area: Optional[tuple] = None, 
                           interval: Optional[int] = None) -> None:
        """Start continuous flight tracking"""
        self.tracking_active = True
        interval = interval or self.config.DEFAULT_REFRESH_INTERVAL
        
        while self.tracking_active:
            try:
                if len(self.tracked_flights) >= self.config.MAX_TRACKED_FLIGHTS:
                    logger.warning("Maximum tracked flights reached")
                    break
                
                flights = self.client.get_flights_by_area(*area) if area else self.client.get_states()
                
                for flight in flights:
                    self.tracked_flights[flight.icao24] = flight
                
                logger.info(f"Updated {len(flights)} flights")
                
                current_time = time.time()
                to_remove = []
                for icao24, flight in self.tracked_flights.items():
                    if current_time - flight.last_contact > self.config.FLIGHT_EXPIRY_TIME:
                        to_remove.append(icao24)
                
                for icao24 in to_remove:
                    del self.tracked_flights[icao24]
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Tracking error: {e}")
                await asyncio.sleep(interval)
    
    def stop_tracking(self):
        """Stop continuous tracking"""
        self.tracking_active = False
        if self.tracking_task:
            self.tracking_task.cancel()
            self.tracking_task = None
    
    def get_current_flights(self) -> List[Dict]:
        """Get current tracked flights as dictionaries"""
        return [flight.to_dict() for flight in self.tracked_flights.values()]
    
    def get_flight_info(self, icao24: str) -> Optional[Dict]:
        """Get specific flight information"""
        if icao24 in self.tracked_flights:
            return self.tracked_flights[icao24].to_dict()
        
        flight = self.client.get_flight_by_icao(icao24)
        if flight:
            self.tracked_flights[icao24] = flight
            return flight.to_dict()
        
        return None