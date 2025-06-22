import { AdminAPI } from './admin_api.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const logColumns = [
        { header: 'Timestamp', key: 'timestamp', cell: l => new Date(l.timestamp).toLocaleString() },
        { header: 'Event Type', key: 'event_type', cell: l => `<span class="font-mono text-xs">${l.event_type}</span>` },
        { header: 'User ID', key: 'user_id' },
        { header: 'Details', key: 'details', cell: l => `<pre class="text-xs">${JSON.stringify(l.details, null, 2)}</pre>`},
    ];
    
    const fetchLogs = async (page = 1) => {
        const response = await apiClient.get(`/admin/audit-log?page=${page}&per_page=25`);
        if (!response.ok) throw new Error('Failed to fetch logs');
        return response.data;
    };

    new DataTableFactory('logs-table-container', {
        columns: logColumns,
        fetchData: fetchLogs,
        dataKey: 'logs',
        totalKey: 'total_logs'
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const logBody = document.getElementById('audit-log-body');
    if(!logBody) return;

    const loadAuditLog = async () => {
        try {
            const logs = await AdminAPI.getAuditLogs();
            logBody.innerHTML = '';
            logs.forEach(log => {
                const row = document.createElement('tr');
                row.className = 'border-b';
                row.innerHTML = `
                    <td class="p-2">${new Date(log.timestamp).toLocaleString()}</td>
                    <td class="p-2">${log.user_email}</td>
                    <td class="p-2">${log.action}</td>
                    <td class="p-2">${log.details}</td>
                `;
                logBody.appendChild(row);
            });
        } catch (error) {
            showToast('Failed to load audit logs', 'error');
        }
    };

    loadAuditLog();
});
