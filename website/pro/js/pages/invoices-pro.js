/**
 * Manages the B2B invoices page.
 */
import { ProAPI } from '../pro_api.js';
import { requireB2BAuth } from '../../js/auth_service.js';
import { showNotification } from '../../js/common/ui.js';
import { t } from '../../js/i18n.js';

document.addEventListener('DOMContentLoaded', () => {
    requireB2BAuth();

    const invoicesTableBody = document.querySelector('#invoices-table tbody');
    
    if (!invoicesTableBody) {
        console.error('Invoices table body not found.');
        return;
    }

    const createInvoiceRow = (invoice) => {
        const row = document.createElement('tr');
        const statusClass = invoice.status === 'Paid' ? 'text-green-600' : 'text-red-600';
        
        row.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${invoice.invoice_number}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${new Date(invoice.date).toLocaleDateString()}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${invoice.total_amount.toFixed(2)} €</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${statusClass}">${t('invoices.status.' + invoice.status.toLowerCase())}</td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a href="/api/b2b/invoices/${invoice.id}/download" class="text-indigo-600 hover:text-indigo-900">${t('invoices.download')}</a>
            </td>
        `;
        return row;
    };

    const loadInvoices = async () => {
        try {
            const invoices = await ProAPI.getInvoices();
            invoicesTableBody.innerHTML = '';
            if (invoices && invoices.length > 0) {
                invoices.forEach(invoice => {
                    invoicesTableBody.appendChild(createInvoiceRow(invoice));
                });
            } else {
                invoicesTableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4">${t('invoices.noInvoices')}</td></tr>`;
            }
        } catch (error) {
            console.error('Failed to load invoices:', error);
            showNotification(t('invoices.loadError'), 'error');
            invoicesTableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-red-500">${t('invoices.loadError')}</td></tr>`;
        }
    };

    loadInvoices();
});
