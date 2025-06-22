import { ProAPI } from './pro_api.js';
import { showNotification } from '../../js/common/ui.js';
import { t } from '../../js/i18n.js';


document.addEventListener('DOMContentLoaded', () => {
    loadReferralData();
    const generateCodeBtn = document.getElementById('generate-referral-code-btn');
    if (generateCodeBtn) {
        generateCodeBtn.addEventListener('click', handleGenerateCode);
    }
});

async function loadReferralData() {
    const container = document.getElementById('referral-codes-container');
    if (!container) return;

    try {
        const referrals = await proApi.get('/referrals');
        container.innerHTML = '';
        if (referrals.length > 0) {
            referrals.forEach(ref => {
                const codeEl = document.createElement('div');
                codeEl.className = 'p-4 bg-gray-100 rounded-lg shadow';
                codeEl.innerHTML = `<p class="font-bold text-lg">Your Code: <span class="font-mono text-blue-600">${ref.referral_code}</span></p>`;
                container.appendChild(codeEl);
            });
        } else {
            container.innerHTML = '<p>You have not generated any referral codes yet.</p>';
        }
    } catch (error) {
        console.error('Failed to load referral data:', error);
        showToast('Could not load your referral codes.', 'error');
    }
}

async function handleGenerateCode() {
    try {
        const newReferral = await proApi.post('/referrals/generate');
        if (newReferral) {
            showToast('New referral code generated!', 'success');
            loadReferralData(); // Refresh the list
        }
    } catch (error) {
        console.error('Failed to generate referral code:', error);
        showToast('Error generating new code.', 'error');
    }
}
