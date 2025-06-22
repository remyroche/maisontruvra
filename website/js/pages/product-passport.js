// NEW FILE: website/source/js/pages/product-passport.js
// Fetches and displays the product details for the passport page.

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('passport-container');
    const loadingIndicator = document.getElementById('loading');

    const params = new URLSearchParams(window.location.search);// This new script is dedicated to the new passport page. It's kept separate from
// `produit-detail.js` because their functionalities are distinct.

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('passport-container');
    const loadingIndicator = document.getElementById('loading');

    const params = new URLSearchParams(window.location.search);
    const itemId = params.get('item_id');

    if (!itemId) {
        container.innerHTML = '<h1 class="text-2xl font-bold text-brand-primary text-center">ID d\'article manquant</h1><p class="text-center mt-4">Veuillez scanner un QR code valide.</p>';
        return;
    }

    try {
        const item = await fetchWithAuth(`${getApiBaseUrl()}/products/items/${itemId}/details`);
        const product = item.product;
        
        loadingIndicator.style.display = 'none';

        container.innerHTML = `
            <div class="border-b-2 border-brand-secondary pb-4 mb-6">
                <h1 class="text-4xl font-bold font-serif text-brand-primary text-center">Passeport Produit Unique</h1>
            </div>
            
            <div class="grid md:grid-cols-2 gap-8 items-center">
                <div>
                    <img src="${product.image_url || '[https://placehold.co/600x400/F5DEB3/8B4513?text=Image+Produit](https://placehold.co/600x400/F5DEB3/8B4513?text=Image+Produit)'}" alt="Image de ${product.name}" class="rounded-lg shadow-md w-full">
                </div>
                <div>
                    <h2 class="text-3xl font-bold text-brand-primary">${product.name}</h2>
                    <p class="text-lg text-gray-500 mt-1">Numéro de Série: <strong>${item.serial_number}</strong></p>
                    <p class="text-2xl text-gray-800 my-4">${product.price.toFixed(2)} €</p>
                    <div class="text-base text-gray-700 space-y-2">
                        <p><strong>Catégorie:</strong> ${product.category.name}</p>
                        <p><strong>Statut:</strong> <span class="font-semibold px-2 py-1 rounded ${item.status === 'available' ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}">${item.status.charAt(0).toUpperCase() + item.status.slice(1)}</span></p>
                    </div>
                </div>
            </div>

            <div class="mt-8 pt-6 border-t border-brand-secondary">
                <h3 class="text-2xl font-bold text-brand-primary mb-3">Description du Modèle</h3>
                <p class="text-gray-700 leading-relaxed">${product.description}</p>
            </div>
        `;

    } catch (error) {
        loadingIndicator.style.display = 'none';
        console.error('Failed to load item passport:', error);
        container.innerHTML = '<h1 class="text-2xl font-bold text-red-600 text-center">Erreur</h1><p class="text-center mt-4">Impossible de charger les détails de l\'article.</p>';
    }
});
