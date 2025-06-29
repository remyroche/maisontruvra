// website/src/services/api.js
// Description: This is the new, single source for all API calls.
// It includes a global error handler to notify users of failed requests.

import axios from 'axios';
import { useNotificationStore } from '../stores/notification';
import router from '../router';


// Create an Axios instance with a base URL.
// The Vite proxy will handle forwarding these requests to the Flask backend in development.
const apiClient = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
    },
    withCredentials: true, // Send cookies with requests
});

// --- Axios Interceptors ---

// Request Interceptor to add CSRF token
apiClient.interceptors.request.use(async (config) => {
    // Only add CSRF token for state-changing methods
    if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(config.method.toUpperCase())) {
        try {
            // Fetch a new CSRF token for each relevant request to prevent stale tokens
            const { data } = await axios.get('/api/auth/csrf-token');
            config.headers['X-CSRF-TOKEN'] = data.csrf_token;
        } catch (error) {
            console.error('Could not fetch CSRF token', error);
            const notificationStore = useNotificationStore();
            notificationStore.addNotification({ message: 'A security error occurred. Please refresh the page.', type: 'error' });
            return Promise.reject(new Error('CSRF token fetch failed.'));
        }
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});


// Response Interceptor for global error handling
apiClient.interceptors.response.use(
    (response) => {
        // Any status code that lie within the range of 2xx cause this function to trigger
        return response;
    },
    (error) => {
        // Any status codes that falls outside the range of 2xx cause this function to trigger
        const notificationStore = useNotificationStore();

        if (error.response) {
            const { status, data } = error.response;
            const message = data.message || 'An unexpected error occurred.';

            switch (status) {
                case 401:
                    // Unauthorized: Redirect to login page
                    // This is a critical security action.
                    console.error('Unauthorized access. Redirecting to login.');
                    // Avoid redirecting if we are already on a public auth page
                    if (!router.currentRoute.value.meta.public) {
                        router.push({ name: 'Login' });
                        notificationStore.addNotification({ message: 'Your session has expired. Please log in again.', type: 'error' });
                    }
                    break;
                case 403:
                    // Forbidden
                    notificationStore.addNotification({ message: `Access Denied: ${message}`, type: 'error' });
                    break;
                case 404:
                    // Not Found
                    notificationStore.addNotification({ message: 'The requested resource was not found.', type: 'error' });
                    break;
                case 422: // Unprocessable Entity (Validation Error)
                case 400: // Bad Request
                    // The global handler can show a generic message.
                    // Specific forms should handle detailed error messages from the response body.
                    notificationStore.addNotification({ message: `Error: ${message}`, type: 'warning' });
                    break;
                case 500:
                default:
                    // Server Error or other issues
                    notificationStore.addNotification({ message: 'A server error occurred. Please try again later.', type: 'error' });
                    break;
            }
        } else if (error.request) {
            // The request was made but no response was received
            notificationStore.addNotification({ message: 'Could not connect to the server. Please check your network.', type: 'error' });
        } else {
            // Something happened in setting up the request that triggered an Error
            notificationStore.addNotification({ message: `An error occurred: ${error.message}`, type: 'error' });
        }

        return Promise.reject(error);
    }
);

// --- API Service Methods (Grouped by Feature) ---

export default {
    // === AUTHENTICATION ===
    login(credentials) { return apiClient.post('/auth/login', credentials); },
    logout() { return apiClient.post('/auth/logout'); },
    register(userData) { return apiClient.post('/auth/register', userData); },
    fetchCurrentUser() { return apiClient.get('/auth/me'); },
    forgotPassword(email) { return apiClient.post('/auth/forgot-password', { email }); },
    resetPassword(data) { return apiClient.post('/auth/reset-password', data); }, // { token, new_password }
    verifyEmail(token) { return apiClient.get(`/auth/verify-email/${token}`); },

    // === USER ACCOUNT ===
    getProfile() { return apiClient.get('/account/profile'); },
    updateProfile(profileData) { return apiClient.put('/account/profile', profileData); },
    changePassword(passwordData) { return apiClient.put('/account/change-password', passwordData); },
    getAccountOrders(params) { return apiClient.get('/account/orders', { params }); },
    getAccountOrder(orderId) { return apiClient.get(`/account/orders/${orderId}`); },
    getAddresses() { return apiClient.get('/account/addresses'); },
    addAddress(addressData) { return apiClient.post('/account/addresses', addressData); },
    updateAddress(addressId, addressData) { return apiClient.put(`/account/addresses/${addressId}`, addressData); },
    deleteAddress(addressId) { return apiClient.delete(`/account/addresses/${addressId}`); },

    // === PRODUCTS & SHOP ===
    getProducts(params) { return apiClient.get('/products', { params }); },
    getProduct(productId) { return apiClient.get(`/products/${productId}`); },
    getProductBySlug(slug) { return apiClient.get(`/products/slug/${slug}`); },
    getCategories() { return apiClient.get('/products/categories'); },
    getCollections() { return apiClient.get('/products/collections'); },
    addProductReview(productId, reviewData) { return apiClient.post(`/products/${productId}/reviews`, reviewData); },
    searchProducts(query) { return apiClient.get('/search', { params: { q: query } }); },

    // === CART ===
    getCart() { return apiClient.get('/cart'); },
    addToCart(productId, quantity, options = {}) { return apiClient.post('/cart/add', { product_id: productId, quantity, options }); },
    updateCartItem(itemId, quantity) { return apiClient.put(`/cart/item/${itemId}`, { quantity }); },
    removeFromCart(itemId) { return apiClient.delete(`/cart/item/${itemId}`); },

    // === WISHLIST ===
    getWishlist() { return apiClient.get('/wishlist'); },
    addToWishlist(productId) { return apiClient.post('/wishlist/add', { product_id: productId }); },
    removeFromWishlist(productId) { return apiClient.delete('/wishlist/remove', { data: { product_id: productId } }); },

    // === CHECKOUT ===
    startCheckout(checkoutData) { return apiClient.post('/checkout', checkoutData); },
    getDeliveryOptions(addressData) { return apiClient.post('/checkout/delivery-options', addressData); },
    getPaymentIntent() { return apiClient.post('/checkout/create-payment-intent'); },

    // === BLOG / JOURNAL ===
    getBlogPosts(params) { return apiClient.get('/blog', { params }); },
    getBlogPost(slug) { return apiClient.get(`/blog/post/${slug}`); },

    // === NEWSLETTER ===
    subscribeToNewsletter(email) { return apiClient.post('/newsletter/subscribe', { email }); },

    // === B2B (Business-to-Business) ===
    b2bLogin(credentials) { return apiClient.post('/b2b/auth/login', credentials); },
    b2bGetDashboard() { return apiClient.get('/b2b/dashboard'); },
    b2bGetOrders(params) { return apiClient.get('/b2b/orders', { params }); },
    b2bQuickOrder(items) { return apiClient.post('/b2b/quick-order', { items }); },
    b2bGetInvoices() { return apiClient.get('/b2b/invoices'); },

    // === ADMIN API ===
    // Admin Dashboard
    adminGetDashboardStats() { return apiClient.get('/admin/dashboard'); },

    // Admin User Management
    adminGetUsers(params) { return apiClient.get('/admin/users', { params }); },
    adminGetUser(userId) { return apiClient.get(`/admin/users/${userId}`); },
    adminCreateUser(userData) { return apiClient.post('/admin/users', userData); },
    adminUpdateUser(userId, userData) { return apiClient.put(`/admin/users/${userId}`, userData); },
    adminDeleteUser(userId) { return apiClient.delete(`/admin/users/${userId}`); },

    // Admin Product Management
    adminGetProducts(params) { return apiClient.get('/admin/products', { params }); },
    adminGetProduct(productId) { return apiClient.get(`/admin/products/${productId}`); },
    adminCreateProduct(productData) { return apiClient.post('/admin/products', productData, { headers: { 'Content-Type': 'multipart/form-data' } }); },
    adminUpdateProduct(productId, productData) { return apiClient.put(`/admin/products/${productId}`, productData, { headers: { 'Content-Type': 'multipart/form-data' } }); },
    adminDeleteProduct(productId) { return apiClient.delete(`/admin/products/${productId}`); },
    
    // Admin Order Management
    adminGetOrders(params) { return apiClient.get('/admin/orders', { params }); },
    adminGetOrder(orderId) { return apiClient.get(`/admin/orders/${orderId}`); },
    adminUpdateOrderStatus(orderId, status) { return apiClient.put(`/admin/orders/${orderId}/status`, { status }); },
    
    // Admin Blog Management
    adminGetBlogPosts(params) { return apiClient.get('/admin/blog', { params }); },
    adminCreateBlogPost(postData) { return apiClient.post('/admin/blog', postData); },
    adminUpdateBlogPost(postId, postData) { return apiClient.put(`/admin/blog/${postId}`, postData); },
    adminDeleteBlogPost(postId) { return apiClient.delete(`/admin/blog/${postId}`); },
    
    // Admin Audit Log
    adminGetAuditLogs(params) { return apiClient.get('/admin/audit-log', { params }); },


    // To classify
    adminGetDeliverySettings() { return apiClient.get('/admin/delivery/settings'); },
    adminUpdateDeliverySettings(settings) { return apiClient.post('/admin/delivery/settings', settings); },
    getDeliveryCountries() { return apiClient.get('/delivery/countries'); },


};