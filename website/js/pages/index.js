import { initializeApp } from '../main.js';
import * as api from '../api.js';
import { renderProduct } from '../ui.js';

initializeApp();

document.addEventListener('DOMContentLoaded', () => {
    const featuredContainer = document.getElementById('featured-products');
    if (featuredContainer) {
        api.getProducts()
            .then(products => {
                products.slice(0, 4).forEach(product => { // Show 4 featured products
                    featuredContainer.appendChild(renderProduct(product));
                });
            })
            .catch(error => {
                featuredContainer.innerHTML = "<p>Could not load featured products.</p>";
            });
    }
});
