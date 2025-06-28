/**
 * @file /js/services/api.js
 * @description Main API client service - centralized HTTP client configuration
 * Re-exports the API clients from the src directory for consistency
 */

// Re-export API clients from the main services directory
export { apiClient, adminApiClient } from '../../src/services/api.js';

// For backward compatibility with existing imports
export { apiClient as default } from '../../src/services/api.js';