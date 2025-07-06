import React, { useState, useEffect, useRef } from 'react';
import { MapPin, Plane, Play, Square, RefreshCw, Settings, AlertCircle } from 'lucide-react';
import FlightAPI from '../api';

const FlightTracker = () => {
  const [flights, setFlights] = useState([]);
  const [isTracking, setIsTracking] = useState(false);
  const [location, setLocation] = useState({ lat: 40.7128, lon: -74.0060 });
  const [radius, setRadius] = useState(0.5);
  const [interval, setInterval] = useState(10);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFlight, setSelectedFlight] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  
  const intervalRef = useRef(null);

  const fetchFlights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await FlightAPI.getFlightsByArea(
        location.lat - radius,
        location.lat + radius,
        location.lon - radius,
        location.lon + radius
      );
      
      setFlights(result.content[0].text ? JSON.parse(result.content[0].text).flights : []);
      setLastUpdate(new Date());
    } catch (err) {
      setError('Failed to fetch flight data');
      console.error('Error fetching flights:', err);
    } finally {
      setLoading(false);
    }
  };

  const startTracking = async () => {
    setIsTracking(true);
    setError(null);
    
    try {
      await FlightAPI.makeRequest('tools/call', {
        name: 'start_continuous_tracking',
        arguments: {
          latitude: location.lat,
          longitude: location.lon,
          radius: radius,
          interval: interval
        }
      });
      
      intervalRef.current = setInterval(fetchFlights, interval * 1000);
      
    } catch (err) {
      setError('Failed to start tracking');
      setIsTracking(false);
    }
  };

  const stopTracking = async () => {
    setIsTracking(false);
    
    try {
      await FlightAPI.makeRequest('tools/call', {
        name: 'stop_tracking',
        arguments: {}
      });
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    } catch (err) {
      setError('Failed to stop tracking');
    }
  };

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
        },
        (error) => {
          setError('Failed to get location');
        }
      );
    } else {
      setError('Geolocation not supported');
    }
  };

  const formatAltitude = (altitude) => {
    if (!altitude) return 'N/A';
    return `${Math.round(altitude).toLocaleString()} ft`;
  };

  const formatSpeed = (velocity) => {
    if (!velocity) return 'N/A';
    return `${Math.round(velocity)} kts`;
  };

  const formatDirection = (track) => {
    if (!track) return 'N/A';
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    const index = Math.round(track / 22.5) % 16;
    return `${Math.round(track)}° ${directions[index]}`;
  };

  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            Flight Tracker
          </h1>
          <p className="text-slate-300">Real-time flight monitoring over your location</p>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 mb-8 border border-slate-700">
          <div className="flex flex-wrap gap-4 items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={getUserLocation}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                <MapPin className="w-4 h-4" />
                Use My Location
              </button>
              
              <div className="flex items-center gap-2">
                <span className="text-sm text-slate-300">Lat:</span>
                <input
                  type="number"
                  value={location.lat}
                  onChange={(e) => setLocation({...location, lat: parseFloat(e.target.value)})}
                  className="w-24 px-2 py-1 bg-slate-700 rounded text-sm"
                  step="0.0001"
                />
                <span className="text-sm text-slate-300">Lon:</span>
                <input
                  type="number"
                  value={location.lon}
                  onChange={(e) => setLocation({...location, lon: parseFloat(e.target.value)})}
                  className="w-24 px-2 py-1 bg-slate-700 rounded text-sm"
                  step="0.0001"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 text-slate-400 hover:text-white transition-colors"
              >
                <Settings className="w-5 h-5" />
              </button>
              
              <button
                onClick={fetchFlights}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 rounded-lg transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </button>
              
              <button
                onClick={isTracking ? stopTracking : startTracking}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  isTracking 
                    ? 'bg-red-600 hover:bg-red-700' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isTracking ? <Square className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                {isTracking ? 'Stop' : 'Start'} Tracking
              </button>
            </div>
          </div>

          {showSettings && (
            <div className="mt-4 pt-4 border-t border-slate-700">
              <div className="flex gap-4 items-center">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-300">Radius:</span>
                  <input
                    type="range"
                    min="0.1"
                    max="2"
                    step="0.1"
                    value={radius}
                    onChange={(e) => setRadius(parseFloat(e.target.value))}
                    className="w-24"
                  />
                  <span className="text-sm text-slate-300">{radius}°</span>
                </div>
                
                <div className="flex items-center gap-2">
                  <span className="text-sm text-slate-300">Interval:</span>
                  <input
                    type="range"
                    min="5"
                    max="30"
                    step="1"
                    value={interval}
                    onChange={(e) => setInterval(parseInt(e.target.value))}
                    className="w-24"
                  />
                  <span className="text-sm text-slate-300">{interval}s</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-6 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-200">{error}</span>
          </div>
        )}

        {lastUpdate && (
          <div className="text-center text-slate-400 text-sm mb-6">
            Last updated: {lastUpdate.toLocaleString()}
            {isTracking && <span className="text-green-400 ml-2">● Live</span>}
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {flights.map((flight) => (
            <div
              key={flight.icao24}
              className={`bg-slate-800/50 backdrop-blur-sm rounded-lg p-4 border transition-all cursor-pointer hover:bg-slate-800/70 ${
                selectedFlight?.icao24 === flight.icao24 
                  ? 'border-blue-500 bg-slate-800/70' 
                  : 'border-slate-700'
              }`}
              onClick={() => setSelectedFlight(flight)}
            >
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2 bg-blue-600/20 rounded-lg">
                  <Plane className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">
                    {flight.callsign || 'Unknown'}
                  </h3>
                  <p className="text-xs text-slate-400">{flight.icao24}</p>
                </div>
              </div>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Country:</span>
                  <span className="text-white">{flight.origin_country}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Altitude:</span>
                  <span className="text-white">{formatAltitude(flight.baro_altitude)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Speed:</span>
                  <span className="text-white">{formatSpeed(flight.velocity)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Direction:</span>
                  <span className="text-white">{formatDirection(flight.true_track)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Status:</span>
                  <span className={`${flight.on_ground ? 'text-yellow-400' : 'text-green-400'}`}>
                    {flight.on_ground ? 'On Ground' : 'In Flight'}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {flights.length === 0 && !loading && (
          <div className="text-center py-12">
            <Plane className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <p className="text-slate-400">No flights detected in the area</p>
            <p className="text-slate-500 text-sm mt-2">Try adjusting your location or radius</p>
          </div>
        )}

        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-slate-400">Scanning for flights...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlightTracker;