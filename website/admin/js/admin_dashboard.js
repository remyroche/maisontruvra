// website/source/admin/js/admin_dashboard.js
import { apiClient } from './api-client.js';

document.addEventListener('DOMContentLoaded', function() {
    const summaryContainer = document.getElementById('admin-summary-container');
    if (!summaryContainer) return;

    const renderSummary = (data) => {
        summaryContainer.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Total Users</h5>
                            <p class="card-text">${data.total_users}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Pending Orders</h5>
                            <p class="card-text">${data.pending_orders}</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">Products Out of Stock</h5>
                            <p class="card-text">${data.products_out_of_stock}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    };

    const loadSummary = () => {
        summaryContainer.innerHTML = '<p>Loading summary data...</p>';
        apiClient.get('/admin/dashboard-summary')
            .then(data => {
                renderSummary(data);
            })
            .catch(error => {
                summaryContainer.innerHTML = '<div class="alert alert-danger">Could not load summary data.</div>';
                console.error("Failed to load admin summary:", error);
            });
    };

    loadSummary();
});
