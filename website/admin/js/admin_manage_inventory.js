import { AdminAPI } from './admin_api.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('inventory-table-body');
    if(!tableBody) return;

    const loadInventory = async () => {
        try {
            const inventoryItems = await AdminAPI.getInventory();
            tableBody.innerHTML = '';
            inventoryItems.forEach(item => {
                const row = document.createElement('tr');
                row.className = 'border-b';
                row.innerHTML = `
                    <td class="p-2">${item.product_name}</td>
                    <td class="p-2">${item.sku}</td>
                    <td class="p-2">${item.stock}</td>
                    <td class="p-2 flex items-center">
                        <input type="number" class="w-24 p-1 border rounded-md" placeholder="New Stock">
                        <button class="ml-2 bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600" data-id="${item.id}">Update</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } catch (error) {
            showToast('Failed to load inventory', 'error');
        }
    };

    tableBody.addEventListener('click', async (e) => {
        if(e.target.tagName !== 'BUTTON') return;

        const button = e.target;
        const row = button.closest('tr');
        const input = row.querySelector('input[type="number"]');
        const newStock = input.value;
        const inventoryId = button.dataset.id;

        if (newStock === '' || isNaN(newStock)) {
            showToast('Please enter a valid stock number.', 'error');
            return;
        }

        try {
            await AdminAPI.updateInventory(inventoryId, { stock: parseInt(newStock) });
            showToast('Stock updated successfully.', 'success');
            loadInventory(); // Refresh the list
        } catch (error) {
            showToast('Failed to update stock.', 'error');
        }
    });

    loadInventory();
});
