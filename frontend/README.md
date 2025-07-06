# Flight Tracker Application - Frontend

This is the frontend part of the Flight Tracker application, built using React. It communicates with the backend to fetch and display flight data.

## Project Structure

- `src/`: Contains the source code for the React application.
  - `components/`: Contains reusable components.
    - `FlightTracker.jsx`: Main component for rendering flight data.
  - `pages/`: Contains different pages of the application.
    - `Home.js`: Home page of the application.
  - `utils/`: Contains utility functions.
    - `api.js`: API client for communicating with the backend.
  - `App.js`: Entry point for the React application.
  - `index.js`: Renders the App component into the DOM.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   ```

2. Navigate to the frontend directory:
   ```
   cd flight-tracker-app/frontend
   ```

3. Install dependencies:
   ```
   npm install
   ```

## Running the Application

To start the development server, run:
```
npm start
```

The application will be available at `http://localhost:3000`.

## Build

To create a production build, run:
```
npm run build
```

This will generate a `build` directory with the production-ready files.

## Contributing

Feel free to submit issues or pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.