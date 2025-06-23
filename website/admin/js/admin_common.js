// admin_common.js - Common utilities for admin pages

import { ApiClient } from '../../js/common/api_helper.js';

// Initialize CSRF token globally for all admin pages
let csrfToken = null;

// Get CSRF token from backend
async function initializeCSRF() {
  try {
    const response = await fetch('/api/csrf/token', {
      method: 'GET',
      credentials: 'include'
    });

    if (response.ok) {
      const data = await response.json();
      csrfToken = data.csrf_token;

      // Store in meta tag for other scripts
      let metaTag = document.querySelector('meta[name="csrf-token"]');
      if (!metaTag) {
        metaTag = document.createElement('meta');
        metaTag.name = 'csrf-token';
        document.head.appendChild(metaTag);
      }
      metaTag.content = csrfToken;
    }
  } catch (error) {
    console.error('Failed to initialize CSRF token:', error);
  }
}

// Get CSRF token
function getCSRFToken() {
  return csrfToken || document.querySelector('meta[name="csrf-token"]')?.content;
}

// Enhanced API client for admin with CSRF
const adminApiClient = new ApiClient('/admin/api');

// Common admin page initialization
async function setupAdminPage() {
  await initializeCSRF();

  // Setup logout handler
  const logoutBtn = document.getElementById('admin-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }

  // Setup session timeout warning
  setupSessionTimeout();
}

// Alias for backward compatibility
const initializeAdminPage = setupAdminPage;

async function handleLogout() {
  try {
    const response = await adminApiClient.post('/auth/logout', {}, {
      'X-CSRF-Token': getCSRFToken()
    });

    if (response.status === 'success') {
      window.location.href = '/admin/login';
    }
  } catch (error) {
    console.error('Logout failed:', error);
    // Force redirect anyway
    window.location.href = '/admin/login';
  }
}

function setupSessionTimeout() {
  let timeoutWarning;
  let sessionTimeout;

  function resetTimers() {
    clearTimeout(timeoutWarning);
    clearTimeout(sessionTimeout);

    // Warn 5 minutes before timeout
    timeoutWarning = setTimeout(() => {
      if (confirm('Your session will expire in 5 minutes. Click OK to extend.')) {
        // Make a simple request to extend session
        fetch('/admin/api/auth/ping', {
          method: 'POST',
          credentials: 'include',
          headers: {
            'X-CSRF-Token': getCSRFToken()
          }
        });
      }
    }, 25 * 60 * 1000); // 25 minutes

    // Force logout after 30 minutes
    sessionTimeout = setTimeout(() => {
      alert('Session expired. You will be redirected to login.');
      window.location.href = '/admin/login';
    }, 30 * 60 * 1000);
  }

  // Reset timers on user activity
  ['click', 'keypress', 'scroll', 'mousemove'].forEach(event => {
    document.addEventListener(event, resetTimers, true);
  });

  resetTimers();
}

// Check admin authentication
async function checkAdminAuth() {
  const token = localStorage.getItem('admin_token');
  if (!token) {
    window.location.href = '/admin/login';
    return false;
  }
  return true;
}

// Load admin header
async function loadAdminHeader() {
  // Implementation for loading admin header
  console.log('Admin header loaded');
}

export { adminApiClient, getCSRFToken, setupAdminPage, initializeAdminPage, checkAdminAuth, loadAdminHeader };