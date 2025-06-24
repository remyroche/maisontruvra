import { adminAPI } from './admin_common.js';

document.addEventListener('DOMContentLoaded', function () {
    const galleryContainer = document.getElementById('asset-gallery-container');
    const uploadForm = document.getElementById('upload-form');

    const loadAssets = async () => {
        try {
            const assets = await adminAPI.get('/assets');
            renderAssets(assets);
        } catch (error) {
            galleryContainer.innerHTML = '<p class="text-danger">Impossible de charger la bibliothèque de médias.</p>';
        }
    };

    const renderAssets = (assets) => {
        if (!assets || assets.length === 0) {
            galleryContainer.innerHTML = '<p class="text-muted">Aucun média trouvé.</p>';
            return;
        }

        galleryContainer.innerHTML = assets.map(asset => `
            <div class="asset-card" id="asset-card-${asset.id}">
                <img src="${asset.url}" alt="${asset.filename}">
                <div class="card-body">
                    <p class="card-text small text-muted text-truncate" title="${asset.filename}">${asset.filename}</p>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-outline-secondary btn-copy-url" data-url="${asset.url}">Copier</button>
                    <button class="btn btn-sm btn-outline-danger btn-delete-asset" data-id="${asset.id}">Suppr.</button>
                </div>
            </div>
        `).join('');
    };

    // Handle form submission for new uploads
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        const button = uploadForm.querySelector('button[type="submit"]');
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

        try {
            await adminAPI.post('/assets/upload', formData, true); // true indicates FormData
            Toastify({ text: 'Image uploadée avec succès!', backgroundColor: 'green' }).showToast();
            uploadForm.reset();
            loadAssets(); // Refresh gallery
        } catch (error) {
            const errorMessage = error.responseJSON?.error || 'Échec de l\'upload.';
            Toastify({ text: errorMessage, backgroundColor: 'red' }).showToast();
        } finally {
            button.disabled = false;
            button.textContent = 'Uploader';
        }
    });
    
    // Event delegation for copy and delete buttons
    galleryContainer.addEventListener('click', async (e) => {
        if (e.target.classList.contains('btn-copy-url')) {
            const urlToCopy = e.target.dataset.url;
            navigator.clipboard.writeText(window.location.origin + urlToCopy)
                .then(() => Toastify({ text: 'URL copiée!', backgroundColor: 'blue' }).showToast())
                .catch(() => Toastify({ text: 'Erreur de copie', backgroundColor: 'red' }).showToast());
        }

        if (e.target.classList.contains('btn-delete-asset')) {
            if (!confirm('Êtes-vous sûr de vouloir supprimer cette image ? Cette action est irréversible.')) {
                return;
            }
            const assetId = e.target.dataset.id;
            try {
                await adminAPI.delete(`/assets/${assetId}`);
                Toastify({ text: 'Image supprimée.', backgroundColor: 'green' }).showToast();
                // Remove the card from the DOM directly for a faster UI response
                document.getElementById(`asset-card-${assetId}`).remove();
            } catch (error) {
                 const errorMessage = error.responseJSON?.error || 'Erreur lors de la suppression.';
                 Toastify({ text: errorMessage, backgroundColor: 'red' }).showToast();
            }
        }
    });

    // Initial load
    loadAssets();
});
