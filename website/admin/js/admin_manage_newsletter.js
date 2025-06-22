// website/source/admin/js/admin_manage_newsletter.js

import { checkAdminAuth, loadAdminHeader } from './admin_common.js';
import { showToast } from './admin_ui.js';
import { config } from './admin_config.js';
import { AdminApi } from './admin_api.js';


document.addEventListener('DOMContentLoaded', async function() {
    // --- AUTH & INITIALIZATION ---
    await checkAdminAuth();
    const api = new AdminApi(config.api_url, localStorage.getItem('admin_token'));
    await loadAdminHeader();

    // --- DOM ELEMENT SELECTION ---
    // This section is for the newsletter composer UI
    const composerSection = document.getElementById('composer-section');
    if (composerSection) {
        const quill = new Quill('#editor', {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    ['link', { 'list': 'ordered' }, { 'list': 'bullet' }],
                    [{ 'color': [] }, { 'background': [] }],
                    ['clean']
                ]
            },
            placeholder: 'Compose your amazing newsletter here...',
        });

        const userTypeFilters = document.querySelectorAll('.user-type-filter');
        const b2cTiersContainer = document.getElementById('b2c-tiers-container');
        const b2bTiersContainer = document.getElementById('b2b-tiers-container');
        const fetchRecipientsBtn = document.getElementById('fetch-recipients-btn');
        const recipientListContainer = document.getElementById('recipient-list');
        const recipientCountEl = document.getElementById('recipient-count');
        const selectAllCheckbox = document.getElementById('select-all-recipients');
        const sendNewsletterBtn = document.getElementById('send-newsletter-btn');
        const subjectInput = document.getElementById('newsletter-subject');

        let state = {
            allTiers: { b2c: [], b2b: [] },
            currentRecipients: [],
            currentUserType: null,
        };
        
        async function loadTiers() {
            try {
                const response = await api.get('/admin/newsletter/tiers');
                if (!response.ok) throw new Error('Failed to load tiers');
                const data = await response.json();
                
                state.allTiers = data;
                populateTierCheckboxes('b2c', data.b2c, b2cTiersContainer);
                populateTierCheckboxes('b2b', data.b2b, b2bTiersContainer);
            } catch (error) {
                console.error('Error fetching tiers:', error);
                showToast('Could not load user tiers. Please refresh.', true);
            }
        }

        function populateTierCheckboxes(type, tiers, container) {
            container.innerHTML = tiers.length > 0
                ? tiers.map(tier => `
                    <label class="flex items-center font-normal text-sm">
                        <input type="checkbox" class="tier-checkbox h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500" data-type="${type}" value="${tier.id}">
                        <span class="ml-2 text-gray-700">${tier.name}</span>
                    </label>
                `).join('')
                : '<p class="text-xs text-gray-500">No tiers found for this user type.</p>';
        }

        function handleUserTypeChange() {
            state.currentUserType = document.querySelector('input[name="user_type"]:checked')?.value;
            if (state.currentUserType) {
                b2cTiersContainer.classList.toggle('hidden', state.currentUserType !== 'b2c');
                b2bTiersContainer.classList.toggle('hidden', state.currentUserType !== 'b2b');
                fetchRecipientsBtn.disabled = false;
            } else {
                fetchRecipientsBtn.disabled = true;
            }
        }
        
        async function fetchRecipients() {
            if (!state.currentUserType) {
                showToast('Please select a user type first.', true);
                return;
            }

            const tierCheckboxes = document.querySelectorAll(`#${state.currentUserType}-tiers-container .tier-checkbox:checked`);
            const tier_ids = Array.from(tierCheckboxes).map(cb => cb.value).join(',');
            
            setLoadingState(true, fetchRecipientsBtn, 'Fetching...');
            try {
                const response = await api.get(`/admin/newsletter/recipients?user_type=${state.currentUserType}&tier_ids=${tier_ids}`);
                if(!response.ok) throw new Error('Could not fetch recipients.');
                const recipients = await response.json();
                state.currentRecipients = recipients;
                renderRecipientList();
            } catch (error) {
                console.error('Error fetching recipients:', error);
                recipientListContainer.innerHTML = '<p class="text-red-500 text-center p-4">Failed to load recipients.</p>';
                recipientCountEl.textContent = '';
            } finally {
                setLoadingState(false, fetchRecipientsBtn, 'Fetch Recipients');
            }
        }

        function renderRecipientList() {
            const count = state.currentRecipients.length;
            recipientCountEl.textContent = `${count} recipient${count === 1 ? '' : 's'} found.`;
            selectAllCheckbox.checked = count > 0;

            if (count === 0) {
                recipientListContainer.innerHTML = '<p class="text-gray-500 text-center p-4">No recipients match the criteria.</p>';
                return;
            }
            
            recipientListContainer.innerHTML = state.currentRecipients.map(r => `
                <div class="flex items-center p-1 rounded hover:bg-gray-100">
                     <input type="checkbox" class="recipient-checkbox h-4 w-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500" data-id="${r.id}" data-type="${state.currentUserType}" checked>
                     <span class="ml-3 text-sm text-gray-800">${r.email}</span>
                </div>
            `).join('');
        }

        function handleSelectAll() {
            const checkboxes = document.querySelectorAll('.recipient-checkbox');
            checkboxes.forEach(checkbox => checkbox.checked = selectAllCheckbox.checked);
        }
        
        async function sendNewsletter() {
            const subject = subjectInput.value.trim();
            const content = quill.root.innerHTML;
            const selectedRecipients = Array.from(document.querySelectorAll('.recipient-checkbox:checked'))
                .map(cb => ({
                    id: parseInt(cb.dataset.id, 10),
                    type: cb.dataset.type
                }));

            if (!subject) {
                return showToast('Please provide a subject.', true);
            }
            if (quill.getLength() <= 1) { // Quill adds a newline by default
                return showToast('Please add content to the newsletter.', true);
            }
            if (selectedRecipients.length === 0) {
                return showToast('Please select at least one recipient.', true);
            }

            // Consider replacing `confirm` with a custom modal from `admin_ui.js` for better UX
            if (!confirm(`You are about to send this newsletter to ${selectedRecipients.length} recipients. Are you sure?`)) {
                return;
            }
            
            setSendingState(true);
            try {
                const payload = { subject, content, recipients: selectedRecipients };
                const response = await api.post('/admin/newsletter/send', payload);
                
                if (response.status !== 202) {
                    const err = await response.json();
                    throw new Error(err.error || 'Failed to send newsletter');
                }
                
                showToast('Newsletter is being sent in the background!');
                resetForm();
            } catch (error) {
                console.error('Error sending newsletter:', error);
                showToast(`Error: ${error.message}`, true);
            } finally {
                setSendingState(false);
            }
        }
        
        function resetForm() {
            subjectInput.value = '';
            quill.setText('');
            recipientListContainer.innerHTML = '<p class="text-gray-400 text-center p-4">Please select filters and fetch recipients.</p>';
            recipientCountEl.textContent = '';
            selectAllCheckbox.checked = false;
            state.currentRecipients = [];
        }
        
        function setLoadingState(isLoading, button, loadingText) {
            button.disabled = isLoading;
            const originalText = button.dataset.originalText || button.textContent;
            if (isLoading) {
                 button.dataset.originalText = originalText;
                 button.textContent = loadingText;
            } else {
                 button.textContent = originalText;
            }
        }

        function setSendingState(isSending) {
            sendNewsletterBtn.disabled = isSending;
            const svg = sendNewsletterBtn.querySelector('svg');
            if (svg) svg.classList.toggle('hidden', isSending);
            
            const originalText = sendNewsletterBtn.dataset.originalText || 'Send Newsletter';
             if (isSending) {
                 sendNewsletterBtn.dataset.originalText = originalText;
                 sendNewsletterBtn.innerHTML = `
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Sending...
                 `;
            } else {
                 sendNewsletterBtn.innerHTML = `
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path></svg>
                    ${originalText}
                 `;
            }
        }

        userTypeFilters.forEach(radio => radio.addEventListener('change', handleUserTypeChange));
        fetchRecipientsBtn.addEventListener('click', fetchRecipients);
        selectAllCheckbox.addEventListener('change', handleSelectAll);
        sendNewsletterBtn.addEventListener('click', sendNewsletter);
        fetchRecipientsBtn.disabled = true;
        loadTiers();
    }
    
    // This section handles the logic for the subscriber list view
    const subscribersSection = document.getElementById('subscribers-section');
    if (subscribersSection) {
        const b2cTableBody = document.getElementById('subscribers-table-body-b2c');
        const b2bTableBody = document.getElementById('subscribers-table-body-b2b');

        function formatDate(dateString) {
            if (!dateString) return 'N/A';
            const options = { year: 'numeric', month: 'long', day: 'numeric' };
            return new Date(dateString).toLocaleDateString('fr-FR', options);
        }

        function createSubscriberRow(subscriber) {
            return `
                <tr>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        <p class="text-gray-900 whitespace-no-wrap">${subscriber.email}</p>
                    </td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        <p class="text-gray-900 whitespace-no-wrap">${formatDate(subscriber.subscribed_at)}</p>
                    </td>
                    <td class="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                        <span class="relative inline-block px-3 py-1 font-semibold ${subscriber.status === 'active' ? 'text-green-900' : 'text-red-900'} leading-tight">
                            <span aria-hidden class="absolute inset-0 ${subscriber.status === 'active' ? 'bg-green-200' : 'bg-red-200'} opacity-50 rounded-full"></span>
                            <span class="relative">${subscriber.status}</span>
                        </span>
                    </td>
                </tr>
            `;
        }

        async function loadSubscribers(audience, tableBody) {
             try {
                // NOTE: Assumes an endpoint '/admin/newsletter/subscribers?audience=' exists.
                // You may need to create this endpoint in your backend.
                const response = await api.get(`/admin/newsletter/subscribers?audience=${audience}`);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const subscribers = await response.json();

                if (subscribers && subscribers.length > 0) {
                    tableBody.innerHTML = subscribers.map(createSubscriberRow).join('');
                } else {
                    tableBody.innerHTML = '<tr><td colspan="3" class="text-center p-5">Aucun abonné trouvé.</td></tr>';
                }
            } catch (error) {
                console.error(`Error loading ${audience} subscribers:`, error);
                tableBody.innerHTML = '<tr><td colspan="3" class="text-center p-5 text-red-500">Impossible de charger les abonnés.</td></tr>';
            }
        }

        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                const tab = button.dataset.tab;
                
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.add('hidden');
                });
                document.getElementById(`subscribers-list-${tab}`).classList.remove('hidden');
            });
        });

        // Initial load
        if (b2cTableBody) loadSubscribers('b2c', b2cTableBody);
        if (b2bTableBody) loadSubscribers('b2b', b2bTableBody);
    }
});
