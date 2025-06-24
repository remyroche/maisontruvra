<!--
 * FILENAME: website/js/admin/components/layout/SidebarNav.vue
 * DESCRIPTION: New dynamic, data-driven, collapsible sidebar navigation.
-->
<template>
  <nav class="flex-1 px-2 py-4 space-y-2">
    <div v-for="section in navStructure" :key="section.title">
      <h3 class="px-4 pt-4 pb-2 text-xs text-gray-400 font-bold uppercase tracking-wider">{{ section.title }}</h3>
      <ul>
        <li v-for="link in section.links" :key="link.name">
          <router-link :to="link.path" class="flex items-center px-4 py-2 text-gray-300 hover:bg-gray-700 hover:text-white rounded-md text-sm" active-class="bg-gray-900 text-white">
             <component :is="link.icon" class="h-5 w-5 mr-3" />
            {{ link.name }}
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
// In a real app, you might move these icons to their own files
const HomeIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1V10a1 1 0 00-1-1H7a1 1 0 00-1 1v10a1 1 0 001 1h2z"></path></svg>` };
const UsersIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M15 21a6 6 0 00-9-5.197M15 11a4 4 0 110-8 4 4 0 010 8z" /></svg>` };
const ShoppingBagIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" /></svg>` };
const ClipboardListIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>` };
const TagIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5a2 2 0 012 2v5a2 2 0 01-2 2H7a2 2 0 01-2-2V5a2 2 0 012-2zm0 0l7 7m-7-7l-7 7" /></svg>`};
const CollectionIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>`};
const CogIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.096 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>`};

const navStructure = [
    { title: 'Main', links: [ { name: 'Dashboard', path: '/admin', icon: HomeIcon } ] },
    { title: 'E-commerce', links: [
        { name: 'Orders', path: '/admin/orders', icon: ClipboardListIcon },
        { name: 'Products', path: '/admin/products', icon: ShoppingBagIcon },
        { name: 'Categories', path: '/admin/categories', icon: TagIcon },
        { name: 'Collections', path: '/admin/collections', icon: CollectionIcon },
    ]},
    { title: 'System', links: [
        { name: 'Users', path: '/admin/users', icon: UsersIcon },
        { name: 'Settings', path: '/admin/settings', icon: CogIcon }
    ]}
];
</script>
