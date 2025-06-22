/**
 * pro_common.js
 *
 * This script contains common functionalities shared across the professional (B2B) pages of Maison Trüvra.
 * It handles tasks such as loading common UI components (header/footer), managing the user session,
 * and providing utility functions needed throughout the professional section.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Load header and footer for professional pages
    loadProHeaderAndFooter();

    // Check user authentication status and update UI accordingly
    updateUserSessionDisplay();
});

/**
 * Loads the professional header and footer into their respective placeholders.
 * This ensures a consistent structure across all B2B pages.
 */
async function loadProHeaderAndFooter() {
    try {
        const headerPlaceholder = document.getElementById('pro-header-placeholder');
        const footerPlaceholder = document.getElementById('pro-footer-placeholder');

        if (headerPlaceholder) {
            const response = await fetch('pro_header.html');
            if (!response.ok) throw new Error('Failed to load professional header.');
            headerPlaceholder.innerHTML = await response.text();
        }

        if (footerPlaceholder) {
            const response = await fetch('pro_footer.html');
            if (!response.ok) throw new Error('Failed to load professional footer.');
            footerPlaceholder.innerHTML = await response.text();
        }
    } catch (error) {
        console.error('Error loading professional layout:', error);
        // Optionally display an error message to the user
    }
}

/**
 * Checks for professional user session and updates the UI.
 * This function can be expanded to display user name, account links, etc.
 */
function updateUserSessionDisplay() {
    const proUserToken = sessionStorage.getItem('proUserToken');
    const userDisplayElement = document.getElementById('pro-user-display'); // Assuming this ID exists in the header

    if (proUserToken && userDisplayElement) {
        // In a real application, you would decode the token or fetch user data
        // For this example, we'll just show a generic message.
        const professionalUser = JSON.parse(sessionStorage.getItem('professionalUser'));
        if (professionalUser) {
            userDisplayElement.textContent = `Welcome, ${professionalUser.company_name}`;
        }
    } else {
        // Handle UI for logged-out users if necessary
    }
}

/**
 * Logs out the professional user by clearing session storage and redirecting.
 */


async function proLogout() {
    try {
        // The API endpoint for B2B logout is at /api/b2b/logout
        await fetchProAPI('/logout', { method: 'POST' }); 
    } catch (error) {
        console.error('B2B logout failed:', error);
    } finally {
        // Always redirect to the login page after attempting to log out
        window.location.href = '/pro/professionnels.html';
    }
}


document.addEventListener('DOMContentLoaded', () => {
    // Inject the header
    const headerPlaceholder = document.querySelector('pro-header-placeholder');
    if (headerPlaceholder) {
        fetch('/pro/pro_header.html')
            .then(res => res.text())
            .then(data => {
                headerPlaceholder.innerHTML = data;
                // --- START NEW CODE ---
                // Add logout functionality after header is loaded
                const logoutLink = document.getElementById('b2b-logout-link');
                if (logoutLink) {
                    logoutLink.addEventListener('click', e => {
                        e.preventDefault();
                        proLogout();
                    });
                }
                // --- END NEW CODE ---
            });
    }
});
