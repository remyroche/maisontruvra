document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const tableBody = document.getElementById('invoices-table-body');
    const tableHeaders = document.querySelectorAll('#invoices-table th[data-sort]');
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    const paginationControls = document.getElementById('pagination-controls');

    // --- State Management ---
    const state = {
        allInvoices: [], // Stores all invoices fetched from the API
        filteredInvoices: [], // Stores invoices after filtering
        sort: {
            column: 'date',
            direction: 'desc'
        },
        pagination: {
            currentPage: 1,
            itemsPerPage: 10,
        },
        filters: {
            searchTerm: '',
            status: 'all'
        }
    };

    // --- Utility Functions ---
    /**
     * Debounce function to limit how often a function is called.
     * Useful for search inputs to avoid firing on every keystroke.
     * @param {Function} func The function to debounce.
     * @param {number} delay The delay in milliseconds.
     * @returns {Function} The debounced function.
     */
    const debounce = (func, delay) => {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), delay);
        };
    };

    // --- UI Update Functions ---
    const showLoading = () => {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center p-8 text-gray-500">Chargement des factures...</td></tr>`;
        paginationControls.classList.add('hidden');
    };

    const showError = (message) => {
        tableBody.innerHTML = `<tr><td colspan="5" class="text-center p-8 text-red-500">${message}</td></tr>`;
        paginationControls.classList.add('hidden');
    };
    
    const updateSortIndicators = () => {
        tableHeaders.forEach(header => {
            const indicator = header.querySelector('.sort-indicator');
            if (header.dataset.sort === state.sort.column) {
                indicator.textContent = state.sort.direction === 'asc' ? '▲' : '▼';
            } else {
                indicator.textContent = '';
            }
        });
    };

    // --- Main Render Function ---
    const render = () => {
        // 1. Apply Filtering
        let filtered = [...state.allInvoices];
        if (state.filters.searchTerm) {
            filtered = filtered.filter(inv => inv.id.toLowerCase().includes(state.filters.searchTerm.toLowerCase()));
        }
        if (state.filters.status !== 'all') {
            filtered = filtered.filter(inv => inv.status === state.filters.status);
        }
        state.filteredInvoices = filtered;

        // 2. Apply Sorting
        state.filteredInvoices.sort((a, b) => {
            const { column, direction } = state.sort;
            let valA = a[column];
            let valB = b[column];
            if (column === 'date') {
                valA = new Date(valA);
                valB = new Date(valB);
            }
            if (valA < valB) return direction === 'asc' ? -1 : 1;
            if (valA > valB) return direction === 'asc' ? 1 : -1;
            return 0;
        });
        
        // 3. Apply Pagination
        const { currentPage, itemsPerPage } = state.pagination;
        const totalItems = state.filteredInvoices.length;
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        const start = (currentPage - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        const paginatedInvoices = state.filteredInvoices.slice(start, end);

        // 4. Render Table
        if (paginatedInvoices.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="5" class="text-center p-8 text-gray-500">Aucune facture ne correspond à votre recherche.</td></tr>`;
            paginationControls.classList.add('hidden');
        } else {
            tableBody.innerHTML = '';
            paginatedInvoices.forEach(invoice => {
                const statusClass = invoice.status === 'Payée' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
                const row = `
                    <tr class="border-b border-gray-200 hover:bg-gray-50">
                        <td class="p-4 font-medium">${invoice.id}</td>
                        <td class="p-4 text-gray-700">${new Date(invoice.date).toLocaleDateString('fr-FR')}</td>
                        <td class="p-4 text-gray-700">${invoice.amount.toFixed(2)} €</td>
                        <td class="p-4">
                            <span class="px-2 py-1 text-xs font-semibold rounded-full ${statusClass}">${invoice.status}</span>
                        </td>
                        <td class="p-4">
                            <a href="${invoice.url}" download class="text-black hover:underline" aria-label="Télécharger la facture ${invoice.id}">
                                <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                            </a>
                        </td>
                    </tr>`;
                tableBody.insertAdjacentHTML('beforeend', row);
            });
            paginationControls.classList.remove('hidden');
        }

        // 5. Update UI components
        updateSortIndicators();
        pageInfo.textContent = `Page ${currentPage} sur ${totalPages || 1}`;
        prevPageBtn.disabled = currentPage === 1;
        nextPageBtn.disabled = currentPage === totalPages || totalPages === 0;
    };
    
    // --- Data Fetching ---
    const loadInvoices = async () => {
        showLoading();
        try {
            const rawInvoices = await proApi.getInvoices();
            state.allInvoices = rawInvoices.map(inv => ({
                id: inv.invoice_number,
                date: inv.created_at,
                amount: inv.total_amount,
                status: inv.status,
                url: inv.pdf_url
            }));
            state.pagination.currentPage = 1;
            render();
        } catch (error) {
            console.error('Erreur lors du chargement des factures:', error);
            showError('Impossible de charger vos factures. Veuillez réessayer plus tard.');
        }
    };

    // --- Event Handlers ---
    const handleSort = (column) => {
        if (state.sort.column === column) {
            state.sort.direction = state.sort.direction === 'asc' ? 'desc' : 'asc';
        } else {
            state.sort.column = column;
            state.sort.direction = 'asc';
        }
        state.pagination.currentPage = 1;
        render();
    };

    const handleSearch = debounce((event) => {
        state.filters.searchTerm = event.target.value;
        state.pagination.currentPage = 1;
        render();
    }, 300);

    const handleFilterStatus = (event) => {
        state.filters.status = event.target.value;
        state.pagination.currentPage = 1;
        render();
    };

    // --- Event Listeners ---
    tableHeaders.forEach(header => header.addEventListener('click', () => handleSort(header.dataset.sort)));
    searchInput.addEventListener('input', handleSearch);
    statusFilter.addEventListener('change', handleFilterStatus);
    prevPageBtn.addEventListener('click', () => {
        if (state.pagination.currentPage > 1) {
            state.pagination.currentPage--;
            render();
        }
    });
    nextPageBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(state.filteredInvoices.length / state.pagination.itemsPerPage);
        if (state.pagination.currentPage < totalPages) {
            state.pagination.currentPage++;
            render();
        }
    });

    // --- Initial Load ---
    loadInvoices();
});
