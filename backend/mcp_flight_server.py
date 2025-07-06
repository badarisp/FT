#!/usr/bin/env python3

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from config import Config
from flight_data_service import FlightTracker, FlightData

class MCPServer:
    """Model Context Protocol Server for Flight Tracking"""
    
    def __init__(self, config: Config):
        self.config = config
        self.flight_tracker = FlightTracker(config)
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format=self.config.LOG_FORMAT
        )
        self.logger = logging.getLogger(__name__)
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request"""
        try:
            method = request.get('method')
            params = request.get('params', {})
            request_id = request.get('id')
            
            if method == 'initialize':
                return await self.initialize(params, request_id)
            elif method == 'tools/list':
                return await self.list_tools(request_id)
            elif method == 'tools/call':
                return await self.call_tool(params, request_id)
            elif method == 'resources/list':
                return await self.list_resources(request_id)
            elif method == 'resources/read':
                return await self.read_resource(params, request_id)
            else:
                return self.error_response(f"Unknown method: {method}", request_id)
                
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return self.error_response(str(e), request.get('id'))
    
    async def initialize(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Initialize the MCP server"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": self.config.MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True}
                },
                "serverInfo": {
                    "name": "flight-tracker",
                    "version": "1.0.0"
                }
            }
        }
    
    async def list_tools(self, request_id: str) -> Dict[str, Any]:
        """List available tools"""
        tools = [
            {
                "name": "get_flights_by_area",
                "description": "Get flights in a specific geographic area",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "min_lat": {"type": "number"},
                        "max_lat": {"type": "number"},
                        "min_lon": {"type": "number"},
                        "max_lon": {"type": "number"}
                    },
                    "required": ["min_lat", "max_lat", "min_lon", "max_lon"]
                }
            },
            {
                "name": "get_flight_by_icao",
                "description": "Get specific flight by ICAO24 code",
                "inputSchema": {
                    "type": "object",
                    "properties": {"icao24": {"type": "string"}},
                    "required": ["icao24"]
                }
            },
            {
                "name": "get_flights_by_country",
                "description": "Get flights by origin country",
                "inputSchema": {
                    "type": "object",
                    "properties": {"country": {"type": "string"}},
                    "required": ["country"]
                }
            },
            {
                "name": "get_all_flights",
                "description": "Get all currently tracked flights",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "search_flights",
                "description": "Search flights by callsign pattern",
                "inputSchema": {
                    "type": "object",
                    "properties": {"callsign_pattern": {"type": "string"}},
                    "required": ["callsign_pattern"]
                }
            },
            {
                "name": "start_continuous_tracking",
                "description": "Start continuous flight tracking",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "radius": {"type": "number"},
                        "interval": {"type": "number"}
                    },
                    "required": ["latitude", "longitude", "radius", "interval"]
                }
            },
            {
                "name": "stop_tracking",
                "description": "Stop continuous flight tracking",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"tools": tools}
        }
    
    async def call_tool(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Call a specific tool"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        try:
            if tool_name == 'get_flights_by_area':
                result = await self.get_flights_by_area(arguments)
            elif tool_name == 'get_flight_by_icao':
                result = await self.get_flight_by_icao(arguments)
            elif tool_name == 'get_flights_by_country':
                result = await self.get_flights_by_country(arguments)
            elif tool_name == 'get_all_flights':
                result = await self.get_all_flights()
            elif tool_name == 'search_flights':
                result = await self.search_flights(arguments)
            elif tool_name == 'start_continuous_tracking':
                result = await self.start_continuous_tracking(arguments)
            elif tool_name == 'stop_tracking':
                result = await self.stop_tracking()
            else:
                return self.error_response(f"Unknown tool: {tool_name}", request_id)
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {"type": "text", "text": json.dumps(result, indent=2)}
                    ]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}")
            return self.error_response(str(e), request_id)
    
    async def get_flights_by_area(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get flights in a specific area"""
        min_lat = args['min_lat']
        max_lat = args['max_lat']
        min_lon = args['min_lon']
        max_lon = args['max_lon']
        
        flights = self.flight_tracker.client.get_flights_by_area(
            min_lat, max_lat, min_lon, max_lon
        )
        
        return {
            "flights": [flight.to_dict() for flight in flights],
            "count": len(flights),
            "area": {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon
            }
        }
    
    async def get_flight_by_icao(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific flight by ICAO24"""
        icao24 = args['icao24']
        flight_data = self.flight_tracker.get_flight_info(icao24)
        
        if flight_data:
            return {"flight": flight_data, "found": True}
        else:
            return {"flight": None, "found": False, "message": f"Flight {icao24} not found"}
    
    async def get_flights_by_country(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get flights by country"""
        country = args['country']
        flights = self.flight_tracker.client.get_flights_by_country(country)
        
        return {
            "flights": [flight.to_dict() for flight in flights],
            "count": len(flights),
            "country": country
        }
    
    async def get_all_flights(self) -> Dict[str, Any]:
        """Get all currently tracked flights"""
        flights = self.flight_tracker.get_current_flights()
        
        return {
            "flights": flights,
            "count": len(flights),
            "timestamp": self.flight_tracker.client.last_request_time
        }
    
    async def search_flights(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search flights by callsign pattern"""
        pattern = args['callsign_pattern'].lower()
        all_flights = self.flight_tracker.client.get_states()
        
        matching_flights = []
        for flight in all_flights:
            if flight.callsign and pattern in flight.callsign.lower():
                matching_flights.append(flight.to_dict())
        
        return {
            "flights": matching_flights,
            "count": len(matching_flights),
            "search_pattern": pattern
        }
    
    async def start_continuous_tracking(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Start continuous flight tracking"""
        latitude = args['latitude']
        longitude = args['longitude']
        radius = args['radius']
        interval = args['interval']
        
        min_lat = latitude - radius
        max_lat = latitude + radius
        min_lon = longitude - radius
        max_lon = longitude + radius
        
        if self.flight_tracker.tracking_active:
            return {"status": "already_running"}
        
        self.flight_tracker.tracking_task = asyncio.create_task(
            self.flight_tracker.start_tracking(
                area=(min_lat, max_lat, min_lon, max_lon),
                interval=interval
            )
        )
        return {"status": "started", "area": {"min_lat": min_lat, "max_lat": max_lat, "min_lon": min_lon, "max_lon": max_lon}}
    
    async def stop_tracking(self) -> Dict[str, Any]:
        """Stop continuous flight tracking"""
        if not self.flight_tracker.tracking_active:
            return {"status": "not_running"}
        
        self.flight_tracker.stop_tracking()
        return {"status": "stopped"}
    
    async def list_resources(self, request_id: str) -> Dict[str, Any]:
        """List available resources"""
        resources = [
            {"uri": "flight://current", "name": "Current Flights", "description": "Currently tracked flights", "mimeType": "application/json"},
            {"uri": "flight://stats", "name": "Flight Statistics", "description": "Flight tracking statistics", "mimeType": "application/json"}
        ]
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {"resources": resources}
        }
    
    async def read_resource(self, params: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Read a specific resource"""
        uri = params.get('uri')
        
        if uri == "flight://current":
            content = self.flight_tracker.get_current_flights()
        elif uri == "flight://stats":
            content = {
                "total_flights": len(self.flight_tracker.tracked_flights),
                "last_update": self.flight_tracker.client.last_request_time,
                "tracking_active": self.flight_tracker.tracking_active
            }
        else:
            return self.error_response(f"Unknown resource: {uri}", request_id)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "contents": [
                    {"uri": uri, "mimeType": "application/json", "text": json.dumps(content, indent=2)}
                ]
            }
        }
    
    def error_response(self, message: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Create error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32000, "message": message}
        }

class MCPTransport:
    """Transport layer for MCP communication"""
    
    def __init__(self, server: MCPServer):
        self.server = server
        self.running = False
    
    async def start(self):
        """Start the MCP transport"""
        self.running = True
        
        while self.running:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await self.server.handle_request(request)
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = self.server.error_response(f"Invalid JSON: {e}")
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                error_response = self.server.error_response(f"Transport error: {e}")
                print(json.dumps(error_response))
                sys.stdout.flush()
    
    def stop(self):
        """Stop the transport"""
        self.running = False

class MCPHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP requests"""
    
    def __init__(self, *args, server_instance=None, **kwargs):
        self.mcp_server = server_instance
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request = json.loads(post_data.decode('utf-8'))
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                self.mcp_server.handle_request(request)
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_http_server(config: Config):
    """Run MCP server over HTTP"""
    server = MCPServer(config)
    
    def handler(*args, **kwargs):
        MCPHTTPHandler(*args, server_instance=server, **kwargs)
    
    httpd = HTTPServer((config.MCP_SERVER_HOST, config.MCP_SERVER_PORT), handler)
    print(f"MCP Flight Server running on http://{config.MCP_SERVER_HOST}:{config.MCP_SERVER_PORT}")
    httpd.serve_forever()

async def main():
    """Main entry point"""
    config = Config.from_env()
    if len(sys.argv) > 1 and sys.argv[1] == '--http':
        port = int(sys.argv[2]) if len(sys.argv) > 2 else config.MCP_SERVER_PORT
        threading.Thread(target=run_http_server, args=(config,), daemon=True).start()
        while True:
            await asyncio.sleep(3600)
    else:
        server = MCPServer(config)
        transport = MCPTransport(server)
        await transport.start()

if __name__ == "__main__":
    asyncio.run(main())