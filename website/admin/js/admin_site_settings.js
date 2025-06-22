import { AdminAPI } from './admin_api.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('site-settings-form');
    if (!form) return;

    const maintenanceModeCheck = document.getElementById('maintenance-mode');
    const taxRateInput = document.getElementById('tax-rate');

    const loadSettings = async () => {
        try {
            const settings = await AdminAPI.getSiteSettings();
            maintenanceModeCheck.checked = settings.maintenance_mode === 'true';
            taxRateInput.value = settings.tax_rate || '0';
        } catch (error) {
            showToast('Failed to load site settings.', 'error');
        }
    };

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const settingsToSave = {
            maintenance_mode: maintenanceModeCheck.checked,
            tax_rate: taxRateInput.value
        };

        try {
            await AdminAPI.updateSiteSettings(settingsToSave);
            showToast('Settings saved successfully!', 'success');
        } catch (error) {
            showToast('Failed to save settings.', 'error');
        }
    });

    loadSettings();
});
