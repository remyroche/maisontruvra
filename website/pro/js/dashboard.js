// website/source/pro/js/dashboard.js
import { apiClient } from '../js/api-client.js';

document.addEventListener('DOMContentLoaded', function () {
    const dashboardContainer = document.getElementById('b2b-dashboard-container');
    if (!dashboardContainer) return;

    const renderDashboard = (data) => {
        dashboardContainer.innerHTML = '';

        const ordersHtml = data.recent_orders?.length
            ? data.recent_orders.map(o => `<li>Order #${o.id} - Status: <strong>${o.status}</strong></li>`).join('')
            : '<li>No recent orders found.</li>';
        
        const invoicesHtml = data.pending_invoices?.length
            ? data.pending_invoices.map(i => `<li>Invoice #${i.id} - Amount: $${i.amount}</li>`).join('')
            : '<li>No pending invoices.</li>';

        const loyaltyHtml = data.loyalty_status
            ? `<p>Current Tier: <strong>${data.loyalty_status.tier_name}</strong> | Points: <strong>${data.loyalty_status.points}</strong></p>`
            : '<p>No loyalty information available.</p>';

        dashboardContainer.innerHTML = `
            <div class="card mb-4">
                <div class="card-header"><h4>Recent Orders</h4></div>
                <div class="card-body"><ul>${ordersHtml}</ul></div>
            </div>
            <div class="card mb-4">
                <div class="card-header"><h4>Pending Invoices</h4></div>
                <div class="card-body"><ul>${invoicesHtml}</ul></div>
            </div>
            <div class="card">
                <div class="card-header"><h4>Loyalty Status</h4></div>
                <div class="card-body">${loyaltyHtml}</div>
            </div>
        `;
    };

    const loadDashboard = () => {
        dashboardContainer.innerHTML = '<p>Loading dashboard...</p>';
        apiClient.get('/b2b/dashboard-summary')
            .then(data => {
                renderDashboard(data);
            })
            .catch(error => {
                dashboardContainer.innerHTML = '<div class="alert alert-danger">Could not load B2B dashboard data.</div>';
                console.error("Failed to load B2B dashboard:", error);
            });
    };

    loadDashboard();
});
