import { adminApi } from './admin_api.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    loadPassports();
});

async function loadPassports() {
    const tableBody = document.getElementById('passports-table-body');
    if (!tableBody) return;

    try {
        const passports = await adminApi.get('/passports');
        tableBody.innerHTML = ''; // Clear existing rows

        if (passports.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No passports found.</td></tr>';
            return;
        }

        passports.forEach(passport => {
            const row = `
                <tr>
                    <td class="px-4 py-2">${passport.id}</td>
                    <td class="px-4 py-2">${passport.product.name} (ID: ${passport.product_id})</td>
                    <td class="px-4 py-2 font-mono">${passport.unique_identifier}</td>
                    <td class="px-4 py-2">${new Date(passport.creation_date).toLocaleString()}</td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    } catch (error) {
        console.error('Failed to load passports:', error);
        showToast('Error loading passports.', 'error');
        tableBody.innerHTML = '<tr><td colspan="4" class="text-center text-red-500">Failed to load data.</td></tr>';
    }
}
