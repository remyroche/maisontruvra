/**
 * This file contains consolidated UI-related utility functions for the public-facing website.
 * It merges the previous ui.js and common/ui.js files.
 */

/**
 * Displays a toast notification message.
 * @param {string} message The message to display.
 * @param {string} type 'success', 'error', or 'info'.
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        console.error('Toast container not found!');
        return;
    }

    const toast = document.createElement('div');
    let bgColor, textColor;

    switch (type) {
        case 'success':
            bgColor = 'bg-green-500';
            textColor = 'text-white';
            break;
        case 'error':
            bgColor = 'bg-red-500';
            textColor = 'text-white';
            break;
        default:
            bgColor = 'bg-gray-800';
            textColor = 'text-white';
            break;
    }

    toast.className = `p-4 rounded-md shadow-lg ${bgColor} ${textColor} transition-transform transform translate-y-20 opacity-0`;
    toast.textContent = message;

    toastContainer.appendChild(toast);

    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-y-20', 'opacity-0');
    }, 10);

    // Animate out and remove
    setTimeout(() => {
        toast.classList.add('opacity-0');
        toast.addEventListener('transitionend', () => {
            toast.remove();
        });
    }, 3000);
}


/**
 * Initializes and handles the mobile menu toggle.
 */
function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
}

/**
 * Initializes all dropdown menus on the page.
 */
function initializeDropdowns() {
    const dropdownToggles = document.querySelectorAll('[data-dropdown-toggle]');
    
    dropdownToggles.forEach(toggle => {
        const dropdownMenu = document.getElementById(toggle.getAttribute('data-dropdown-toggle'));
        if(dropdownMenu) {
            toggle.addEventListener('click', (event) => {
                event.stopPropagation();
                dropdownMenu.classList.toggle('hidden');
            });
        }
    });

    // Hide dropdown when clicking outside
    window.addEventListener('click', (event) => {
        dropdownToggles.forEach(toggle => {
            const dropdownMenu = document.getElementById(toggle.getAttribute('data-dropdown-toggle'));
            if(dropdownMenu && !dropdownMenu.classList.contains('hidden') && !toggle.contains(event.target)) {
                 dropdownMenu.classList.add('hidden');
            }
        });
    });
}

/**
 * Updates the cart count displayed in the header.
 * Fetches the count from the cart service.
 */
async function updateCartCount() {
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        try {
            const cart = await CartService.getCart(); // Assumes CartService is available
            const count = cart.items.reduce((sum, item) => sum + item.quantity, 0);
            cartCountElement.textContent = count;
            cartCountElement.classList.toggle('hidden', count === 0);
        } catch (error) {
            console.error("Failed to update cart count:", error);
            // Don't show a toast for this, as it's a background task.
        }
    }
}


// Run initializers when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    initializeMobileMenu();
    initializeDropdowns();
    updateCartCount();
