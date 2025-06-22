<template>
    <transition
        enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
        enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
        leave-active-class="transition ease-in duration-100"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0">
        <div v-if="notification.isVisible" class="fixed top-5 right-5 w-full max-w-sm z-50">
            <div v-bind:class="notificationClasses" class="rounded-lg shadow-lg p-4">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg v-if="notification.type === 'success'" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                         <svg v-if="notification.type === 'error'" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm font-medium text-white">
                            {{ notification.message }}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </transition>
</template>

<script setup>
import { computed } from 'vue';
import { useNotificationStore } from '../../stores/notification.js';

const notification = useNotificationStore();

const notificationClasses = computed(() => {
    return {
        'bg-green-600': notification.type === 'success',
        'bg-red-600': notification.type === 'error',
    };
});
</script>
