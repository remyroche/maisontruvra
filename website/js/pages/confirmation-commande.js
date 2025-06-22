/**
 * Manages the order confirmation page.
 */
import { API } from '../api.js';
import { showNotification } from '../common/ui.js';
import { t } from '../i18n.js';

document.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const orderId = params.get('orderId');

    const orderNumberEl = document.getElementById('order-number');
    const orderItemsEl = document.getElementById('order-items');
    const orderTotalEl = document.getElementById('order-total');
    
    if (!orderId) {
        console.error('Order ID not found in URL.');
        document.body.innerHTML = `<p>${t('confirmation.noOrderId')}</p>`;
        return;
    }

    const loadOrderDetails = async () => {
        try {
            const order = await API.getOrderDetails(orderId);
            if (order) {
                orderNumberEl.textContent = order.id;
                orderTotalEl.textContent = `${order.total_amount.toFixed(2)} €`;

                orderItemsEl.innerHTML = ''; // Clear existing items
                order.items.forEach(item => {
                    const li = document.createElement('li');
                    li.className = 'flex justify-between py-2 border-b';
                    li.innerHTML = `
                        <span>${item.product_name} (x${item.quantity})</span>
                        <span>${item.price.toFixed(2)} €</span>
                    `;
                    orderItemsEl.appendChild(li);
                });
            } else {
                throw new Error('Order not found');
            }
        } catch (error) {
            console.error('Failed to load order details:', error);
            showNotification(t('confirmation.loadError'), 'error');
            if (orderNumberEl) {
                orderNumberEl.textContent = 'N/A';
            }
        }
    };

    if (orderNumberEl && orderItemsEl && orderTotalEl) {
        loadOrderDetails();
    }
});
