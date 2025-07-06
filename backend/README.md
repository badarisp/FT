# Flight Tracker Backend

This is the backend service for the Flight Tracker application. It handles core flight data operations and communicates with the OpenSky API to fetch flight information.

## Project Structure

- **src/**: Contains the source code for the backend application.
  - **app.js**: Main application file.
  - **controllers/**: Contains controller files for handling requests.
  - **models/**: Contains model files for data structures.
  - **routes/**: Contains route definitions for the API.
  - **utils/**: Contains utility functions and database connection logic.

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flight-tracker-app/backend
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on the `.env.example` file and fill in the required environment variables.

4. Run the application:
   ```
   python app.py
   ```

## API Endpoints

- **GET /flights**: Retrieve a list of flights.
- **GET /flights/:id**: Retrieve details of a specific flight.

## License

This project is licensed under the MIT License. See the LICENSE file for details.