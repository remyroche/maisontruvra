/**
 * @file security.js
 * @description A collection of frontend security utility functions.
 * This module provides functions to help mitigate common web vulnerabilities
 * such as Cross-Site Scripting (XSS), insecure redirects, and provides
 * mechanisms for implementing a Content Security Policy (CSP).
 *
 * To use this module, you'll need to install DOMPurify:
 * npm install dompurify
 */

import DOMPurify from 'dompurify';

/**
 * =============================================================================
 * --- Input Sanitization (XSS Prevention) ---
 * =============================================================================
 */

/**
 * Sanitizes a string of HTML content to prevent Cross-Site Scripting (XSS) attacks.
 * It uses DOMPurify to remove any potentially malicious code. This should be used
 * whenever you need to render user-provided content as HTML (e.g., with v-html in Vue).
 *
 * @param {string} dirtyHTML The potentially unsafe HTML string.
 * @returns {string} The sanitized, safe HTML string.
 *
 * @example
 * // In a Vue component:
 * // import { sanitizeHTML } from '@/js/utils/security.js';
 * // this.safeContent = sanitizeHTML(this.userGeneratedContent);
 * // <div v-html="safeContent"></div>
 */
export function sanitizeHTML(dirtyHTML) {
  if (typeof dirtyHTML !== 'string') {
    console.warn('sanitizeHTML expected a string but received', typeof dirtyHTML);
    return '';
  }
  return DOMPurify.sanitize(dirtyHTML, {
    USE_PROFILES: { html: true }, // Allow standard HTML tags
    FORBID_TAGS: ['style', 'script'], // Explicitly forbid style and script tags
    FORBID_ATTR: ['onerror', 'onload', 'on...'], // Forbid dangerous event handlers
  });
}

/**
 * =============================================================================
 * --- Content Security Policy (CSP) ---
 * =============================================================================
 */

/**
 * Dynamically generates and applies a Content Security Policy (CSP) by adding
 * or updating a <meta> tag in the document's <head>. A strong CSP is a critical
 * defense-in-depth measure against XSS and data injection attacks.
 *
 * Note: While setting CSP via a meta tag is good, setting it via an HTTP header
 * from the backend is the preferred and more robust method.
 *
 * @param {object} options - An object to configure the CSP directives.
 * @param {string[]} [options.defaultSrc=["'self'"]] - Default source for content.
 * @param {string[]} [options.scriptSrc=["'self'"]] - Allowed sources for scripts.
 * @param {string[]} [options.styleSrc=["'self'", "'unsafe-inline'"]] - Allowed sources for styles.
 * @param {string[]} [options.imgSrc=["'self'", "data:"]] - Allowed sources for images.
 * @param {string[]} [options.connectSrc=["'self'"]] - Allowed backend domains for API calls.
 * @param {string[]} [options.fontSrc=["'self'"]] - Allowed sources for fonts.
 * @param {string} [options.reportUri] - A URL to send CSP violation reports to.
 *
 * @example
 * // In your main.js or App.vue
 * // import { generateCSP } from '@/js/utils/security.js';
 * // generateCSP({
 * //   connectSrc: ["'self'", "https://api.example.com"],
 * //   imgSrc: ["'self'", "data:", "https://images.example.com"],
 * //   reportUri: '/csp-violations'
 * // });
 */
export function generateCSP(options = {}) {
  const policy = {
    'default-src': options.defaultSrc || ["'self'"],
    'script-src': options.scriptSrc || ["'self'"],
    'style-src': options.styleSrc || ["'self'", "'unsafe-inline'"], // 'unsafe-inline' is often needed for Vue styles.
    'img-src': options.imgSrc || ["'self'", "data:"],
    'connect-src': options.connectSrc || ["'self'"],
    'font-src': options.fontSrc || ["'self'"],
    'object-src': ["'none'"], // Disallow plugins like Flash.
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"], // Prevent clickjacking.
    'upgrade-insecure-requests': [],
    ...options, // Allow overriding defaults
  };

  const cspString = Object.entries(policy)
    .map(([directive, sources]) => {
      if (sources.length === 0) {
        return directive;
      }
      return `${directive} ${sources.join(' ')}`;
    })
    .join('; ');

  let cspTag = document.querySelector("meta[http-equiv='Content-Security-Policy']");
  if (!cspTag) {
    cspTag = document.createElement('meta');
    cspTag.setAttribute('http-equiv', 'Content-Security-Policy');
    document.head.appendChild(cspTag);
  }
  cspTag.setAttribute('content', cspString);
  console.log('CSP has been applied.');
}

/**
 * =============================================================================
 * --- Secure Navigation & Redirects ---
 * =============================================================================
 */

/**
 * Validates a URL to ensure it is a safe, same-origin redirect target.
 * This helps prevent Open Redirect vulnerabilities, where an attacker could
 * redirect users from your site to a malicious one.
 *
 * @param {string} url - The URL to validate.
 * @returns {boolean} - True if the URL is a safe, relative path. False otherwise.
 *
 * @example
 * // const redirectUrl = new URLSearchParams(window.location.search).get('redirect');
 * // if (validateRedirectUrl(redirectUrl)) {
 * //   router.push(redirectUrl);
 * // } else {
 * //   router.push('/'); // Fallback to a safe default
 * // }
 */
export function validateRedirectUrl(url) {
  if (!url || typeof url !== 'string') {
    return false;
  }
  // A safe redirect URL should start with a single '/' and not contain '//' or '..'.
  // It should also not start with a protocol like 'http:' or 'javascript:'.
  return url.startsWith('/') && !url.includes('//') && !url.includes('..');
}

/**
 * Secures all links within a given DOM element that use `target="_blank"`.
 * It adds `rel="noopener noreferrer"` to prevent the newly opened page from
 * gaining access to the original page's `window` object (tabnapping).
 *
 * @param {HTMLElement} containerElement - The DOM element to scan for insecure links.
 *
 * @example
 * // In a Vue component's mounted hook, after rendering user content:
 * // secureTargetBlank(this.$refs.contentContainer);
 */
export function secureTargetBlank(containerElement) {
  if (!containerElement || typeof containerElement.querySelectorAll !== 'function') {
    return;
  }
  const links = containerElement.querySelectorAll('a[target="_blank"]');
  links.forEach(link => {
    link.setAttribute('rel', 'noopener noreferrer');
  });
}


/**
 * =============================================================================
 * --- Secure Token & Data Storage ---
 * =============================================================================
 *
 * It is critical to NEVER store sensitive information, such as JWTs (JSON Web Tokens),
 * API keys, or personal user data in localStorage. localStorage is accessible via
 * JavaScript, making it vulnerable to XSS attacks. If an attacker can inject
- * a script, they can read the entire contents of localStorage.
 *
 * BEST PRACTICE:
 * 1.  **JWTs**: Should be stored in `HttpOnly` cookies. These cookies are sent
 * with every HTTP request to the server but are inaccessible to client-side
 * JavaScript, providing a strong defense against token theft via XSS.
 * The backend is responsible for setting this cookie upon login.
 * 2.  **CSRF Tokens**: Should be handled by the API client. The backend sends a
 * CSRF token, and the client-side code includes it in a header (e.g.,
 * `X-CSRF-Token`) on subsequent state-changing requests.
 *
 * This section does not provide an exportable function, but serves as a documented
 * reminder of best practices.
 */
