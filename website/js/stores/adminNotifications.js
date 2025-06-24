/*
 * FILENAME: website/js/stores/adminNotifications.js
 * DESCRIPTION: New Pinia store to manage a global notification system for the admin panel.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAdminNotificationStore = defineStore('adminNotifications', () => {
  const notifications = ref([]);

  const addNotification = (notification) => {
    const id = Date.now() + Math.random();
    notifications.value.push({ ...notification, id });

    // Automatically remove after a delay
    setTimeout(() => {
      removeNotification(id);
    }, notification.duration || 5000);
  };

  const removeNotification = (id) => {
    notifications.value = notifications.value.filter(n => n.id !== id);
  };

  return { notifications, addNotification, removeNotification };
});
