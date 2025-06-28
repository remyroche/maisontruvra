/**
 * @file /js/api-client.js
 * @description Backward compatibility bridge for API client imports
 * @deprecated Use './services/api.js' instead
 */

// Re-export from the new services directory
export { apiClient, adminApiClient } from './services/api.js';

// Default export for backward compatibility
export { apiClient as default } from './services/api.js';