import { handleAPIError } from './common/api_helper.js';
import { getCSRFToken } from './utils.js';
import { API_BASE_URL } from './config.js';

/**
 * A wrapper for the native fetch API to simplify making API calls.
 * It automatically includes CSRF tokens for mutating requests.
 *
 * @param {string} endpoint The API endpoint to call.
 * @param {object} [options={}] Optional fetch options (method, body, headers, etc.).
 * @returns {Promise<any>} A promise that resolves with the JSON response.
 */
async function fetchAPI(endpoint, options = {}) {
    let url = `${API_BASE_URL}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    const method = options.method || 'GET';

    if (method !== 'GET' && method !== 'HEAD') {
        const csrfToken = await getCSRFToken();
        if (csrfToken) {
            headers['X-CSRF-TOKEN'] = csrfToken;
        }
    }

    const config = {
        ...options,
        method,
        headers,
        body: options.body ? JSON.stringify(options.body) : null,
    };
    
    // For GET requests, append params to URL if any
    if ((method === 'GET' || method === 'HEAD') && options.params) {
        const params = new URLSearchParams(options.params);
        url += `?${params.toString()}`;
    }


    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: 'An unknown error occurred' }));
            throw { status: response.status, data: errorData };
        }
        if (response.status === 204) { // No Content
            return null;
        }
        return await response.json();
    } catch (error) {
        handleAPIError(error);
        throw error;
    }
}


const apiClient = {
    // Product APIs
    getProducts: (params) => fetchAPI('/api/products/', { params }),
    getProduct: (id) => fetchAPI(`/api/products/${id}`),
    getProductReviews: (id) => fetchAPI(`/api/products/${id}/reviews`),
    submitReview: (id, reviewData) => fetchAPI(`/api/products/${id}/reviews`, { method: 'POST', body: reviewData }),

    // Cart APIs
    getCart: () => fetchAPI('/api/cart/'),
    addToCart: (productId, quantity) => fetchAPI('/api/cart/add', { method: 'POST', body: { product_id: productId, quantity } }),
    updateCartItem: (productId, quantity) => fetchAPI('/api/cart/update', { method: 'PUT', body: { product_id: productId, quantity } }),
    removeFromCart: (productId) => fetchAPI('/api/cart/remove', { method: 'POST', body: { product_id: productId } }),
    applyVoucher: (voucherCode) => fetchAPI('/api/cart/voucher/apply', {method: 'POST', body: {voucher_code: voucherCode}}),

    // Auth APIs
    login: (email, password) => fetchAPI('/api/auth/login', { method: 'POST', body: { email, password } }),
    register: (userData) => fetchAPI('/api/auth/register', { method: 'POST', body: userData }),
    logout: () => fetchAPI('/api/auth/logout', { method: 'POST' }),
    checkSession: () => fetchAPI('/api/auth/session'),
    requestPasswordReset: (email) => fetchAPI('/api/auth/forgot-password', { method: 'POST', body: { email } }),
    resetPassword: (token, newPassword) => fetchAPI('/api/auth/reset-password', { method: 'POST', body: { token, new_password: newPassword } }),

    // User account APIs
    getAccountDetails: () => fetchAPI('/api/account/profile'),
    updateAccountDetails: (profileData) => fetchAPI('/api/account/profile', { method: 'PUT', body: profileData }),
    changePassword: (passwords) => fetchAPI('/api/account/password', { method: 'PUT', body: passwords }),
    getAddresses: () => fetchAPI('/api/account/addresses'),
    addAddress: (addressData) => fetchAPI('/api/account/addresses', { method: 'POST', body: addressData }),
    updateAddress: (addressId, addressData) => fetchAPI(`/api/account/addresses/${addressId}`, { method: 'PUT', body: addressData }),
    deleteAddress: (addressId) => fetchAPI(`/api/account/addresses/${addressId}`, { method: 'DELETE' }),

    // Order APIs
    createOrder: (orderPayload) => fetchAPI('/api/orders/create', { method: 'POST', body: orderPayload }),
    getOrder: (orderId) => fetchAPI(`/api/orders/${orderId}`),
    listOrders: () => fetchAPI('/api/orders/'),

    // Newsletter
    subscribeB2C: (email) => fetchAPI('/api/newsletter/subscribe/b2c', { method: 'POST', body: { email } }),

    // B2B APIs
    b2bLogin: (credentials) => fetchAPI('/api/b2b/auth/login', { method: 'POST', body: credentials }),
    b2bRegister: (companyInfo) => fetchAPI('/api/b2b/auth/register', { method: 'POST', body: companyInfo }),
    b2bLogout: () => fetchAPI('/api/b2b/auth/logout', { method: 'POST' }),
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
