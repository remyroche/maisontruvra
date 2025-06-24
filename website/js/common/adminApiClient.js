/*
 * FILENAME: website/js/common/adminApiClient.js
 * DESCRIPTION: Centralized API client for all Admin Portal requests.
 *
 * This client standardizes API calls from the admin frontend. It automatically
 * handles fetching and attaching the CSRF token to secure requests (POST, PUT, DELETE),
 * which is a critical security measure against Cross-Site Request Forgery.
 * It also standardizes error handling.
 */
import axios from 'axios';

// Create an Axios instance with default settings for the admin API
const adminApiClient = axios.create({
  baseURL: '/api/admin', // Base path for all admin API endpoints
});

// --- Security: CSRF Token Handling ---
// Before making a state-changing request, we must fetch a CSRF token.
async function getCsrfToken() {
  try {
    const response = await axios.get('/api/auth/csrf-token');
    return response.data.csrf_token;
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
    throw new Error('Could not initialize secure session.');
  }
}

// Interceptor to attach the CSRF token to secure requests
adminApiClient.interceptors.request.use(async (config) => {
  const secureMethods = ['post', 'put', 'delete', 'patch'];
  if (secureMethods.includes(config.method.toLowerCase())) {
    const csrfToken = await getCsrfToken();
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default adminApiClient;
