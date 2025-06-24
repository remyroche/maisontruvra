<!--
 * FILENAME: website/js/admin/views/AdminProfileView.vue
 * DESCRIPTION: View for the logged-in admin to manage their own profile.
-->
<template>
    <AdminLayout>
        <div class="space-y-8 max-w-4xl mx-auto">
             <header>
                <h1 class="text-3xl font-bold text-gray-800">My Profile</h1>
            </header>

            <!-- Update Profile Form -->
            <form @submit.prevent="handleProfileUpdate" class="bg-white p-8 rounded-lg shadow-md space-y-4">
                <h2 class="text-xl font-bold text-gray-700">Personal Information</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                     <div>
                        <label class="block text-sm font-medium">First Name</label>
                        <input type="text" v-model="profileForm.first_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                    </div>
                     <div>
                        <label class="block text-sm font-medium">Last Name</label>
                        <input type="text" v-model="profileForm.last_name" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                    </div>
                </div>
                <div class="pt-4 flex justify-end">
                    <button type="submit" :disabled="profileStore.isLoading" class="bg-indigo-600 text-white font-bold py-2 px-4 rounded">Update Profile</button>
                </div>
            </form>

             <!-- Change Password Form -->
            <form @submit.prevent="handlePasswordChange" class="bg-white p-8 rounded-lg shadow-md space-y-4">
                <h2 class="text-xl font-bold text-gray-700">Change Password</h2>
                 <div>
                    <label class="block text-sm font-medium">Current Password</label>
                    <input type="password" v-model="passwordForm.current_password" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                </div>
                 <div>
                    <label class="block text-sm font-medium">New Password</label>
                    <input type="password" v-model="passwordForm.new_password" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                </div>
                 <div>
                    <label class="block text-sm font-medium">Confirm New Password</label>
                    <input type="password" v-model="passwordForm.confirm_password" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                </div>
                <div class="pt-4 flex justify-end">
                    <button type="submit" :disabled="profileStore.isLoading" class="bg-indigo-600 text-white font-bold py-2 px-4 rounded">Change Password</button>
                </div>
            </form>
        </div>
    </AdminLayout>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useAdminAuthStore } from '../../stores/adminAuth';
import { useAdminProfileStore } from '../../stores/adminProfile';
import { useAdminNotificationStore } from '../../stores/adminNotifications';
import AdminLayout from '../components/AdminLayout.vue';

const authStore = useAdminAuthStore();
const profileStore = useAdminProfileStore();
const notificationStore = useAdminNotificationStore();

const profileForm = ref({ first_name: '', last_name: '' });
const passwordForm = ref({ current_password: '', new_password: '', confirm_password: '' });

watch(() => authStore.adminUser, (newUser) => {
    if(newUser) {
        profileForm.value.first_name = newUser.first_name;
        profileForm.value.last_name = newUser.last_name;
    }
}, { immediate: true });

const handleProfileUpdate = async () => {
    const success = await profileStore.updateProfile(profileForm.value);
    if(success) {
        notificationStore.addNotification({ type: 'success', title: 'Profile Updated' });
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Update Failed', message: profileStore.error });
    }
};

const handlePasswordChange = async () => {
    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
        notificationStore.addNotification({ type: 'error', title: 'Error', message: 'New passwords do not match.' });
        return;
    }
    const success = await profileStore.changePassword(passwordForm.value);
     if(success) {
        notificationStore.addNotification({ type: 'success', title: 'Password Changed Successfully' });
        passwordForm.value = { current_password: '', new_password: '', confirm_password: '' }; // Clear form
    } else {
        notificationStore.addNotification({ type: 'error', title: 'Password Change Failed', message: profileStore.error });
    }
};

</script>
