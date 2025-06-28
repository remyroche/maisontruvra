// productUtils.js

/**
 * Renders a list of products into a specified container element.
 * @param {Array} products - The array of product objects to render.
 * @param {HTMLElement} container - The DOM element where products will be rendered.
 */
export function renderProducts(products, container) {
    container.innerHTML = ''; // Clear existing content

    if (!products || products.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500">No products found.</p>';
        return;
    }

    products.forEach(product => {
        const productElement = document.createElement('div');
        productElement.className = 'product-item';
        productElement.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}" class="product-image">
            <h2 class="product-name">${product.name}</h2>
            <p class="product-price">${product.price} €</p>
            <button class="add-to-cart-btn" data-product-id="${product.id}">Add to Cart</button>
        `;
        container.appendChild(productElement);
    });
}
