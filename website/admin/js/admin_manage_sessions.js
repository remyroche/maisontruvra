// This file handles the logic for the "Manage Sessions" page in the admin panel.
// It allows an admin to view all active user sessions and revoke them if necessary.

import { apiClient } from './api-client.js'; // Adjust path if needed
document.addEventListener('DOMContentLoaded', function () {
    const healthCheckContainer = document.getElementById('health-check-container');
    if (!healthCheckContainer) return;

    const renderStatus = (serviceName, data) => {
        const statusClass = data.status === 'ok' ? 'text-success' : 'text-danger';
        const latency = data.latency_ms ? `(${data.latency_ms} ms)` : '';
        const errorMessage = data.status !== 'ok' ? `<p class="text-muted small">${data.error_message}</p>` : '';

        return `
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">${serviceName.charAt(0).toUpperCase() + serviceName.slice(1)}</h5>
                    <p class="card-text">
                        Status: <strong class="${statusClass}">${data.status.toUpperCase()}</strong> ${latency}
                    </p>
                    ${errorMessage}
                </div>
            </div>
        `;
    };

    const loadHealthStatus = () => {
        healthCheckContainer.innerHTML = '<p>Checking system health...</p>';

        apiClient.get('/admin/monitoring/health')
            .then(data => {
                let content = '';
                for (const [service, statusData] of Object.entries(data)) {
                    content += renderStatus(service, statusData);
                }
                healthCheckContainer.innerHTML = content;
            })
            .catch(error => {
                healthCheckContainer.innerHTML = `
                    <div class="alert alert-danger">
                        Could not retrieve system health status. Please try again later.
                    </div>
                `;
                console.error('Health check failed:', error);
            });
    };

    loadHealthStatus();
});


});
