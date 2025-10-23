// Security utilities for input sanitization and validation
import DOMPurify from 'dompurify';

/**
 * Sanitize HTML content to prevent XSS attacks
 * @param {string} html - HTML content to sanitize
 * @returns {string} - Sanitized HTML content
 */
export function sanitizeHtml(html) {
  if (!html || typeof html !== 'string') return '';
  
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    ALLOWED_ATTR: [],
    KEEP_CONTENT: true
  });
}

/**
 * Sanitize plain text input
 * @param {string} text - Text to sanitize
 * @returns {string} - Sanitized text
 */
export function sanitizeText(text) {
  if (!text || typeof text !== 'string') return '';
  
  return text
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim();
}

/**
 * Validate and sanitize email address
 * @param {string} email - Email to validate
 * @returns {object} - { isValid: boolean, sanitized: string, error: string }
 */
export function validateEmail(email) {
  if (!email || typeof email !== 'string') {
    return { isValid: false, sanitized: '', error: 'Email is required' };
  }
  
  const sanitized = email.trim().toLowerCase();
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  
  if (sanitized.length > 254) {
    return { isValid: false, sanitized, error: 'Email is too long' };
  }
  
  if (!emailRegex.test(sanitized)) {
    return { isValid: false, sanitized, error: 'Invalid email format' };
  }
  
  return { isValid: true, sanitized, error: null };
}

/**
 * Validate password strength
 * @param {string} password - Password to validate
 * @returns {object} - { isValid: boolean, score: number, errors: string[] }
 */
export function validatePassword(password) {
  if (!password || typeof password !== 'string') {
    return { isValid: false, score: 0, errors: ['Password is required'] };
  }
  
  const errors = [];
  let score = 0;
  
  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long');
  } else {
    score += 1;
  }
  
  if (password.length > 128) {
    errors.push('Password is too long');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  } else {
    score += 1;
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  } else {
    score += 1;
  }
  
  if (!/\d/.test(password)) {
    errors.push('Password must contain at least one number');
  } else {
    score += 1;
  }
  
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('Password must contain at least one special character');
  } else {
    score += 1;
  }
  
  // Check for common weak patterns
  const commonPasswords = ['password', '123456', 'qwerty', 'abc123', 'password123'];
  if (commonPasswords.some(common => password.toLowerCase().includes(common))) {
    errors.push('Password contains common weak patterns');
  }
  
  return {
    isValid: errors.length === 0,
    score,
    errors
  };
}

/**
 * Sanitize user input for database storage
 * @param {string} input - Input to sanitize
 * @returns {string} - Sanitized input
 */
export function sanitizeInput(input) {
  if (!input || typeof input !== 'string') return '';
  
  return input
    .replace(/[<>]/g, '') // Remove HTML tags
    .replace(/javascript:/gi, '') // Remove javascript protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .replace(/['"]/g, '') // Remove quotes that could break SQL
    .trim();
}

/**
 * Validate and sanitize URL
 * @param {string} url - URL to validate
 * @returns {object} - { isValid: boolean, sanitized: string, error: string }
 */
export function validateUrl(url) {
  if (!url || typeof url !== 'string') {
    return { isValid: false, sanitized: '', error: 'URL is required' };
  }
  
  const sanitized = url.trim();
  
  try {
    const urlObj = new URL(sanitized);
    
    // Only allow http and https protocols
    if (!['http:', 'https:'].includes(urlObj.protocol)) {
      return { isValid: false, sanitized, error: 'Only HTTP and HTTPS URLs are allowed' };
    }
    
    return { isValid: true, sanitized, error: null };
  } catch (error) {
    return { isValid: false, sanitized, error: 'Invalid URL format' };
  }
}

/**
 * Escape HTML entities
 * @param {string} text - Text to escape
 * @returns {string} - Escaped text
 */
export function escapeHtml(text) {
  if (!text || typeof text !== 'string') return '';
  
  const htmlEscapes = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;'
  };
  
  return text.replace(/[&<>"'/]/g, (match) => htmlEscapes[match]);
}

/**
 * Generate a secure random token
 * @param {number} length - Token length (default: 32)
 * @returns {string} - Secure random token
 */
export function generateSecureToken(length = 32) {
  const array = new Uint8Array(length);
  crypto.getRandomValues(array);
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Check if a string contains potentially malicious content
 * @param {string} input - Input to check
 * @returns {boolean} - True if potentially malicious
 */
export function isPotentiallyMalicious(input) {
  if (!input || typeof input !== 'string') return false;
  
  const maliciousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe/i,
    /<object/i,
    /<embed/i,
    /<link/i,
    /<meta/i,
    /<style/i,
    /expression\s*\(/i,
    /url\s*\(/i,
    /@import/i
  ];
  
  return maliciousPatterns.some(pattern => pattern.test(input));
}