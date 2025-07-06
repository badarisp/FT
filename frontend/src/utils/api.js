const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

export const fetchFlights = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/flights`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching flight data:', error);
        throw error;
    }
};