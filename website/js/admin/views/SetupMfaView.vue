<!--
 * FILENAME: website/js/admin/views/SetupMfaView.vue
 * UPDATED: Implemented with placeholder for QR code and setup flow.
-->
<template>
  <AdminLayout>
    <div class="space-y-6 max-w-lg mx-auto">
      <header><h1 class="text-3xl font-bold text-gray-800">Setup Multi-Factor Authentication</h1></header>
      <div class="bg-white p-8 rounded-lg shadow-md text-center">
        <h2 class="text-xl font-bold mb-4">Scan this QR Code</h2>
        <div class="bg-gray-200 h-48 w-48 mx-auto flex items-center justify-center">
            <p class="text-gray-500">QR Code Here</p>
        </div>
        <p class="mt-4 text-sm text-gray-600">Scan the code with your authenticator app, then enter the code below to verify.</p>
         <div class="mt-4">
            <label class="block text-sm font-medium">Verification Code</label>
            <input type="text" class="mt-1 block w-full max-w-xs mx-auto border-gray-300 rounded-md shadow-sm">
        </div>
        <button class="mt-4 bg-indigo-600 text-white font-bold py-2 px-4 rounded">Enable MFA</button>
      </div>
    </div>
  </AdminLayout>
</template>
<script setup>
import AdminLayout from '../components/AdminLayout.vue';
</script>
