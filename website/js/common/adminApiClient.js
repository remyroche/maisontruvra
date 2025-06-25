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
const apiClient = axios.create({
  baseURL: '/api/admin', 
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
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

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const authStore = useAdminAuthStore();

    if (error.response && error.response.status === 401) {
      // Check if the server is specifically asking for re-authentication
      if (error.response.data?.reason === 'reauth_required') {
        // Don't log out. Instead, trigger the re-auth modal flow.
        authStore.promptForReAuth(error.config);
      } else {
        // For any other 401 error, perform a full logout.
        authStore.logout();
      }
    }
    return Promise.reject(error);
  }
);

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
