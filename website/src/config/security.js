// Security configuration for the frontend application
export const securityConfig = {
  // Content Security Policy configuration
  csp: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"], // Note: unsafe-eval needed for Vue dev tools
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'", "ws://localhost:*", "wss://localhost:*"],
    'frame-ancestors': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
    'upgrade-insecure-requests': true,
  },

  // Input validation rules
  validation: {
    email: {
      maxLength: 254,
      pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
    },
    password: {
      minLength: 8,
      maxLength: 128,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecialChars: true,
    },
    name: {
      maxLength: 100,
      pattern: /^[a-zA-ZÀ-ÿ\s'-]+$/,
    },
    phone: {
      pattern: /^[\+]?[1-9][\d]{0,15}$/,
    },
    url: {
      allowedProtocols: ['http:', 'https:'],
      maxLength: 2048,
    },
  },

  // Rate limiting configuration
  rateLimit: {
    login: {
      maxAttempts: 5,
      windowMs: 15 * 60 * 1000, // 15 minutes
    },
    api: {
      maxRequests: 100,
      windowMs: 15 * 60 * 1000, // 15 minutes
    },
    passwordReset: {
      maxAttempts: 3,
      windowMs: 60 * 60 * 1000, // 1 hour
    },
  },

  // Session configuration
  session: {
    maxAge: 24 * 60 * 60 * 1000, // 24 hours
    refreshThreshold: 60 * 60 * 1000, // 1 hour
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'strict',
  },

  // CSRF protection
  csrf: {
    tokenHeader: 'X-CSRF-TOKEN',
    cookieName: 'csrf_token',
    maxAge: 60 * 60 * 1000, // 1 hour
  },

  // XSS protection
  xss: {
    allowedTags: ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
    allowedAttributes: [],
    stripUnsafeTags: true,
  },

  // File upload security
  fileUpload: {
    maxSize: 5 * 1024 * 1024, // 5MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    scanForMalware: true,
  },

  // API security
  api: {
    timeout: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 1000, // 1 second
    validateResponse: true,
  },

  // Logging configuration
  logging: {
    logSecurityEvents: true,
    logFailedAttempts: true,
    logSuspiciousActivity: true,
    maxLogEntries: 1000,
  },

  // Feature flags for security features
  features: {
    twoFactorAuth: true,
    passwordStrengthMeter: true,
    sessionTimeout: true,
    deviceFingerprinting: false, // Disabled for privacy
    auditLogging: true,
    realTimeMonitoring: false, // Disabled for performance
  },
};

// Security headers configuration
export const securityHeaders = {
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), interest-cohort=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
};

// Content Security Policy string
export const cspString = Object.entries(securityConfig.csp)
  .map(([directive, sources]) => {
    if (typeof sources === 'boolean') {
      return sources ? directive : '';
    }
    return `${directive} ${sources.join(' ')}`;
  })
  .filter(Boolean)
  .join('; ');

// Security event types
export const securityEvents = {
  LOGIN_SUCCESS: 'login_success',
  LOGIN_FAILED: 'login_failed',
  LOGOUT: 'logout',
  PASSWORD_CHANGE: 'password_change',
  PROFILE_UPDATE: 'profile_update',
  SUSPICIOUS_ACTIVITY: 'suspicious_activity',
  RATE_LIMIT_EXCEEDED: 'rate_limit_exceeded',
  CSRF_VIOLATION: 'csrf_violation',
  XSS_ATTEMPT: 'xss_attempt',
  INVALID_INPUT: 'invalid_input',
};

// Security levels
export const securityLevels = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
};

export default securityConfig;