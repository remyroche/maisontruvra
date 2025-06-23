
/**
 * Common utilities for admin pages
 */

// Check if admin is authenticated
export function checkAdminAuth() {
    const token = localStorage.getItem('admin_token');
    if (!token) {
        window.location.href = '/admin/admin_login.html';
        return false;
    }
    return true;
}

// Load admin header
export function loadAdminHeader() {
    fetch('/admin/admin_header.html')
        .then(response => response.text())
        .then(html => {
            const headerContainer = document.getElementById('admin-header');
            if (headerContainer) {
                headerContainer.innerHTML = html;
            }
        })
        .catch(error => {
            console.error('Error loading admin header:', error);
        });
}

// Common API helper for admin calls
export async function adminApiCall(endpoint, options = {}) {
    const token = localStorage.getItem('admin_token');
    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers
    };

    // Add CSRF token for non-GET requests
    if (options.method && options.method !== 'GET') {
        const csrfToken = getCookie('csrf_token');
        if (csrfToken) {
            headers['X-CSRF-Token'] = csrfToken;
        }
    }

    const response = await fetch(`/api/admin${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401) {
        localStorage.removeItem('admin_token');
        window.location.href = '/admin/admin_login.html';
        return null;
    }

    return response;
}

// Helper to get cookie value
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}
