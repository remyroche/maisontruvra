<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-800 text-white flex-shrink-0">
      <div class="p-4 text-lg font-semibold">Admin Panel</div>
      <nav>
        <ul>
          <li v-for="item in navItems" :key="item.name">
            <router-link :to="item.path" class="flex items-center p-4 hover:bg-gray-700">
              <component :is="item.icon" class="h-6 w-6 mr-3" />
              <span>{{ item.name }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white shadow p-4 flex justify-between items-center">
        <h1 class="text-xl font-bold">Dashboard</h1>
        <div>
          <router-link to="/admin/profile" class="mr-4">Profile</router-link>
          <button @click="logout" class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded">
            Logout
          </button>
        </div>
      </header>
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAdminAuthStore } from '@/stores/adminAuth';
import {
  ChartBarIcon,
  UsersIcon,
  ShoppingBagIcon,
  TagIcon,
  CubeIcon,
  CollectionIcon,
  TruckIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  ChatAlt2Icon,
  NewspaperIcon,
  SparklesIcon,
  CogIcon,
  ShieldCheckIcon,
  UserGroupIcon,
  DocumentReportIcon,
  ClockIcon,
  KeyIcon,
  ViewGridIcon,
  QrcodeIcon,
  TerminalIcon,
  GiftIcon,
  TrashIcon, // Added TrashIcon for the Recycling Bin
} from '@heroicons/vue/outline';

const router = useRouter();
const authStore = useAdminAuthStore();

const navItems = [
  { name: 'Dashboard', path: '/admin/dashboard', icon: ChartBarIcon },
  { name: 'Users', path: '/admin/manage-users', icon: UsersIcon },
  { name: 'B2B', path: '/admin/manage-b2b', icon: UserGroupIcon },
  { name: 'Orders', path: '/admin/manage-orders', icon: ShoppingBagIcon },
  { name: 'Products', path: '/admin/manage-products', icon: CubeIcon },
  { name: 'Categories', path: '/admin/manage-categories', icon: TagIcon },
  { name: 'Collections', path: '/admin/manage-collections', icon: CollectionIcon },
  { name: 'Inventory', path: '/admin/manage-inventory', icon: ViewGridIcon },
  { name: 'Delivery', path: '/admin/manage-delivery', icon: TruckIcon },
  { name: 'Discounts', path: '/admin/manage-discounts', icon: CurrencyDollarIcon },
  { name: 'Invoices', path: '/admin/manage-invoices', icon: DocumentTextIcon },
  { name: 'Quotes', path: '/admin/manage-quotes', icon: ChatAlt2Icon },
  { name: 'Reviews', path: '/admin/manage-reviews', icon: ChatAlt2Icon },
  { name: 'Blog', path: '/admin/manage-blog', icon: NewspaperIcon },
  { name: 'Loyalty', path: '/admin/manage-loyalty', icon: SparklesIcon },
  { name: 'Newsletter', path: '/admin/manage-newsletter', icon: GiftIcon },
  { name: 'Assets', path: '/admin/manage-assets', icon: DocumentReportIcon },
  { name: 'Passports', path: '/admin/view-passports', icon: QrcodeIcon },
  { name: 'POS', path: '/admin/manage-pos', icon: TerminalIcon },
  { name: 'Sessions', path: '/admin/manage-sessions', icon: ClockIcon },
  { name: 'Roles', path: '/admin/manage-roles', icon: KeyIcon },
  { name: 'Site Settings', path: '/admin/site-settings', icon: CogIcon },
  { name: 'Audit Log', path: '/admin/audit-log', icon: ShieldCheckIcon },
  { name: 'Recycling Bin', path: '/admin/recycling-bin', icon: TrashIcon }, // Added new navigation item
];

const logout = async () => {
  await authStore.logout();
  router.push('/admin/login');
};
</script>

<style scoped>
/* Add any specific styles for the admin dashboard here */
.router-link-active {
  @apply bg-gray-700;
}
</style>
