import { checkAdminAuth, loadAdminHeader } from './admin_common.js';
import { AdminApi } from './admin_api.js';
import { config } from './admin_config.js';
import { showToast } from './admin_ui.js';

document.addEventListener('DOMContentLoaded', async () => {
    // Standard auth and header loading
    await checkAdminAuth();
    await loadAdminHeader();
    const api = new AdminApi(config.api_url, localStorage.getItem('admin_token'));

    // --- DOM Element Selection ---
    // Profile Info
    const profileNameEl = document.getElementById('profile-name');
    const profileEmailEl = document.getElementById('profile-email');
    const profileRolesEl = document.getElementById('profile-roles');

    // MFA Elements
    const mfaStatusContainer = document.getElementById('mfa-status-container');
    const mfaSetupContainer = document.getElementById('mfa-setup-container');
    const mfaQrCodeImg = document.getElementById('mfa-qr-code');
    const mfaVerifyForm = document.getElementById('mfa-verify-form');
    const mfaVerifyCodeInput = document.getElementById('mfa-verify-code');
    
    // State
    let mfaSecret = ''; // Temporarily store the secret during setup

    // --- Functions ---

    /**
     * Fetches the current user's profile data and MFA status.
     */
    async function loadProfile() {
        try {
            // This endpoint needs to be created, it should return the logged-in user's details.
            const user = await api.get('/admin/auth/profile'); 
            
            profileNameEl.textContent = `${user.first_name || ''} ${user.last_name || ''}`;
            profileEmailEl.textContent = user.email;
            profileRolesEl.innerHTML = user.roles.map(role => `<span class="bg-gray-200 text-gray-800 text-xs font-medium mr-2 px-2.5 py-0.5 rounded">${role}</span>`).join('');

            renderMfaStatus(user.mfa_enabled);

        } catch (error) {
            showToast('Could not load profile data.', true);
        }
    }

    /**
     * Renders the MFA status and the appropriate action button.
     * @param {boolean} isEnabled - The current MFA status of the user.
     */
    function renderMfaStatus(isEnabled) {
        if (isEnabled) {
            mfaStatusContainer.innerHTML = `
                <div class="flex items-center justify-between">
                    <p class="text-green-600 font-medium">Two-Factor Authentication is enabled.</p>
                    <button id="disable-mfa-btn" class="text-sm bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700">Disable MFA</button>
                </div>
            `;
        } else {
            mfaStatusContainer.innerHTML = `
                <div class="flex items-center justify-between">
                    <p>Two-Factor Authentication is not enabled. We highly recommend enabling it.</p>
                    <button id="enable-mfa-btn" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Enable MFA</button>
                </div>
            `;
        }
    }

    // --- Event Listeners ---

    // Use event delegation for dynamically created buttons
    mfaStatusContainer.addEventListener('click', async (e) => {
        if (e.target.id === 'enable-mfa-btn') {
            try {
                e.target.disabled = true;
                e.target.textContent = 'Generating...';
                const data = await api.setupMfa(); // Calls GET /admin/auth/mfa/setup
                mfaSecret = data.secret;
                mfaQrCodeImg.src = `data:image/png;base64,${data.qr_code}`;
                mfaSetupContainer.classList.remove('hidden');
                e.target.textContent = 'Enable MFA';
                e.target.disabled = false;
            } catch (error) {
                showToast('Could not start MFA setup.', true);
            }
        }

        if (e.target.id === 'disable-mfa-btn') {
            if (confirm('Are you sure you want to disable Two-Factor Authentication?')) {
                // You would need to create a 'disable' endpoint for this.
                // await api.disableMfa(); 
                showToast('MFA Disabled (Endpoint not implemented).');
                // renderMfaStatus(false); // Update UI
            }
        }
    });

    mfaVerifyForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const mfa_code = mfaVerifyCodeInput.value;
        const submitBtn = e.target.querySelector('button');
        submitBtn.disabled = true;

        try {
            await api.verifyMfaSetup({ secret: mfaSecret, mfa_code }); // Calls POST /admin/auth/mfa/verify-setup
            showToast('MFA enabled successfully!');
            mfaSetupContainer.classList.add('hidden');
            renderMfaStatus(true); // Refresh status
        } catch (error) {
            showToast('Invalid code. Please try again.', true);
        } finally {
            submitBtn.disabled = false;
        }
    });

    // Initial Load
    loadProfile();
});
