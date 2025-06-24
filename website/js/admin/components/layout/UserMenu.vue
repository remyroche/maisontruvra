<!--
 * FILENAME: website/js/admin/components/layout/UserMenu.vue
 * DESCRIPTION: New dropdown menu for the header.
-->
<template>
    <div class="relative" ref="menuRef">
        <button @click="isOpen = !isOpen" class="flex items-center space-x-2">
            <span class="font-medium text-sm text-gray-700">{{ adminUserEmail }}</span>
             <svg class="h-5 w-5 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </button>
        <transition name="fade">
            <div v-if="isOpen" class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-xl z-20">
                <router-link to="/admin/profile" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">My Profile</router-link>
                <a @click="handleLogout" href="#" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">Logout</a>
            </div>
        </transition>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useAdminAuthStore } from '../../../stores/adminAuth';

const authStore = useAdminAuthStore();
const isOpen = ref(false);
const menuRef = ref(null);

const adminUserEmail = computed(() => authStore.adminUser?.email || 'Admin');

const handleLogout = async () => {
    await authStore.logout();
    window.location.href = '/admin/login';
};

const handleClickOutside = (event) => {
    if (menuRef.value && !menuRef.value.contains(event.target)) {
        isOpen.value = false;
    }
};

onMounted(() => document.addEventListener('mousedown', handleClickOutside));
onUnmounted(() => document.removeEventListener('mousedown', handleClickOutside));

</script>
<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease-in-out; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
