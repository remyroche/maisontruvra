import { DataTableFactory } from './components/DataTableFactory.js';
import { adminAPI } from './admin_common.js';

document.addEventListener('DOMContentLoaded', function () {
    let editStockModal;

    // Initialize the Bootstrap Modal once the DOM is ready
    const modalElement = document.getElementById('editStockModal');
    if (modalElement) {
        editStockModal = new bootstrap.Modal(modalElement);
    }

    const columns = [
        { data: 'product.name', title: 'Produit' },
        { data: 'product.sku', title: 'SKU' },
        { 
            data: 'quantity', 
            title: 'Quantité Totale',
            render: function(data, type, row) {
                // Display the quantity with an edit button
                return `${data} <button class="btn btn-sm btn-outline-warning ms-2 btn-edit-total" data-id="${row.id}" data-name="${row.product.name}" data-quantity="${data}">Modifier</button>`;
            }
        },
        { data: 'available_quantity', title: 'Disponible' },
        {
            data: 'id',
            title: 'Ajouter du Stock (Génère Passeports)',
            orderable: false,
            render: function(data, type, row) {
                return `
                    <div class="input-group input-group-sm" style="width: 150px;">
                        <input type="number" class="form-control" placeholder="Qté" aria-label="Quantity to add">
                        <button class="btn btn-success btn-add-stock" data-id="${data}" type="button">Ajouter</button>
                    </div>
                `;
            }
        }
    ];

    const inventoryTable = DataTableFactory.create('inventory-table', '/api/admin/inventory', columns);

    // --- Event Handler for ADDING stock (generates passports) ---
    $('#inventory-table tbody').on('click', '.btn-add-stock', async function () {
        const button = $(this);
        const inventoryId = button.data('id');
        const input = button.closest('.input-group').find('input');
        const quantityToAdd = input.val();

        if (!quantityToAdd || isNaN(quantityToAdd) || parseInt(quantityToAdd) <= 0) {
            Toastify({ text: 'Veuillez entrer une quantité positive à ajouter.', backgroundColor: 'orange' }).showToast();
            return;
        }

        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');

        try {
            const response = await adminAPI.post(`/inventory/${inventoryId}/add_stock`, {
                quantity: parseInt(quantityToAdd)
            });
            Toastify({ text: response.message, backgroundColor: 'green' }).showToast();
            inventoryTable.ajax.reload(null, false);
        } catch (error) {
            const errorMessage = error.responseJSON?.error || 'Une erreur est survenue.';
            Toastify({ text: errorMessage, backgroundColor: 'red' }).showToast();
        } finally {
            button.prop('disabled', false).text('Ajouter');
            input.val('');
        }
    });

    // --- Event Handlers for EDITING total stock (with warning) ---
    // 1. Open the warning modal when "Modifier" is clicked
    $('#inventory-table tbody').on('click', '.btn-edit-total', function () {
        const button = $(this);
        const inventoryId = button.data('id');
        const productName = button.data('name');
        const currentQuantity = button.data('quantity');
        
        // Populate and show the modal
        $('#modalInventoryId').val(inventoryId);
        $('#modalProductName').val(productName);
        $('#newTotalQuantity').val(currentQuantity);
        
        if(editStockModal) {
            editStockModal.show();
        }
    });

    // 2. Handle the final confirmation from within the modal
    $('#confirmStockUpdate').on('click', async function() {
        const button = $(this);
        const inventoryId = $('#modalInventoryId').val();
        const newQuantity = $('#newTotalQuantity').val();

        if (newQuantity === '' || isNaN(newQuantity) || parseInt(newQuantity) < 0) {
            alert('Veuillez entrer une quantité totale valide.');
            return;
        }

        button.prop('disabled', true).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>');

        try {
            // This endpoint just sets the total quantity and does NOT create passports.
            const response = await adminAPI.put(`/inventory/${inventoryId}`, {
                quantity: parseInt(newQuantity)
            });
            Toastify({ text: response.message, backgroundColor: 'green' }).showToast();
            inventoryTable.ajax.reload(null, false);
            if(editStockModal) {
                editStockModal.hide();
            }
        } catch (error) {
            const errorMessage = error.responseJSON?.error || 'Une erreur est survenue.';
            Toastify({ text: errorMessage, backgroundColor: 'red' }).showToast();
        } finally {
            button.prop('disabled', false).text('Confirmer la modification');
        }
    });
});

