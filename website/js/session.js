/**
 * Manages the user's session token in localStorage.
 */
const TOKEN_KEY = 'jwt_token';

export const storeToken = (token) => {
    localStorage.setItem(TOKEN_KEY, token);
};

export const getToken = () => {
    return localStorage.getItem(TOKEN_KEY);
};

export const removeToken = () => {
    localStorage.removeItem(TOKEN_KEY);
};
