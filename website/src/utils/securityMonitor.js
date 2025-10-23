// Security monitoring and event logging utility
import { securityEvents, securityLevels } from '@/config/security.js';
import { safeStorage } from './secureStorage.js';

class SecurityMonitor {
  constructor() {
    this.events = [];
    this.maxEvents = 1000;
    this.rateLimitMap = new Map();
    this.suspiciousPatterns = [
      /<script/i,
      /javascript:/i,
      /on\w+\s*=/i,
      /<iframe/i,
      /<object/i,
      /<embed/i,
      /expression\s*\(/i,
      /url\s*\(/i,
      /@import/i,
      /eval\s*\(/i,
      /function\s*\(/i,
    ];
  }

  /**
   * Log a security event
   * @param {string} eventType - Type of security event
   * @param {object} details - Event details
   * @param {string} level - Security level
   */
  logEvent(eventType, details = {}, level = securityLevels.MEDIUM) {
    const event = {
      id: this.generateEventId(),
      timestamp: new Date().toISOString(),
      type: eventType,
      level,
      details,
      userAgent: navigator.userAgent,
      url: window.location.href,
      ip: this.getClientIP(),
    };

    this.events.unshift(event);
    
    // Keep only the most recent events
    if (this.events.length > this.maxEvents) {
      this.events = this.events.slice(0, this.maxEvents);
    }

    // Store in secure storage
    this.persistEvents();

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log('Security Event:', event);
    }

    // Send to server in production
    if (process.env.NODE_ENV === 'production') {
      this.sendEventToServer(event);
    }
  }

  /**
   * Check for suspicious activity
   * @param {string} input - Input to check
   * @param {string} context - Context of the input
   * @returns {boolean} - True if suspicious
   */
  checkSuspiciousActivity(input, context = '') {
    if (!input || typeof input !== 'string') return false;

    const isSuspicious = this.suspiciousPatterns.some(pattern => pattern.test(input));
    
    if (isSuspicious) {
      this.logEvent(securityEvents.SUSPICIOUS_ACTIVITY, {
        input: input.substring(0, 100), // Truncate for privacy
        context,
        pattern: 'XSS_ATTEMPT',
      }, securityLevels.HIGH);
    }

    return isSuspicious;
  }

  /**
   * Check rate limiting
   * @param {string} key - Rate limit key
   * @param {number} maxAttempts - Maximum attempts allowed
   * @param {number} windowMs - Time window in milliseconds
   * @returns {boolean} - True if rate limit exceeded
   */
  checkRateLimit(key, maxAttempts, windowMs) {
    const now = Date.now();
    const windowStart = now - windowMs;
    
    if (!this.rateLimitMap.has(key)) {
      this.rateLimitMap.set(key, []);
    }
    
    const attempts = this.rateLimitMap.get(key);
    
    // Remove old attempts
    const recentAttempts = attempts.filter(timestamp => timestamp > windowStart);
    this.rateLimitMap.set(key, recentAttempts);
    
    if (recentAttempts.length >= maxAttempts) {
      this.logEvent(securityEvents.RATE_LIMIT_EXCEEDED, {
        key,
        attempts: recentAttempts.length,
        maxAttempts,
        windowMs,
      }, securityLevels.HIGH);
      
      return true;
    }
    
    // Record this attempt
    recentAttempts.push(now);
    this.rateLimitMap.set(key, recentAttempts);
    
    return false;
  }

  /**
   * Monitor failed login attempts
   * @param {string} email - Email address
   * @param {string} reason - Failure reason
   */
  monitorFailedLogin(email, reason) {
    const key = `login_${email}`;
    const isRateLimited = this.checkRateLimit(key, 5, 15 * 60 * 1000); // 5 attempts in 15 minutes
    
    this.logEvent(securityEvents.LOGIN_FAILED, {
      email: email.substring(0, 3) + '***', // Mask email for privacy
      reason,
      isRateLimited,
    }, isRateLimited ? securityLevels.HIGH : securityLevels.MEDIUM);
    
    return isRateLimited;
  }

  /**
   * Monitor successful login
   * @param {string} email - Email address
   * @param {object} userInfo - User information
   */
  monitorSuccessfulLogin(email, userInfo = {}) {
    this.logEvent(securityEvents.LOGIN_SUCCESS, {
      email: email.substring(0, 3) + '***', // Mask email for privacy
      userId: userInfo.id,
      isB2B: userInfo.is_b2b,
    }, securityLevels.LOW);
  }

  /**
   * Monitor logout
   * @param {string} userId - User ID
   */
  monitorLogout(userId) {
    this.logEvent(securityEvents.LOGOUT, {
      userId,
    }, securityLevels.LOW);
  }

  /**
   * Monitor password change
   * @param {string} userId - User ID
   */
  monitorPasswordChange(userId) {
    this.logEvent(securityEvents.PASSWORD_CHANGE, {
      userId,
    }, securityLevels.MEDIUM);
  }

  /**
   * Monitor profile updates
   * @param {string} userId - User ID
   * @param {object} changes - Changes made
   */
  monitorProfileUpdate(userId, changes) {
    this.logEvent(securityEvents.PROFILE_UPDATE, {
      userId,
      changes: Object.keys(changes),
    }, securityLevels.LOW);
  }

  /**
   * Monitor CSRF violations
   * @param {string} endpoint - API endpoint
   * @param {string} reason - Violation reason
   */
  monitorCSRFViolation(endpoint, reason) {
    this.logEvent(securityEvents.CSRF_VIOLATION, {
      endpoint,
      reason,
    }, securityLevels.HIGH);
  }

  /**
   * Monitor invalid input
   * @param {string} field - Field name
   * @param {string} value - Input value
   * @param {string} reason - Validation reason
   */
  monitorInvalidInput(field, value, reason) {
    this.logEvent(securityEvents.INVALID_INPUT, {
      field,
      value: value.substring(0, 50), // Truncate for privacy
      reason,
    }, securityLevels.MEDIUM);
  }

  /**
   * Get security events
   * @param {number} limit - Maximum number of events to return
   * @returns {Array} - Array of security events
   */
  getEvents(limit = 100) {
    return this.events.slice(0, limit);
  }

  /**
   * Clear old events
   * @param {number} maxAge - Maximum age in milliseconds
   */
  clearOldEvents(maxAge = 7 * 24 * 60 * 60 * 1000) { // 7 days
    const cutoff = Date.now() - maxAge;
    this.events = this.events.filter(event => 
      new Date(event.timestamp).getTime() > cutoff
    );
    this.persistEvents();
  }

  /**
   * Generate unique event ID
   * @returns {string} - Event ID
   */
  generateEventId() {
    return `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Get client IP (simplified)
   * @returns {string} - Client IP or 'unknown'
   */
  getClientIP() {
    // In a real application, this would be provided by the server
    return 'unknown';
  }

  /**
   * Persist events to secure storage
   */
  persistEvents() {
    try {
      safeStorage.setItem('security_events', this.events, { expires: 7 * 24 * 60 * 60 * 1000 }); // 7 days
    } catch (error) {
      console.error('Failed to persist security events:', error);
    }
  }

  /**
   * Load events from secure storage
   */
  loadEvents() {
    try {
      const stored = safeStorage.getItem('security_events');
      if (stored && Array.isArray(stored)) {
        this.events = stored;
      }
    } catch (error) {
      console.error('Failed to load security events:', error);
    }
  }

  /**
   * Send event to server
   * @param {object} event - Security event
   */
  async sendEventToServer(event) {
    try {
      // This would send the event to your backend security monitoring system
      // await fetch('/api/security/events', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify(event)
      // });
    } catch (error) {
      console.error('Failed to send security event to server:', error);
    }
  }
}

// Create singleton instance
const securityMonitor = new SecurityMonitor();

// Load events on initialization
securityMonitor.loadEvents();

export default securityMonitor;