/**
 * @fileoverview
 * This file provides essential security-related utility functions for the frontend application.
 * It includes functions for sanitizing HTML to prevent XSS attacks and for validating
 * redirect URLs to prevent open redirect vulnerabilities.
 */

import DOMPurify from 'dompurify';

/**
 * A set of allowed domains for redirection. This acts as a whitelist to ensure
 * that users are only redirected to safe and trusted pages.
 * The main application domain is included by default.
 */
const ALLOWED_REDIRECT_DOMAINS = new Set([
  window.location.hostname,
  // Add other trusted subdomains or external domains if necessary
  // e.g., 'help.maisontruvra.com'
]);

/**
 * Sanitizes an HTML string to prevent Cross-Site Scripting (XSS) attacks.
 * It uses DOMPurify to remove any potentially malicious code from the HTML,
 * such as <script> tags or inline event handlers.
 *
 * @param {string} dirtyHtml The potentially unsafe HTML string to sanitize.
 * @returns {string} The sanitized, safe HTML string.
 */
export function sanitizeHTML(dirtyHtml) {
  if (typeof dirtyHtml !== 'string') {
    return '';
  }
  return DOMPurify.sanitize(dirtyHtml);
}

/**
 * Validates a URL to ensure it is a safe and legitimate redirect target.
 * It checks against a whitelist of allowed domains and ensures the URL
 * protocol is either HTTP or HTTPS.
 *
 * @param {string} url The URL to validate.
 * @returns {boolean} True if the URL is valid and safe, false otherwise.
 */
export function validateRedirectUrl(url) {
  if (!url || typeof url !== 'string') {
    return false;
  }

  try {
    const urlObject = new URL(url, window.location.origin);
    
    // Allow relative URLs or URLs from whitelisted domains
    const isAllowedDomain = ALLOWED_REDIRECT_DOMAINS.has(urlObject.hostname);
    const isSafeProtocol = ['https:', 'http:'].includes(urlObject.protocol);

    return isAllowedDomain && isSafeProtocol;
  } catch (e) {
    // Invalid URL format
    return false;
  }
}

/**
 * Retrieves a redirect URL from the current window's query parameters
 * and validates it. If the URL is valid, it returns it; otherwise,
 * it returns a safe fallback URL (the root path).
 * * @param {string} paramName The name of the query parameter containing the redirect URL.
 * @param {string} [fallbackUrl='/'] The default URL to return if validation fails.
 * @returns {string} A validated, safe redirect URL.
 */
export function getValidatedRedirectUrl(paramName, fallbackUrl = '/') {
    const urlParams = new URLSearchParams(window.location.search);
    const redirectUrl = urlParams.get(paramName);

    if (redirectUrl && validateRedirectUrl(redirectUrl)) {
        return redirectUrl;
    }

    return fallbackUrl;
}
