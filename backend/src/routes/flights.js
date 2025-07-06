const express = require('express');
const router = express.Router();
const flightsController = require('../controllers/flightsController');

// Route to get all flights
router.get('/', flightsController.getAllFlights);

// Route to get a flight by ID
router.get('/:id', flightsController.getFlightById);

// Route to create a new flight
router.post('/', flightsController.createFlight);

// Route to update a flight by ID
router.put('/:id', flightsController.updateFlight);

// Route to delete a flight by ID
router.delete('/:id', flightsController.deleteFlight);

module.exports = router;