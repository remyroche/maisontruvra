/*
 * FILENAME: website/js/stores/adminAssets.js
 * DESCRIPTION: Pinia store for managing site assets (images, etc.).
 */
import { defineStore } from 'pinia';
import { ref } from 'vue';
import adminApiClient from '../common/adminApiClient';

export const useAdminAssetStore = defineStore('adminAssets', () => {
    const assets = ref([]);
    const isLoading = ref(false);
    const error = ref(null);

    async function fetchAssets() {
        // ...
    }

    async function uploadAsset(file) {
        // ...
    }
    
    async function deleteAsset(id) {
        // ...
    }

    return { assets, isLoading, error, fetchAssets, uploadAsset, deleteAsset };
});
