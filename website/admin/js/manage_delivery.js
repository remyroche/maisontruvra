import { apiClient } from '../../js/api-client.js';

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('methods-table-body');
    const modal = document.getElementById('method-modal');
    const form = document.getElementById('method-form');
    const modalTitle = document.getElementById('modal-title');
    const methodIdInput = document.getElementById('method-id');
    const tiersContainer = document.getElementById('tiers-checkbox-container');
    
    let allTiers = [];

    const fetchAllTiers = async () => {
        try {
            const response = await apiClient.get('/admin/delivery-methods/tiers');
            allTiers = response.data;
        } catch (error) {
            console.error("Failed to fetch tiers:", error);
            alert("Erreur: Impossible de charger les niveaux de fidélité.");
        }
    };

    const populateTiersCheckboxes = (selectedTierNames = []) => {
        tiersContainer.innerHTML = allTiers.map(tier => `
            <div class="flex items-start">
                <div class="flex items-center h-5">
                    <input id="tier-${tier.id}" name="tiers" type="checkbox" value="${tier.id}"
                           ${selectedTierNames.includes(tier.name) ? 'checked' : ''}
                           class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded">
                </div>
                <div class="ml-3 text-sm">
                    <label for="tier-${tier.id}" class="font-medium text-gray-700">${tier.name}</label>
                </div>
            </div>
        `).join('');
    };

    const fetchAndRenderMethods = async () => {
        try {
            const response = await apiClient.get('/admin/delivery-methods');
            const methods = response.data;
            tableBody.innerHTML = methods.map(method => `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${method.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${method.description}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">€${method.price.toFixed(2)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${method.accessible_to_tiers.map(tier => `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">${tier}</span>`).join(' ')}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button class="edit-btn text-indigo-600 hover:text-indigo-900" data-id="${method.id}">Modifier</button>
                        <button class="delete-btn text-red-600 hover:text-red-900 ml-4" data-id="${method.id}">Supprimer</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error("Failed to load delivery methods:", error);
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4">Erreur de chargement des méthodes.</td></tr>`;
        }
    };
    
    const openModal = (method = null) => {
        form.reset();
        if (method) {
            modalTitle.textContent = "Modifier la Méthode de Livraison";
            methodIdInput.value = method.id;
            document.getElementById('name').value = method.name;
            document.getElementById('description').value = method.description;
            document.getElementById('price').value = method.price;
            populateTiersCheckboxes(method.accessible_to_tiers);
        } else {
            modalTitle.textContent = "Ajouter une Méthode de Livraison";
            methodIdInput.value = '';
            populateTiersCheckboxes();
        }
        modal.classList.remove('modal-inactive');
        modal.classList.add('modal-active');
    };

    const closeModal = () => {
        modal.classList.add('modal-inactive');
        modal.classList.remove('modal-active');
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = methodIdInput.value;
        const selectedTierIds = Array.from(tiersContainer.querySelectorAll('input:checked')).map(input => parseInt(input.value));
        
        const data = {
            name: document.getElementById('name').value,
            description: document.getElementById('description').value,
            price: document.getElementById('price').value,
            tier_ids: selectedTierIds
        };

        try {
            if (id) {
                await apiClient.put(`/admin/delivery-methods/${id}`, data);
            } else {
                await apiClient.post('/admin/delivery-methods', data);
            }
            closeModal();
            fetchAndRenderMethods();
        } catch (error) {
            console.error("Failed to save method:", error);
            alert("Erreur lors de la sauvegarde.");
        }
    });

    tableBody.addEventListener('click', async (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const id = e.target.dataset.id;
            try {
                const response = await apiClient.get('/admin/delivery-methods');
                const method = response.data.find(m => m.id == id);
                if (method) openModal(method);
            } catch(error) {
                console.error("Failed to fetch method details", error);
            }
        }

        if (e.target.classList.contains('delete-btn')) {
            const id = e.target.dataset.id;
            if (confirm("Êtes-vous sûr de vouloir supprimer cette méthode ?")) {
                try {
                    await apiClient.delete(`/admin/delivery-methods/${id}`);
                    fetchAndRenderMethods();
                } catch (error) {
                    console.error("Failed to delete method:", error);
                    alert("Erreur lors de la suppression.");
                }
            }
        }
    });

    document.getElementById('add-method-btn').addEventListener('click', () => openModal());
    document.getElementById('cancel-btn').addEventListener('click', closeModal);

    // Initial load
    (async () => {
        await fetchAllTiers();
        await fetchAndRenderMethods();
    })();
});
