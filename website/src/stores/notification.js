/**
 * @file /src/stores/notification.js
 * @description A generic Pinia store for managing global notifications.
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([]);

  const showNotification = (message, type = 'info', title = null, duration = 5000) => {
    const id = Date.now() + Math.random();
    const notification = {
      id,
      message,
      type,
      title,
      duration
    };
    
    notifications.value.push(notification);

    setTimeout(() => {
      removeNotification(id);
    }, duration);
  };

  const removeNotification = (id) => {
    notifications.value = notifications.value.filter(n => n.id !== id);
  };

  return { notifications, showNotification, removeNotification };
});