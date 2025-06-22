import { checkAdminAuth, loadAdminHeader } from './admin_common.js';
import { AdminApi } from './admin_api.js';
import { config } from './admin_config.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', async () => {
    await checkAdminAuth();
    await loadAdminHeader();
    const api = new AdminApi(config.api_url, localStorage.getItem('admin_token'));

    const form = document.getElementById('collection-form');
    const formTitle = document.getElementById('form-title');
    const collectionIdInput = document.getElementById('collection-id');
    const collectionNameInput = document.getElementById('collection-name');
    const collectionDescriptionInput = document.getElementById('collection-description');
    const tableBody = document.getElementById('collections-table-body');
    const cancelBtn = document.getElementById('cancel-edit-btn');

    async function fetchAndRenderCollections() {
        try {
            const collections = await api.getCollections();
            tableBody.innerHTML = collections.map(c => `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${c.name}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${c.description || ''}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button class="edit-btn text-indigo-600 hover:text-indigo-900" data-id="${c.id}" data-name="${c.name}" data-description="${c.description || ''}">Edit</button>
                        <button class="delete-btn text-red-600 hover:text-red-900 ml-4" data-id="${c.id}">Delete</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            showToast('Failed to load collections', true);
        }
    }

    function resetForm() {
        form.reset();
        collectionIdInput.value = '';
        formTitle.textContent = 'Add New Collection';
        cancelBtn.classList.add('hidden');
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = collectionIdInput.value;
        const data = {
            name: collectionNameInput.value,
            description: collectionDescriptionInput.value,
        };

        try {
            if (id) {
                await api.updateCollection(id, data);
                showToast('Collection updated successfully');
            } else {
                await api.createCollection(data);
                showToast('Collection created successfully');
            }
            resetForm();
            await fetchAndRenderCollections();
        } catch (error) {
            showToast(`Error: ${error.message}`, true);
        }
    });

    tableBody.addEventListener('click', async (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const { id, name, description } = e.target.dataset;
            collectionIdInput.value = id;
            collectionNameInput.value = name;
            collectionDescriptionInput.value = description;
            formTitle.textContent = 'Edit Collection';
            cancelBtn.classList.remove('hidden');
            window.scrollTo(0, 0);
        }

        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Are you sure you want to delete this collection?')) {
                const { id } = e.target.dataset;
                try {
                    await api.deleteCollection(id);
                    showToast('Collection deleted');
                    await fetchAndRenderCollections();
                } catch (error) {
                    showToast(`Error: ${error.message}`, true);
                }
            }
        }
    });

    cancelBtn.addEventListener('click', resetForm);

    fetchAndRenderCollections();
});
