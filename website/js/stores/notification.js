// website/source/js/stores/notification.js
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notification', () => {
    // STATE
    const message = ref('');
    const type = ref('success'); // 'success' or 'error'
    const isVisible = ref(false);

    // ACTIONS
    function showNotification(newMessage, newType = 'success', duration = 4000) {
        message.value = newMessage;
        type.value = newType;
        isVisible.value = true;

        setTimeout(() => {
            isVisible.value = false;
        }, duration);
    }

    function hideNotification() {
        isVisible.value = false;
    }

    return { message, type, isVisible, showNotification, hideNotification };
});
