// website/source/js/common/ui.js

/**
 * Creates and displays a toast notification on the screen.
 * @param {string} message The message to display.
 * @param {'success' | 'error' | 'info'} type The type of toast, for styling.
 * @param {number} duration The duration in milliseconds for the toast to be visible.
 */
export function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-5 right-5 z-50 space-y-2';
        document.body.appendChild(toastContainer);
    }

    // Create the toast element
    const toast = document.createElement('div');

    // Base classes
    let classes = 'max-w-xs p-4 text-sm text-white rounded-lg shadow-lg transition-all transform';

    // Type-specific classes
    if (type === 'success') {
        classes += ' bg-green-500';
    } else if (type === 'error') {
        classes += ' bg-red-500';
    } else {
        classes += ' bg-blue-500';
    }

    toast.className = classes;
    toast.textContent = message;

    // Add animation for entry
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';

    // Append to container
    toastContainer.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    });

    // Set timeout to remove the toast
    setTimeout(() => {
        // Animate out
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        toast.addEventListener('transitionend', () => {
            toast.remove();
        });
    }, duration);
}

/**
 * Creates and shows a modal dialog.
 * Replaces native `confirm` and `alert`.
 * @param {string} title The title of the modal.
 * @param {string} content The HTML content of the modal body.
 * @param {function} onConfirm A callback function to execute if the user confirms.
 */
export function showModal(title, content, onConfirm) {
    // Remove existing modal first
    const existingModal = document.getElementById('app-modal');
    if (existingModal) existingModal.remove();

    const modalBackdrop = document.createElement('div');
    modalBackdrop.id = 'app-modal';
    modalBackdrop.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';

    modalBackdrop.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
            <h3 class="text-lg font-bold mb-4">${title}</h3>
            <div class="mb-6">${content}</div>
            <div class="flex justify-end space-x-4">
                <button id="modal-cancel" class="px-4 py-2 bg-gray-200 rounded-lg hover:bg-gray-300">Cancel</button>
                <button id="modal-confirm" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">Confirm</button>
            </div>
        </div>
    `;

    document.body.appendChild(modalBackdrop);

    const confirmButton = document.getElementById('modal-confirm');
    const cancelButton = document.getElementById('modal-cancel');

    const closeModal = () => modalBackdrop.remove();

    cancelButton.addEventListener('click', closeModal);

    if (onConfirm && typeof onConfirm === 'function') {
        confirmButton.addEventListener('click', () => {
            onConfirm();
            closeModal();
        });
    } else {
        // If no confirm action, it's just an alert, so the button just closes it
        confirmButton.textContent = "OK";
        confirmButton.addEventListener('click', closeModal);
        cancelButton.style.display = 'none'; // Hide cancel for alert-style modals
    }
}