/**
 * Factory for creating interactive and paginated data tables.
 * This has been updated to handle server-side pagination data.
 */
class DataTableFactory {
    /**
     * @param {string} containerId The ID of the element to render the table in.
     * @param {object} options The configuration options for the table.
     * @param {Array<object>} options.columns An array of column definition objects.
     * @param {function(number): Promise<object>} options.fetchData An async function that takes a page number and returns paginated data.
     * @param {string} options.dataKey The key in the fetch response that contains the array of items (e.g., 'users', 'products').
     * @param {string} options.totalKey The key in the fetch response that contains the total number of items.
     */
    constructor(containerId, { columns, fetchData, dataKey, totalKey }) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`DataTable container #${containerId} not found.`);
            return;
        }
        this.columns = columns;
        this.fetchData = fetchData;
        this.dataKey = dataKey;
        this.totalKey = totalKey;
        this.currentPage = 1;
        this.totalPages = 1;
        this.totalItems = 0;

        this.render();
    }

    async render() {
        this.container.innerHTML = `
            <div class="table-responsive">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr></tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        <!-- Data rows will be inserted here -->
                    </tbody>
                </table>
            </div>
            <div id="pagination-controls" class="mt-4 flex items-center justify-between"></div>
        `;

        const theadRow = this.container.querySelector('thead tr');
        this.columns.forEach(col => {
            const th = document.createElement('th');
            th.scope = 'col';
            th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
            th.textContent = col.header;
            theadRow.appendChild(th);
        });

        await this.loadPage(this.currentPage);
    }

    async loadPage(page) {
        this.currentPage = page;
        const tbody = this.container.querySelector('tbody');
        tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="text-center p-4">Loading...</td></tr>`;

        try {
            const response = await this.fetchData(this.currentPage);
            this.totalPages = response.total_pages;
            this.totalItems = response[this.totalKey];
            const items = response[this.dataKey];

            tbody.innerHTML = ''; // Clear loading message

            if (items && items.length > 0) {
                 items.forEach(item => {
                    const tr = document.createElement('tr');
                    this.columns.forEach(col => {
                        const td = document.createElement('td');
                        td.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-700';
                        // Handle nested properties if needed, e.g., 'user.email'
                        const value = col.key.split('.').reduce((p, c) => (p && p[c]) || null, item);
                        td.innerHTML = col.cell ? col.cell(item) : value; // Use cell render function if provided
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="text-center p-4">No data available.</td></tr>`;
            }
            this.renderPaginationControls();
        } catch (error) {
            console.error('Failed to load data for table:', error);
            tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="text-center p-4 text-red-500">Failed to load data.</td></tr>`;
        }
    }

    renderPaginationControls() {
        const controlsContainer = this.container.querySelector('#pagination-controls');
        if (!controlsContainer) return;
        
        controlsContainer.innerHTML = `
            <div>
                 <p class="text-sm text-gray-700">
                    Showing <span class="font-medium">${Math.min(1 + (this.currentPage - 1) * 15, this.totalItems)}</span>
                    to <span class="font-medium">${Math.min(this.currentPage * 15, this.totalItems)}</span>
                    of <span class="font-medium">${this.totalItems}</span> results
                </p>
            </div>
            <div class="flex items-center">
                <div class="text-sm text-gray-700 mr-4">
                    Page <span class="font-medium">${this.currentPage}</span> of <span class="font-medium">${this.totalPages}</span>
                </div>
                <button id="prev-btn" class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50" ${this.currentPage <= 1 ? 'disabled' : ''}>
                    Previous
                </button>
                 <button id="next-btn" class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50" ${this.currentPage >= this.totalPages ? 'disabled' : ''}>
                    Next
                </button>
            </div>
        `;
        
        controlsContainer.querySelector('#prev-btn').addEventListener('click', () => this.loadPage(this.currentPage - 1));
        controlsContainer.querySelector('#next-btn').addEventListener('click', () => this.loadPage(this.currentPage + 1));
    }
}
