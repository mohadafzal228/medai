import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Request interceptor - Add JWT token to headers
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor - Handle errors globally
api.interceptors.response.use(
    (response) => {
        // Return successful responses as-is
        return response;
    },
    (error) => {
        // Handle different error scenarios
        if (error.response) {
            // Server responded with error status
            const status = error.response.status;

            if (status === 401) {
                // Unauthorized - token expired or invalid
                console.error('Unauthorized: Redirecting to login');
                localStorage.removeItem('token');
                window.location.href = '/login';
            } else if (status === 500) {
                console.error('Server error:', error.response.data.detail);
            }

            // Re-throw with error details for component-level handling
            return Promise.reject(error);
        } else if (error.request) {
            // Request made but no response received (network error)
            console.error('Network error: Cannot reach server');
            return Promise.reject(new Error('Cannot connect to server. Please check your connection.'));
        } else {
            // Something else happened
            console.error('Error:', error.message);
            return Promise.reject(error);
        }
    }
);

export default api;
