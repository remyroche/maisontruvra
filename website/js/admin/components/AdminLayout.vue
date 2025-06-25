<template>
  <div class="flex h-screen bg-gray-100">
    <SidebarNav />
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="flex justify-end items-center p-4 bg-white border-b">
        <UserMenu />
      </header>
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-6">
        <router-view />
      </main>
    </div>
    
    <!-- Global Re-authentication Modal -->
    <ReAuthModal 
        :is-open="authStore.isReAuthRequired"
        @submit="handleReAuthSubmit"
        @logout="handleReAuthLogout"
    />
  </div>
</template>

<script setup>
import SidebarNav from './layout/SidebarNav.vue';
import UserMenu from './layout/UserMenu.vue';
import ReAuthModal from './ReAuthModal.vue';
import { useAdminAuthStore } from '@/js/stores/adminAuth';

const authStore = useAdminAuthStore();

const handleReAuthSubmit = async (password) => {
    await authStore.reauthenticateAndRetry(password);
};

const handleReAuthLogout = () => {
    authStore.logout();
};
</script>
