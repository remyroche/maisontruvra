import { getCSRFToken } from './utils.js';
import { API_BASE_URL } from './config.js';
import { useNotificationStore } from './stores/notification';

/**
 * A wrapper for the native fetch API with robust error handling.
 * @param {string} endpoint The API endpoint to call.
 * @param {object} [options={}] Optional fetch options.
 * @returns {Promise<any>} A promise that resolves with the JSON response.
 */
async function fetchAPI(endpoint, options = {}) {
    const notificationStore = useNotificationStore();
    let url = `${API_BASE_URL}${endpoint}`;
    
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
    };

    const method = options.method?.toUpperCase() || 'GET';

    if (method !== 'GET' && method !== 'HEAD') {
        const csrfToken = await getCSRFToken();
        if (csrfToken) {
            headers['X-CSRF-TOKEN'] = csrfToken;
        } else {
            console.error("CSRF Token not found. Aborting mutating request.");
            notificationStore.showNotification("Une erreur de sécurité est survenue. Veuillez rafraîchir la page.", "error");
            return Promise.reject(new Error("CSRF Token not found."));
        }
    }

    const config = { ...options, method, headers };
    if (options.body) {
        config.body = JSON.stringify(options.body);
    }
    
    try {
        const response = await fetch(url, config);
        
        if (!response.ok) {
            let errorData = { message: `Erreur HTTP: ${response.status} ${response.statusText}` };
            try {
                // Try to parse a more specific error message from the API response body
                errorData = await response.json();
            } catch (e) {
                // The body was not JSON or was empty. The status text is the best we have.
            }
            // Throw an object that includes status and the specific message
            throw { status: response.status, data: errorData };
        }

        if (response.status === 204) { // No Content
            return null;
        }
        return await response.json();

    } catch (error) {
        let userMessage;

        if (error.data) { // This is an error object we threw from a non-2xx response
            userMessage = error.data.error || error.data.message || "Une erreur est survenue.";
            console.error(`API Error ${error.status}:`, error.data);
        } else { // This is likely a network error (e.g., fetch failed, CORS, etc.)
            userMessage = "Impossible de contacter le serveur. Veuillez vérifier votre connexion réseau.";
            console.error('Network or other fetch error:', error);
        }

        // Display the user-friendly message
        notificationStore.showNotification(userMessage, 'error');
        
        // Propagate the error so calling functions can also react if needed
        throw error;
    }
}

// The rest of your apiClient object remains the same...
const apiClient = {
    // ... all your methods like getProducts, login, etc.
    // They will now automatically use the new robust fetchAPI handler.
    getProducts: (params) => fetchAPI('/api/products/', { params }),
    searchProducts: (query) => fetchAPI(`/api/products/search`, { params: { q: query } }),
    getProduct: (id) => fetchAPI(`/api/products/${id}`),
    getProductReviews: (id) => fetchAPI(`/api/products/${id}/reviews`),
    submitReview: (id, reviewData) => fetchAPI(`/api/products/${id}/reviews`, { method: 'POST', body: reviewData }),

    getCart: () => fetchAPI('/api/cart/'),
    addToCart: (productId, quantity) => fetchAPI('/api/cart/add', { method: 'POST', body: { product_id: productId, quantity } }),
    updateCartItem: (productId, quantity) => fetchAPI('/api/cart/update', { method: 'PUT', body: { product_id: productId, quantity } }),
    removeFromCart: (productId) => fetchAPI('/api/cart/remove', { method: 'POST', body: { product_id: productId } }),
    applyVoucher: (voucherCode) => fetchAPI('/api/cart/voucher/apply', {method: 'POST', body: {voucher_code: voucherCode}}),

    login: (email, password) => fetchAPI('/api/auth/login', { method: 'POST', body: { email, password } }),
    register: (userData) => fetchAPI('/api/auth/register', { method: 'POST', body: userData }),
    logout: () => fetchAPI('/api/auth/logout', { method: 'POST' }),
    checkSession: () => fetchAPI('/api/auth/session'),
    requestPasswordReset: (email) => fetchAPI('/api/auth/forgot-password', { method: 'POST', body: { email } }),
    resetPassword: (token, newPassword) => fetchAPI('/api/auth/reset-password', { method: 'POST', body: { token, new_password: newPassword } }),

    getAccountDetails: () => fetchAPI('/api/account/profile'),
    updateAccountDetails: (profileData) => fetchAPI('/api/account/profile', { method: 'PUT', body: profileData }),
    changePassword: (passwords) => fetchAPI('/api/account/password', { method: 'PUT', body: passwords }),
    getAddresses: () => fetchAPI('/api/account/addresses'),
    addAddress: (addressData) => fetchAPI('/api/account/addresses', { method: 'POST', body: addressData }),
    updateAddress: (addressId, addressData) => fetchAPI(`/api/account/addresses/${addressId}`, { method: 'PUT', body: addressData }),
    deleteAddress: (addressId) => fetchAPI(`/api/account/addresses/${addressId}`, { method: 'DELETE' }),

    createOrder: (orderPayload) => fetchAPI('/api/orders/create', { method: 'POST', body: orderPayload }),
    getOrder: (orderId) => fetchAPI(`/api/orders/${orderId}`),
    listOrders: () => fetchAPI('/api/orders/'),

    subscribeB2C: (email) => fetchAPI('/api/newsletter/subscribe/b2c', { method: 'POST', body: { email } }),
    subscribeB2B: (email) => fetchAPI('/api/newsletter/subscribe/b2b', { method: 'POST', body: { email } }),

    getBlogPosts: () => fetchAPI('/api/blog/posts'),
    getBlogPostBySlug: (slug) => fetchAPI(`/api/blog/posts/${slug}`),

    b2bLogin: (credentials) => fetchAPI('/api/b2b/auth/login', { method: 'POST', body: credentials }),
    b2bRegister: (companyInfo) => fetchAPI('/api/b2b/auth/register', { method: 'POST', body: companyInfo }),
    b2bLogout: => fetchAPI('/api/b2b/auth/logout', { method: 'POST' }),
    getB2BDashboard: () => fetchAPI('/api/b2b/dashboard'),
    getB2BProducts: (params) => fetchAPI('/api/b2b/products', { params }),
    getB2BOrders: (params) => fetchAPI('/api/b2b/orders', { params }),
    createB2BOrder: (orderData) => fetchAPI('/api/b2b/orders', { method: 'POST', body: orderData }),
    getB2BInvoices: (params) => fetchAPI('/api/b2b/invoices', { params }),
    getB2BInvoice: (invoiceId) => fetchAPI(`/api/b2b/invoices/${invoiceId}`),
    getB2BProfile: () => fetchAPI('/api/b2b/profile'),
    updateB2BProfile: (profileData) => fetchAPI('/api/b2b/profile', { method: 'PUT', body: profileData }),
};


export default apiClient;
