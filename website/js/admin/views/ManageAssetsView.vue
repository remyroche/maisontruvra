<!--
 * FILENAME: website/js/admin/views/ManageAssetsView.vue
 * UPDATED: Implemented with a placeholder for asset upload functionality.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header><h1 class="text-3xl font-bold text-gray-800">Manage Assets</h1></header>
      <div class="bg-white p-8 rounded-lg shadow-md">
        <h2 class="text-xl font-bold mb-4">Upload New Asset</h2>
        <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <p class="text-gray-500">Drag & drop files here or click to select files.</p>
            <p class="text-xs text-gray-400 mt-2">Asset upload functionality is pending implementation.</p>
        </div>
      </div>
    </div>
  </AdminLayout>
</template>
<script setup>
import AdminLayout from '../components/AdminLayout.vue';
</script>
