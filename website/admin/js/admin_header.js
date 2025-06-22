import { api } from './admin_api.js';

function getNavLinks(userRole, pages) {
    const allLinks = [
        { href: '/admin/admin_dashboard.html', text: 'Dashboard', page: 'admin_dashboard.html' },
        { href: '/admin/admin_manage_users.html', text: 'Manage Users', page: 'admin_manage_users.html' },
        { href: '/admin/admin_manage_products.html', text: 'Manage Products', page: 'admin_manage_products.html' },
        { href: '/admin/admin_manage_inventory.html', text: 'Manage Inventory', page: 'admin_manage_inventory.html' },
        { href: '/admin/admin_manage_orders.html', text: 'Manage Orders', page: 'admin_manage_orders.html' },
        { href: '/admin/admin_invoices.html', text: 'Manage Invoices', page: 'admin_invoices.html' },
        { href: '/admin/admin_manage_quotes.html', text: 'Manage Quotes', page: 'admin_manage_quotes.html' },
        { href: '/admin/admin_manage_pos.html', text: 'Point of Sale', page: 'admin_manage_pos.html' },
        { href: '/admin/admin_profile.html', text: 'Profile', page: 'admin_profile.html' },
        { href: '/admin/admin_manage_sessions.html', text: 'Manage Sessions', page: 'admin_manage_sessions.html' },
    ];
    
    // Filter links based on the pages the user's role is allowed to see
    return allLinks.filter(link => pages.includes(link.page));
}


export async function loadAdminHeader() {
    const headerContainer = document.getElementById('admin-header-container');
    const sidebarContainer = document.getElementById('admin-sidebar-container');
    const token = localStorage.getItem('admin_access_token');
    
    if (!token) {
        console.error("No token found, cannot load header/sidebar");
        return;
    }

    // Decode token to get user info without a server call
    const decodedToken = JSON.parse(atob(token.split('.')[1]));
    const userRole = decodedToken.role;
    const authorizedPages = decodedToken.pages;


    const headerResponse = await fetch('/admin/admin_header.html');
    const headerHtml = await headerResponse.text();
    headerContainer.innerHTML = headerHtml;

    const sidebarResponse = await fetch('/admin/admin_sidebar.html');
    let sidebarHtml = await sidebarResponse.text();
    
    const navLinks = getNavLinks(userRole, authorizedPages);
    const navHtml = navLinks.map(link => {
        const isActive = window.location.pathname.endsWith(link.href);
        return `<a href="${link.href}" class="block py-2.5 px-4 rounded transition duration-200 hover:bg-mt-truffle-burgundy ${isActive ? 'bg-mt-truffle-burgundy' : ''}">${link.text}</a>`;
    }).join('');

    sidebarHtml = sidebarHtml.replace('<!-- DYNAMIC_NAV_LINKS -->', navHtml);
    sidebarContainer.innerHTML = sidebarHtml;

    document.getElementById('logout-button').addEventListener('click', async (e) => {
        e.preventDefault();
        try {
            await api.post('/auth/logout');
        } catch (error) {
            console.error("Logout failed, clearing token anyway.", error);
        } finally {
            localStorage.removeItem('admin_access_token');
            window.location.href = '/admin/admin_login.html';
        }
    });

    const userMenuButton = document.getElementById('user-menu-button');
    const userMenu = document.getElementById('user-menu');
    if(userMenuButton) {
        userMenuButton.addEventListener('click', () => {
            userMenu.classList.toggle('hidden');
        });
    }
}
