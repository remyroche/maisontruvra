// File: website/source/admin/js/admin_common.js

import { checkAdminLogin, logout } from './admin_auth.js';

/**
 * Fetches the admin header, injects it into the placeholder,
 * and then attaches necessary event listeners.
 */
async function loadAndSetupHeader() {
    try {
        const response = await fetch('/admin/admin_header.html'); // Path is relative to the 'source' root
        if (!response.ok) {
            throw new Error(`Failed to load header: ${response.statusText}`);
        }
        
        const headerHtml = await response.text();
        const placeholder = document.getElementById('admin-header-placeholder');
        
        if (placeholder) {
            placeholder.innerHTML = headerHtml;

            // The header is now in the DOM, so we can safely find and attach events
            const logoutButton = document.getElementById('admin-logout-btn');
            if (logoutButton) {
                logoutButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    logout();
                });
            }

            // Highlight the active navigation link
            const currentPage = window.location.pathname.split('/').pop();
            const navLinks = placeholder.querySelectorAll('.nav-link');
            navLinks.forEach(link => {
                if (link.getAttribute('href').endsWith(currentPage)) {
                    link.classList.add('active');
                }
            });
        }
    } catch (error) {
        console.error('Error loading admin header:', error);
    }
}

/**
 * A generic initializer for all admin pages. It ensures the user is logged in,
 * loads the header, and then runs any page-specific logic.
 * @param {Function} [pageSpecificInit] - An optional function to run for page-specific setup.
 */
export function initializeAdminPage(pageSpecificInit) {
    document.addEventListener('DOMContentLoaded', async () => {
        const isLoggedIn = await checkAdminLogin();
        if (isLoggedIn) {
            await loadAndSetupHeader();
            if (pageSpecificInit && typeof pageSpecificInit === 'function') {
                pageSpecificInit();
            }
        }
        // If not logged in, checkAdminLogin() will handle the redirect.
    });
}
