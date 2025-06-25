<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">Manage Assets</h1>
    <div class="mb-4">
        <h2 class="text-xl font-semibold">Upload New Asset</h2>
        <input type="file" @change="onFileChange" class="mb-2">
        <button @click="uploadAsset" class="bg-blue-500 text-white px-4 py-2 rounded">Upload</button>
    </div>
    <div v-if="assetsStore.error" class="text-red-500">{{ assetsStore.error }}</div>
    <div>
      <table class="min-w-full bg-white">
        <thead>
          <tr>
            <th class="py-2">Filename</th>
            <th class="py-2">URL</th>
            <th class="py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="asset in assetsStore.assets" :key="asset.id">
            <td class="border px-4 py-2">{{ asset.filename }}</td>
            <td class="border px-4 py-2"><a :href="asset.url" target="_blank" class="text-blue-500 hover:underline">Link</a></td>
            <td class="border px-4 py-2">
              <button @click="deleteAsset(asset.id)" class="bg-red-500 text-white px-4 py-2 rounded">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useAdminAssetsStore } from '@/js/stores/adminAssets';

const assetsStore = useAdminAssetsStore();
const selectedFile = ref(null);

onMounted(() => {
  assetsStore.fetchAssets();
});

const onFileChange = (e) => {
  selectedFile.value = e.target.files[0];
};

const uploadAsset = () => {
    if(selectedFile.value) {
        assetsStore.uploadAsset(selectedFile.value);
    }
};

const deleteAsset = (assetId) => {
    assetsStore.deleteAsset(assetId);
};
</script>
