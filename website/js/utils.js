// website/source/js/utils.js

/**
 * Formats a number as a currency string.
 * @param {number} amount - The amount to format.
 * @param {string} currency - The currency code (e.g., 'EUR').
 * @returns {string} - The formatted currency string.
 */
export function formatCurrency(amount, currency = 'EUR') {
    return new Intl.NumberFormat('fr-FR', { // Using 'fr-FR' for Euro formatting as an example
        style: 'currency',
        currency: currency,
    }).format(amount);
}

/**
 * Gets a URL parameter by its name.
 * @param {string} name - The name of the parameter.
 * @returns {string|null} - The value of the parameter or null if not found.
 */
export function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? null : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

/**
 * Capitalizes the first letter of a string.
 * @param {string} s The string to capitalize.
 * @returns {string}
 */
export function capitalizeFirstLetter(s) {
    if (typeof s !== 'string' || s.length === 0) {
        return '';
    }
    return s.charAt(0).toUpperCase() + s.slice(1);
}

