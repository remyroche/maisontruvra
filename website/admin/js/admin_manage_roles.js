// website/source/admin/js/admin_manage_roles.js

import { checkAdminAuth, loadAdminHeader } from './admin_common.js';
import { showToast } from './admin_ui.js';
import { config } from './admin_config.js';
import { AdminApi } from './admin_api.js';

document.addEventListener('DOMContentLoaded', async () => {
    await checkAdminAuth();
    const api = new AdminApi(config.api_url, localStorage.getItem('admin_token'));
    await loadAdminHeader();

    const container = document.getElementById('roles-table-container');
    const loadingEl = document.getElementById('roles-loading');
    const saveBtn = document.getElementById('save-roles-btn');

    let state = {
        roles: [],
        permissions: [],
        permissionGroups: {}
    };

    function groupPermissions(permissions) {
        const groups = {};
        permissions.forEach(p => {
            const groupName = p.split('_')[0]; // e.g., "VIEW" from "VIEW_USERS"
            if (!groups[groupName]) {
                groups[groupName] = [];
            }
            groups[groupName].push(p);
        });
        return groups;
    }

    async function fetchData() {
        try {
            const [rolesRes, permsRes] = await Promise.all([
                api.get('/admin/users/roles/all-with-permissions'),
                api.get('/admin/users/permissions-map')
            ]);

            if (!rolesRes.ok || !permsRes.ok) {
                throw new Error('Failed to fetch roles or permissions.');
            }

            state.roles = await rolesRes.json();
            state.permissions = await permsRes.json();
            state.permissionGroups = groupPermissions(state.permissions);

            renderTable();
            loadingEl.classList.add('hidden');
            container.classList.remove('hidden');

        } catch (error) {
            console.error(error);
            loadingEl.textContent = 'Error loading data. Please refresh.';
            showToast(error.message, true);
        }
    }

    function renderTable() {
        let tableHtml = '<table class="min-w-full divide-y divide-gray-200">';
        
        // Header Row
        tableHtml += '<thead class="bg-gray-50"><tr>';
        tableHtml += '<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Permission</th>';
        state.roles.forEach(role => {
            // Do not render the 'Admin' role as it's not editable
            if (role.name.toLowerCase() !== 'admin') {
                tableHtml += `<th scope="col" class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">${role.name}</th>`;
            }
        });
        tableHtml += '</tr></thead>';

        // Body Rows
        tableHtml += '<tbody class="bg-white divide-y divide-gray-200">';
        for (const groupName in state.permissionGroups) {
             // Group Header Row
            tableHtml += `
                <tr class="bg-gray-50">
                    <td colspan="${state.roles.length}" class="px-4 py-2 text-sm font-semibold text-gray-700">
                        ${groupName.replace(/_/g, ' ')}
                        <label class="ml-4 font-normal text-xs">
                           <input type="checkbox" class="group-select-all-checkbox" data-group="${groupName}"> Select All in Group
                        </label>
                    </td>
                </tr>`;
            
            state.permissionGroups[groupName].forEach(permission => {
                tableHtml += `<tr><td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${permission}</td>`;
                state.roles.forEach(role => {
                    if (role.name.toLowerCase() !== 'admin') {
                        const hasPermission = role.permissions.includes(permission);
                        tableHtml += `
                            <td class="text-center">
                                <input type="checkbox" 
                                       class="permission-checkbox h-5 w-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500" 
                                       data-role-id="${role.id}" 
                                       data-permission="${permission}"
                                       data-group="${groupName}"
                                       ${hasPermission ? 'checked' : ''}>
                            </td>`;
                    }
                });
                tableHtml += '</tr>';
            });
        }
        tableHtml += '</tbody></table>';

        container.innerHTML = tableHtml;
        addEventListeners();
    }

    function addEventListeners() {
        document.querySelectorAll('.group-select-all-checkbox').forEach(headerCheckbox => {
            headerCheckbox.addEventListener('change', (e) => {
                const group = e.target.dataset.group;
                const isChecked = e.target.checked;
                document.querySelectorAll(`.permission-checkbox[data-group="${group}"]`).forEach(cb => {
                    cb.checked = isChecked;
                });
            });
        });
        saveBtn.addEventListener('click', saveChanges);
    }
    
    async function saveChanges() {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        
        const payload = {
            roles: []
        };

        state.roles.forEach(role => {
            if (role.name.toLowerCase() === 'admin') return;

            const rolePermissions = [];
            document.querySelectorAll(`.permission-checkbox[data-role-id="${role.id}"]:checked`).forEach(cb => {
                rolePermissions.push(cb.dataset.permission);
            });
            
            payload.roles.push({
                id: role.id,
                permissions: rolePermissions
            });
        });

        try {
            const response = await api.put('/admin/users/roles/bulk-update-permissions', payload);
            if (!response.ok) {
                 const errorData = await response.json();
                 throw new Error(errorData.msg || 'Failed to save changes.');
            }
            showToast('Roles and permissions updated successfully!');
            fetchData(); // Refresh data from server
        } catch (error) {
            console.error('Save failed:', error);
            showToast(error.message, true);
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Changes';
        }
    }

    fetchData();
});
