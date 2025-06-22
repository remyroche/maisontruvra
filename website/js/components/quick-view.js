// This function will be called to initialize the quick view functionality
export function initializeQuickView() {
    const modal = document.getElementById('quick-view-modal');
    if (!modal) return;
    
    const modalContent = modal.querySelector('.modal-content');
    const closeButton = modal.querySelector('.close-modal');

    // Close modal functionality
    const closeModal = () => {
        modal.classList.add('hidden');
    };

    if(closeButton) {
        closeButton.addEventListener('click', closeModal);
    }
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Open modal and fetch product data
    const openQuickView = async (productId) => {
        if (!productId) return;
        
        // Show loading state
        modalContent.innerHTML = '<p class="text-center p-8">Loading...</p>';
        modal.classList.remove('hidden');

        try {
            const product = await API.getProductById(productId);

            // Populate modal with product data
            modalContent.innerHTML = `
                <div class="p-6">
                    <h2 class="text-2xl font-bold mb-2">${product.name}</h2>
                    <p class="text-gray-600 mb-4">${product.description}</p>
                    <div class="flex justify-between items-center">
                        <span class="text-xl font-bold">€${product.price}</span>
                        <button class="add-to-cart-quick-view bg-primary text-white px-4 py-2 rounded-md" data-product-id="${product.id}">Add to Cart</button>
                    </div>
                </div>
            `;
            // Re-attach event listener for the new button
            modalContent.querySelector('.add-to-cart-quick-view').addEventListener('click', (e) => {
                const id = e.target.getAttribute('data-product-id');
                // You would call your cart service here, e.g., CartService.addItem(id, 1);
                console.log(`Adding product ${id} to cart from quick view.`);
                showToast(`${product.name} added to cart!`, 'success');
                closeModal();
            });

        } catch (error) {
            console.error('Error fetching product for quick view:', error);
            modalContent.innerHTML = '<p class="text-center p-8 text-red-500">Could not load product details.</p>';
            // Add error handling to API calls and use .catch()
            showToast('Error loading product details.', 'error');
        }
    };

    // Attach event listeners to all quick view buttons on the page
    document.querySelectorAll('.quick-view-btn').forEach(button => {
        button.addEventListener('click', (event) => {
            const productId = event.currentTarget.getAttribute('data-product-id');
            openQuickView(productId);
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // Check if the modal element exists on the page
    const modal = document.getElementById('quick-view-modal');
    if (!modal) {
        // If the modal HTML is not on the page, do nothing.
        // This allows the script to be included on all pages without causing errors.
        return;
    }

    // --- DOM Elements ---
    const modalContent = document.getElementById('modal-content');
    const closeButton = document.getElementById('modal-close');

    // --- State ---
    let currentProductId = null;

    // --- UI Functions ---

    /**
     * Renders a loading state inside the modal.
     */
    const renderLoading = () => {
        modalContent.innerHTML = `<div class="text-center p-8"><p class="text-gray-600">Chargement du produit...</p></div>`;
    };

    /**
     * Renders an error state inside the modal.
     * @param {string} message - The error message to display.
     */
    const renderError = (message) => {
        modalContent.innerHTML = `<div class="text-center p-8"><p class="text-red-500">${message}</p></div>`;
    };

    /**
     * Renders the fetched product data into the modal.
     * @param {object} product - The product data object from the API.
     */
    const renderProduct = (product) => {
        modalContent.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <img src="${product.image}" alt="${product.name}" class="w-full h-auto object-cover rounded-lg shadow-md" onerror="this.onerror=null;this.src='https://placehold.co/600x600/eeeeee/cccccc?text=Image';">
                </div>
                <div>
                    <h2 class="text-3xl font-bold">${product.name}</h2>
                    <p class="text-2xl font-semibold my-4">${product.price.toFixed(2)} €</p>
                    <div class="text-sm text-gray-600 space-y-2 mb-6">
                        ${product.short_description}
                    </div>
                    <div class="flex items-center space-x-4 mb-6">
                        <label for="quantity-qv" class="font-semibold">Quantité:</label>
                        <input type="number" id="quantity-qv" value="1" min="1" class="w-20 p-2 border border-gray-300 rounded-md text-center">
                    </div>
                    <button id="add-to-cart-qv-btn" class="w-full bg-black text-white font-bold py-3 px-8 rounded-md hover:bg-gray-800 transition-colors">
                        Ajouter au Panier
                    </button>
                    <div class="text-center mt-4">
                        <a href="/produit-detail.html?id=${product.id}" class="text-sm text-gray-600 hover:underline">Voir les détails complets &rarr;</a>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listener for the new "Add to Cart" button
        document.getElementById('add-to-cart-qv-btn').addEventListener('click', handleAddToCart);
    };
    
    // --- Event Handlers ---

    /**
     * Handles adding the selected quantity of the product to the cart.
     */
    const handleAddToCart = async () => {
        const quantityInput = document.getElementById('quantity-qv');
        const quantity = parseInt(quantityInput.value, 10);

        if (currentProductId && quantity > 0) {
            try {
                // Assuming a global cartApi object exists
                await cartApi.addItem({ productId: currentProductId, quantity });
                alert(`${quantity} x produit ajouté au panier !`);
                closeModal();
                // Optionally, update the cart icon count in the header
                // window.updateCartCount(); 
            } catch (error) {
                alert("Erreur lors de l'ajout au panier. Veuillez réessayer.");
                console.error("Add to cart error:", error);
            }
        }
    };

    /**
     * Opens the modal and fetches product data.
     * @param {string|number} productId - The ID of the product to display.
     */
    const openModal = async (productId) => {
        currentProductId = productId;
        modal.classList.add('visible');
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
        renderLoading();

        try {
            // Assuming a global api object exists for fetching product details
            const product = await api.getProductDetails(productId);
            renderProduct(product);
        } catch (error) {
            console.error("Failed to load quick view data:", error);
            renderError("Impossible de charger les informations du produit.");
        }
    };

    /**
     * Closes the modal and resets its state.
     */
    const closeModal = () => {
        modal.classList.remove('visible');
        document.body.style.overflow = ''; // Restore background scrolling
        // Clear content after the fade-out transition completes
        setTimeout(() => {
            modalContent.innerHTML = '';
            currentProductId = null;
        }, 300);
    };

    // --- Global Function and Event Listeners ---

    // Expose the openModal function to the global window object
    window.openQuickView = openModal;

    // Close modal via the close button
    closeButton.addEventListener('click', closeModal);

    // Close modal by clicking on the overlay
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close modal by pressing the Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('visible')) {
            closeModal();
        }
    });
});
