// Secure storage utilities with encryption and validation
import { generateSecureToken } from './security.js';

/**
 * Secure storage class that provides encrypted localStorage with validation
 */
class SecureStorage {
  constructor() {
    this.encryptionKey = this.getOrCreateEncryptionKey();
  }

  /**
   * Get or create encryption key for secure storage
   * @returns {string} - Encryption key
   */
  getOrCreateEncryptionKey() {
    let key = localStorage.getItem('_secure_key');
    if (!key) {
      key = generateSecureToken(32);
      localStorage.setItem('_secure_key', key);
    }
    return key;
  }

  /**
   * Simple XOR encryption (for basic obfuscation)
   * @param {string} text - Text to encrypt
   * @param {string} key - Encryption key
   * @returns {string} - Encrypted text
   */
  encrypt(text, key) {
    if (!text || !key) return text;
    
    let result = '';
    for (let i = 0; i < text.length; i++) {
      result += String.fromCharCode(
        text.charCodeAt(i) ^ key.charCodeAt(i % key.length)
      );
    }
    return btoa(result);
  }

  /**
   * Simple XOR decryption
   * @param {string} encryptedText - Encrypted text
   * @param {string} key - Decryption key
   * @returns {string} - Decrypted text
   */
  decrypt(encryptedText, key) {
    if (!encryptedText || !key) return encryptedText;
    
    try {
      const text = atob(encryptedText);
      let result = '';
      for (let i = 0; i < text.length; i++) {
        result += String.fromCharCode(
          text.charCodeAt(i) ^ key.charCodeAt(i % key.length)
        );
      }
      return result;
    } catch (error) {
      console.error('Decryption failed:', error);
      return '';
    }
  }

  /**
   * Set secure item in localStorage
   * @param {string} key - Storage key
   * @param {any} value - Value to store
   * @param {object} options - Storage options
   */
  setItem(key, value, options = {}) {
    try {
      const data = {
        value,
        timestamp: Date.now(),
        expires: options.expires ? Date.now() + options.expires : null,
        version: '1.0'
      };

      const encryptedData = this.encrypt(JSON.stringify(data), this.encryptionKey);
      localStorage.setItem(`_secure_${key}`, encryptedData);
    } catch (error) {
      console.error('Failed to set secure item:', error);
    }
  }

  /**
   * Get secure item from localStorage
   * @param {string} key - Storage key
   * @returns {any} - Stored value or null
   */
  getItem(key) {
    try {
      const encryptedData = localStorage.getItem(`_secure_${key}`);
      if (!encryptedData) return null;

      const decryptedData = this.decrypt(encryptedData, this.encryptionKey);
      const data = JSON.parse(decryptedData);

      // Check if data has expired
      if (data.expires && Date.now() > data.expires) {
        this.removeItem(key);
        return null;
      }

      return data.value;
    } catch (error) {
      console.error('Failed to get secure item:', error);
      return null;
    }
  }

  /**
   * Remove secure item from localStorage
   * @param {string} key - Storage key
   */
  removeItem(key) {
    localStorage.removeItem(`_secure_${key}`);
  }

  /**
   * Clear all secure items
   */
  clear() {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith('_secure_')) {
        localStorage.removeItem(key);
      }
    });
  }

  /**
   * Check if secure item exists
   * @param {string} key - Storage key
   * @returns {boolean} - True if item exists
   */
  hasItem(key) {
    return localStorage.getItem(`_secure_${key}`) !== null;
  }

  /**
   * Get all secure keys
   * @returns {string[]} - Array of secure keys
   */
  getKeys() {
    const keys = Object.keys(localStorage);
    return keys
      .filter(key => key.startsWith('_secure_'))
      .map(key => key.replace('_secure_', ''));
  }
}

// Create singleton instance
const secureStorage = new SecureStorage();

/**
 * Secure storage for sensitive data
 */
export const secureStore = {
  /**
   * Store user preferences securely
   * @param {string} key - Preference key
   * @param {any} value - Preference value
   */
  setPreference(key, value) {
    secureStorage.setItem(`pref_${key}`, value, { expires: 365 * 24 * 60 * 60 * 1000 }); // 1 year
  },

  /**
   * Get user preference
   * @param {string} key - Preference key
   * @returns {any} - Preference value
   */
  getPreference(key) {
    return secureStorage.getItem(`pref_${key}`);
  },

  /**
   * Store authentication token securely
   * @param {string} token - Auth token
   */
  setAuthToken(token) {
    secureStorage.setItem('auth_token', token, { expires: 24 * 60 * 60 * 1000 }); // 24 hours
  },

  /**
   * Get authentication token
   * @returns {string|null} - Auth token
   */
  getAuthToken() {
    return secureStorage.getItem('auth_token');
  },

  /**
   * Remove authentication token
   */
  removeAuthToken() {
    secureStorage.removeItem('auth_token');
  },

  /**
   * Store session data securely
   * @param {string} key - Session key
   * @param {any} value - Session value
   */
  setSession(key, value) {
    secureStorage.setItem(`session_${key}`, value, { expires: 60 * 60 * 1000 }); // 1 hour
  },

  /**
   * Get session data
   * @param {string} key - Session key
   * @returns {any} - Session value
   */
  getSession(key) {
    return secureStorage.getItem(`session_${key}`);
  },

  /**
   * Clear all session data
   */
  clearSession() {
    const keys = secureStorage.getKeys();
    keys.forEach(key => {
      if (key.startsWith('session_')) {
        secureStorage.removeItem(key);
      }
    });
  },

  /**
   * Clear all secure data
   */
  clearAll() {
    secureStorage.clear();
  }
};

/**
 * Safe localStorage wrapper with validation
 */
export const safeStorage = {
  /**
   * Set item with validation
   * @param {string} key - Storage key
   * @param {any} value - Value to store
   * @param {object} options - Storage options
   */
  setItem(key, value, options = {}) {
    try {
      // Validate key
      if (!key || typeof key !== 'string') {
        throw new Error('Invalid storage key');
      }

      // Validate value size (limit to 5MB)
      const valueStr = JSON.stringify(value);
      if (valueStr.length > 5 * 1024 * 1024) {
        throw new Error('Value too large for storage');
      }

      const data = {
        value,
        timestamp: Date.now(),
        expires: options.expires ? Date.now() + options.expires : null
      };

      localStorage.setItem(key, JSON.stringify(data));
    } catch (error) {
      console.error('Failed to set storage item:', error);
    }
  },

  /**
   * Get item with validation
   * @param {string} key - Storage key
   * @returns {any} - Stored value or null
   */
  getItem(key) {
    try {
      const dataStr = localStorage.getItem(key);
      if (!dataStr) return null;

      const data = JSON.parse(dataStr);

      // Check if data has expired
      if (data.expires && Date.now() > data.expires) {
        localStorage.removeItem(key);
        return null;
      }

      return data.value;
    } catch (error) {
      console.error('Failed to get storage item:', error);
      return null;
    }
  },

  /**
   * Remove item
   * @param {string} key - Storage key
   */
  removeItem(key) {
    localStorage.removeItem(key);
  },

  /**
   * Clear all items
   */
  clear() {
    localStorage.clear();
  }
};

export default secureStorage;