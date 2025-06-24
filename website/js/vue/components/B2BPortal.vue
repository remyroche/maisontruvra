<template>
  <div class="flex flex-col min-h-screen bg-gray-100">
    <B2BHeader />

    <main class="flex-grow container mx-auto p-4 sm:p-6 lg:p-8">
      <div class="space-y-8">
        <DashboardStats />
        <LoyaltyStatus />
        <InvoicesTable />
      </div>
    </main>

    <B2BFooter />
  </div>
</template>

<script setup>
import { defineAsyncComponent } from 'vue';
import B2BHeader from './layout/B2BHeader.vue';
import B2BFooter from './layout/B2BFooter.vue';

// Asynchronously load child components for better performance
const DashboardStats = defineAsyncComponent(() => 
  import('./b2b/DashboardStats.vue')
);
const LoyaltyStatus = defineAsyncComponent(() => 
  import('./b2b/LoyaltyStatus.vue')
);
const InvoicesTable = defineAsyncComponent(() => 
  import('./b2b/InvoicesTable.vue')
);
</script>

<style scoped>
/* Scoped styles for the B2B portal layout can be added here */
</style>
