import { initializeAdminPage } from './admin_common.js';
import { ADMIN_API_BASE_URL } from './admin_config.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('invoices-table-body');
    const createBtn = document.getElementById('create-invoice-btn');
    // Assume you have a modal with id 'invoice-modal' in your HTML
    const modal = document.getElementById('invoice-modal'); 
    
    if (!tableBody) return;

    const loadInvoices = async () => {
        try {
            const invoices = await AdminAPI.getInvoices();
            tableBody.innerHTML = '';
            invoices.forEach(inv => {
                const row = document.createElement('tr');
                // ... logic to render each invoice row ...
                tableBody.appendChild(row);
            });
        } catch (error) {
            showToast('Failed to load invoices.', 'error');
        }
    };

    createBtn.addEventListener('click', () => {
        // ... logic to clear and open the 'create invoice' modal ...
        modal.style.display = 'block';
    });
    
    // Add event listener to the modal's form submission
    // const invoiceForm = document.getElementById('invoice-form');
    // invoiceForm.addEventListener('submit', async (e) => { ... });

    loadInvoices();
});


function initInvoicesPage() {
    const token = localStorage.getItem('admin_token');
    const invoicesTableBody = document.querySelector('#invoices-table tbody');

    const fetchInvoices = async () => {
        try {
            const response = await fetch(`${ADMIN_API_BASE_URL}/b2b/invoices`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) throw new Error('Failed to fetch invoices');
            const invoices = await response.json();
            renderInvoices(invoices);
        } catch (error) {
            showToast(error.message, 'error');
        }
    };

    const renderInvoices = (invoices) => {
        invoicesTableBody.innerHTML = '';
        if (!invoices || invoices.length === 0) {
            invoicesTableBody.innerHTML = '<tr><td colspan="6">No invoices found.</td></tr>';
            return;
        }
        invoices.forEach(invoice => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${invoice.id}</td>
                <td>${invoice.b2b_client_name || 'N/A'}</td>
                <td>€${invoice.amount.toFixed(2)}</td>
                <td>${invoice.status}</td>
                <td>${new Date(invoice.due_date).toLocaleDateString()}</td>
                <td class="actions">
                    <button class="btn" onclick="window.open('${invoice.pdf_url}', '_blank')">View PDF</button>
                </td>
            `;
            invoicesTableBody.appendChild(row);
        });
    };

    fetchInvoices();
}

initializeAdminPage(initInvoicesPage);
