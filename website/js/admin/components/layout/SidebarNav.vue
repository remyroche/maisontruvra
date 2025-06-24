<!--
 * FILENAME: website/js/admin/components/layout/SidebarNav.vue
 * DESCRIPTION: Sidebar navigation.
 * UPDATED: Added links for all remaining admin panel features.
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
// ... (existing icon components)
const FingerPrintIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11c0 3.517-1.009 6.789-2.756 9.362A10.001 10.001 0 0112 21c5.523 0 10-4.477 10-10S17.523 1 12 1 2 5.477 2 11c0 1.907.538 3.69 1.474 5.234" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 11a3 3 0 100-6 3 3 0 000 6z" /></svg>`};
const IdentificationIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 012-2h4a2 2 0 012 2v1m-4 0h4" /></svg>`};
const ShieldCheckIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 20.944a11.955 11.955 0 019-2.944 11.955 11.955 0 019 2.944 12.02 12.02 0 00-2.382-9.008z" /></svg>`};
const LockClosedIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>`};
const QrcodeIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h-1m-1-6v.01M12 12v.01M12 8v.01M12 16v.01M12 20v1M4 12H3m1-6V5m12 1v-1m-1 6h.01M12 12h.01M12 8h.01M12 16h.01M12 20h.01M4 12v.01M4 8v.01M4 16v.01M4 20v.01M8 4H7m1 12H7m1-6H7m1-6H7m6-1h.01M16 4h.01M8 20h.01M16 20h.01" /></svg>`};
const MailIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>`};
const ArchiveIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" /></svg>`};
const PhotographIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>`};
const TerminalIcon = { template: `<svg fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4" /></svg>`};

const navStructure = [
    { title: 'Main', links: [ 
        { name: 'Dashboard', path: '/admin', icon: HomeIcon },
        { name: 'Point of Sale', path: '/admin/pos', icon: QrcodeIcon } 
    ] },
    { title: 'E-commerce', links: [
        { name: 'Orders', path: '/admin/orders', icon: ClipboardListIcon },
        { name: 'Invoices', path: '/admin/invoices', icon: DocumentDownloadIcon },
        { name: 'Quotes', path: '/admin/quotes', icon: DocumentDownloadIcon },
        { name: 'Products', path: '/admin/products', icon: ShoppingBagIcon },
        { name: 'Inventory', path: '/admin/inventory', icon: ArchiveIcon },
        { name: 'Categories', path: '/admin/categories', icon: TagIcon },
        { name: 'Collections', path: '/admin/collections', icon: CollectionIcon },
        { name: 'Reviews', path: '/admin/reviews', icon: StarIcon },
        { name: 'Passports', path: '/admin/passports', icon: IdentificationIcon },
    ]},
     { title: 'Marketing', links: [
        { name: 'Blog', path: '/admin/blog', icon: NewspaperIcon },
        { name: 'Newsletter', path: '/admin/newsletter', icon: MailIcon },
        { name: 'Loyalty', path: '/admin/loyalty', icon: GiftIcon },
    ]},
    { title: 'Customers', links: [
        { name: 'Users', path: '/admin/users', icon: UsersIcon },
        { name: 'B2B Accounts', path: '/admin/b2b', icon: OfficeBuildingIcon },
        { name: 'Roles', path: '/admin/roles', icon: ShieldCheckIcon },
    ]},
    { title: 'System', links: [
        { name: 'My Profile', path: '/admin/profile', icon: UserCircleIcon },
        { name: 'Setup MFA', path: '/admin/setup-mfa', icon: LockClosedIcon },
        { name: 'Active Sessions', path: '/admin/sessions', icon: TerminalIcon },
        { name: 'Assets', path: '/admin/assets', icon: PhotographIcon },
        { name: 'Site Settings', path: '/admin/settings', icon: CogIcon },
        { name: 'Audit Log', path: '/admin/audit-log', icon: FingerPrintIcon },
    ]}
];
</script>
