<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Blog</h1>
    
    <div class="mb-4 flex justify-between items-center">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search posts..." 
        class="border rounded p-2 w-1/3"
      >
      <div class="flex items-center space-x-4">
        <label class="flex items-center text-sm">
            <input type="checkbox" v-model="includeDeleted" @change="fetchData" class="mr-2 h-4 w-4 rounded">
            Show Deleted
        </label>
        <button @click="openCreateModal" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
          Create Post
        </button>
      </div>
    </div>

    <div v-if="blogStore.isLoading" class="text-center p-4">Loading posts...</div>
    <div v-if="blogStore.error" class="text-red-500 bg-red-100 p-4 rounded">{{ blogStore.error }}</div>

    <BaseDataTable
      v-if="!blogStore.isLoading && filteredPosts.length"
      :headers="headers"
      :items="filteredPosts"
    >
        <template #row="{ item }">
            <tr :class="{ 'bg-red-50 text-gray-500 italic': item.is_deleted }">
                <td v-for="header in headers" :key="header.value" class="px-6 py-4 whitespace-nowrap text-sm">
                    <slot :name="`item-${header.value}`" :item="item">{{ getNestedValue(item, header.value) }}</slot>
                </td>
            </tr>
        </template>
        
        <template #item-is_published="{ item }">
            <span :class="item.is_published ? 'text-green-500' : 'text-gray-500'">
                {{ item.is_published ? 'Published' : 'Draft' }}
            </span>
             <span v-if="item.is_deleted" class="ml-2 px-2 py-0.5 text-xs font-semibold rounded-full bg-red-200 text-red-800">Deleted</span>
        </template>
        
        <template #item-actions="{ item }">
            <div class="flex items-center space-x-2">
                <button v-if="!item.is_deleted" @click="openEditModal(item)" class="text-indigo-600 hover:text-indigo-900 text-sm">Edit</button>
                <button v-if="!item.is_deleted" @click="confirmDelete(item, 'soft')" class="text-yellow-600 hover:text-yellow-900 text-sm">Soft Delete</button>
                <button v-if="item.is_deleted" @click="restorePost(item.id)" class="text-green-600 hover:text-green-900 text-sm">Restore</button>
                <button @click="confirmDelete(item, 'hard')" class="text-red-600 hover:text-red-900 text-sm">Hard Delete</button>
            </div>
        </template>
    </BaseDataTable>
    
    <div v-if="!blogStore.isLoading && !filteredPosts.length" class="text-center text-gray-500 mt-8">
        No posts found.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAdminBlogStore } from '@/js/stores/adminBlog';
import BaseDataTable from '@/js/admin/components/ui/BaseDataTable.vue';

const blogStore = useAdminBlogStore();

const searchQuery = ref('');
const includeDeleted = ref(false);

const headers = [
  { text: 'Title', value: 'title' },
  { text: 'Category', value: 'category.name' },
  { text: 'Author', value: 'author.first_name' },
  { text: 'Status', value: 'is_published' },
  { text: 'Actions', value: 'actions', sortable: false },
];

const fetchData = () => {
    blogStore.fetchPosts({ include_deleted: includeDeleted.value });
    blogStore.fetchCategories();
};

onMounted(fetchData);

const filteredPosts = computed(() => {
    if (!searchQuery.value) return blogStore.posts;
    return blogStore.posts.filter(p => p.title.toLowerCase().includes(searchQuery.value.toLowerCase()));
});

const getNestedValue = (item, path) => {
    return path.split('.').reduce((acc, part) => acc && acc[part], item);
};

const confirmDelete = (post, type) => {
  const action = type === 'soft' ? 'soft-delete' : 'PERMANENTLY DELETE';
  if (window.confirm(`Are you sure you want to <span class="math-inline">\{action\} the post "</span>{post.title}"?`)) {
    const deleteAction = type === 'soft' ? blogStore.softDeletePost : blogStore.hardDeletePost;
    deleteAction(post.id);
  }
};

const restorePost = (postId) => {
  if (window.confirm('Are you sure you want to restore this post?')) {
    blogStore.restorePost(postId);
  }
};
// NOTE: Modal and form logic would be added here, similar to other views.
</script>
```website/js/admin/router/index.js` (Add Blog route)
```javascript
// ... other imports
import ManageBlogView from '@/js/admin/views/ManageBlogView.vue';

const routes = [
    // ... other routes
    { path: '/blog', name: 'ManageBlog', component: ManageBlogView, meta: { requiresAuth: true, roles: ['Admin', 'Manager', 'Editor'] } },
    // ...
]
// ...
```website/js/admin/components/layout/SidebarNav.vue` (Add Blog link)
```vue
<!-- ... inside the <nav> element ... -->
<router-link to="/admin/blog" v-if="hasRole(['Admin', 'Manager', 'Editor'])"
    class="flex items-center px-4 py-2 text-gray-700 rounded-md hover:bg-gray-200"
    active-class="bg-gray-200">
    <span class="mx-4 font-medium">Blog</span>
</router-link>
<!-- ... -->
