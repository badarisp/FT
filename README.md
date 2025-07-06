Flight Tracker
A real-time flight tracking application using the OpenSky Network API to fetch and display flight data. It features a Python backend with a Model Context Protocol (MCP) server and a React frontend for visualization. Supports tracking flights by geographic area, continuous tracking capabilities.
Features

Real-time flight tracking in a specified geographic area or by aircraft identifier.
Browser geolocation support to track flights near the user's location.
Interactive React frontend with Tailwind CSS and Lucide icons.
MCP server for integration with Claude or other MCP-compatible systems.
Configurable via environment variables and Docker deployment.
Respects OpenSky API rate limits with configurable intervals.

Project Structure
flight-tracker/
├── backend/
│   ├── flight_data_service.py
│   ├── mcp_flight_server.py
│   ├── config.py
│   ├── requirements.txt
│   ├── .env.example
│   └── setup.sh
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── FlightTracker.jsx
│   │   ├── App.js
│   │   ├── api.js
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── Dockerfile
├── .gitignore
├── LICENSE
└── README.md

Prerequisites

Python 3.11+
Node.js 18+
Docker (optional, for containerized deployment)
OpenSky Network account (optional, for higher API rate limits)

Setup Instructions
Local Development

Clone the Repository
git clone https://github.com/your-username/flight-tracker.git
cd flight-tracker


Backend Setup
cd backend
./setup.sh


Edit backend/.env to add your OpenSky API credentials (optional).
Start the MCP server:source venv/bin/activate
python mcp_flight_server.py --http 8080




Frontend Setup
cd frontend
npm install
npm start


The frontend will be available at http://localhost:3000.


Access the Application

Open http://localhost:3000 in your browser.
Set location, radius, and tracking interval via the interface.



Docker Deployment

Build and Run
docker-compose up -d


Configure .env with OpenSky credentials (optional).
Backend: http://localhost:8080
Frontend: http://localhost:3000


Stop the Application
docker-compose down



Configuration

Environment Variables: Copy backend/.env.example to backend/.env and add OpenSky credentials.
OpenSky API: Register at OpenSky Network for credentials.
MCP Server: Configure via backend/config.py or environment variables (MCP_SERVER_HOST, MCP_SERVER_PORT).

Usage

Track Flights by Area: Set latitude, longitude, and radius.
Search by ICAO24: Enter an ICAO24 code for specific flight details.
Filter by Country: View flights by origin country.
Continuous Tracking: Enable with a 5-30 second interval.
Geolocation: Use browser geolocation for local flight tracking.

API Endpoints
The MCP server exposes JSON-RPC tools:

get_flights_by_area: Fetch flights in a bounding box.
get_flight_by_icao: Get flight by ICAO24 code.
get_flights_by_country: Filter by origin country.
get_all_flights: Retrieve all tracked flights.
search_flights: Search by callsign pattern.
start_continuous_tracking: Start tracking with specified parameters.
stop_tracking: Stop continuous tracking.

Example JSON-RPC request:
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "get_flights_by_area",
    "arguments": {
      "min_lat": 40.0,
      "max_lat": 41.0,
      "min_lon": -75.0,
      "max_lon": -73.0
    }
  }
}

Development

Backend: Python 3.11 with requests and asyncio. Supports stdio and HTTP transports.
Frontend: React 18 with Tailwind CSS, Lucide icons, and axios for API calls.
Testing: Run npm test in frontend/ for React tests. Add backend tests in backend/tests/.

Contributing

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit changes (git commit -m 'Add your feature').
Push to the branch (git push origin feature/your-feature).
Open a pull request.


Acknowledgments

OpenSky Network
React
Tailwind CSS
Lucide
