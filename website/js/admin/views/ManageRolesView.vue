<!--
 * FILENAME: website/js/admin/views/ManageRolesView.vue
 * UPDATED: Fully implemented to display roles.
-->
<template>
  <AdminLayout>
    <div class="space-y-6">
      <header><h1 class="text-3xl font-bold text-gray-800">Manage Roles & Permissions</h1></header>
      <div v-if="systemStore.isLoading" class="text-center py-10">Loading roles...</div>
      <div v-else-if="systemStore.error" class="bg-red-100 p-4 rounded text-red-700">{{ systemStore.error }}</div>
      <BaseDataTable v-else :columns="columns" :data="systemStore.roles">
          <template #cell(permissions)="{ value }">
              <div class="flex flex-wrap gap-1">
                  <span v-for="p in value" :key="p" class="bg-gray-200 text-gray-800 text-xs font-medium px-2 py-0.5 rounded-full">{{ p }}</span>
              </div>
          </template>
      </BaseDataTable>
    </div>
  </AdminLayout>
</template>
<script setup>
import { onMounted } from 'vue';
import { useAdminSystemStore } from '../../stores/adminSystem';
import AdminLayout from '../components/AdminLayout.vue';
import BaseDataTable from '../components/ui/BaseDataTable.vue';

const systemStore = useAdminSystemStore();
const columns = [ { key: 'name', label: 'Role Name' }, { key: 'permissions', label: 'Permissions' } ];
onMounted(() => { systemStore.fetchRoles(); });
</script>
