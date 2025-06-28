<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">Admin Dashboard</h1>
    <!-- Stats Cards -->
    <DashboardStats />

    <div class="mt-8">
      <h2 class="text-xl font-semibold text-gray-800 mb-4">Recent Activity</h2>
      <!-- Placeholder for recent orders/users tables -->
       <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
           <div class="bg-white p-4 rounded-lg shadow">
               <h3 class="font-semibold">Recent Orders</h3>
               <!-- Order list would go here -->
           </div>
           <div class="bg-white p-4 rounded-lg shadow">
                <h3 class="font-semibold">New Users</h3>
               <!-- User list would go here -->
           </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';
import { io } from 'socket.io-client';
import { useAdminOrdersStore } from '../../../js/stores/adminOrders';
import { useAdminUsersStore } from '../../../js/stores/adminUsers';
import { useNotificationStore } from '../../../js/stores/notification';
import DashboardStats from '../../vue/components/DashboardStats.vue';

const ordersStore = useAdminOrdersStore();
const usersStore = useAdminUsersStore();
const notificationStore = useNotificationStore();

let socket;

onMounted(() => {
  // Connect to the WebSocket server
  socket = io('http://localhost:5000/admin'); // Use your server address and namespace

  socket.on('connect', () => {
    console.log('Connected to admin WebSocket namespace.');
  });

  // Listen for 'new_order' events
  socket.on('new_order', (order) => {
    notificationStore.showNotification({
      message: `New order #${order.id} placed for €${order.total_amount}.`,
      type: 'info'
    });
    // Refresh dashboard data
    ordersStore.fetchOrders(); 
  });

  // Listen for 'new_user' events
  socket.on('new_user', (user) => {
    notificationStore.showNotification({
      message: `New user registered: ${user.email}.`,
      type: 'info'
    });
    // Refresh dashboard data
    usersStore.fetchUsers();
  });

   // Fetch initial data
  ordersStore.fetchOrders();
  usersStore.fetchUsers();
});

onUnmounted(() => {
  // Disconnect the socket when the component is destroyed
  if (socket) {
    socket.disconnect();
  }
});
</script>
