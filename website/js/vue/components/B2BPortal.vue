// website/source/js/vue/components/B2BPortal.vue
<template>
    <div>
        <DashboardStats />
        <LoyaltyStatus />
        <InvoicesTable />
    </div>
</template>

<script setup>
import { defineAsyncComponent } from 'vue';

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
