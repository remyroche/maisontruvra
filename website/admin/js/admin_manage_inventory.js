import { DataTableFactory } from './components/DataTableFactory.js';
import { adminAPI } from './admin_common.js'; // Assuming adminAPI helper exists

document.addEventListener('DOMContentLoaded', function () {
    const columns = [
        { data: 'product.name', title: 'Produit' },
        { data: 'product.sku', title: 'SKU' },
        { 
            data: 'quantity', 
            title: 'Quantité Totale',
            render: function(data, type, row) {
                // Render as an input field for editing
                return `<input type="number" class="form-control form-control-sm" value="${data}" style="width: 80px;">`;
            }
        },
        { 
            data: 'available_quantity',
            title: 'Disponible',
            render: function(data, type, row) {
                // Display-only, calculated on the backend
                return `<span class="badge bg-secondary">${data}</span>`;
            }
        },
        {
            data: 'id',
            title: 'Actions',
            render: function(data, type, row) {
                // The 'data' here is the inventory ID
                return `<button class="btn btn-primary btn-sm btn-save" data-id="${data}">Enregistrer</button>`;
            }
        }
    ];

    const inventoryTable = DataTableFactory.create('inventory-table', '/api/admin/inventory', columns);

    // Add event listener for the save button
    $('#inventory-table tbody').on('click', '.btn-save', async function () {
        const button = $(this);
        const inventoryId = button.data('id');
        const row = button.closest('tr');
        const quantityInput = row.find('input[type="number"]');
        const newQuantity = quantityInput.val();

        if (newQuantity === '' || isNaN(newQuantity) || parseInt(newQuantity) < 0) {
            alert('Veuillez entrer une quantité valide.');
            return;
        }

        button.prop('disabled', true).text('Sauvegarde...');

        try {
            // This is the key API call that triggers the back-in-stock logic
            const response = await adminAPI.put(`/inventory/${inventoryId}`, {
                quantity: parseInt(newQuantity)
            });

            // On success, show a confirmation and refresh the table data
            // to show updated "Available Quantity"
            Toastify({ text: response.message, backgroundColor: 'green' }).showToast();
            inventoryTable.ajax.reload(null, false); // false = keep paging

        } catch (error) {
            console.error('Failed to update inventory:', error);
            const errorMessage = error.responseJSON?.error || 'Une erreur est survenue.';
            Toastify({ text: errorMessage, backgroundColor: 'red' }).showToast();
        } finally {
            button.prop('disabled', false).text('Enregistrer');
        }
    });
});
