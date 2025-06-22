/**
 * Manages dynamic elements in the site header, like the cart icon count.
 */
document.addEventListener('DOMContentLoaded', () => {
    const cartIconCount = document.getElementById('cart-icon-count');

    if (!cartIconCount) return;

    /**
     * Updates the cart icon with the total number of items.
     * @param {object} cartState - The state object from cartStore.
     */
    function updateCartIcon(cartState) {
        const totalItems = cartState.items.reduce((sum, item) => sum + item.quantity, 0);

        if (totalItems > 0) {
            cartIconCount.textContent = totalItems;
            cartIconCount.style.display = 'flex'; // Or 'block'
        } else {
            cartIconCount.style.display = 'none';
        }
    }

    // Subscribe to the cart store
    window.cartStore.subscribe(updateCartIcon);

    // Initial update
    updateCartIcon(window.cartStore.getState());
});

