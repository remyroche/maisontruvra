// website/source/admin/js/components/DataTable.js

/**
 * A component to render and manage data tables in the admin panel.
 * This is a more robust, though still simplified, version.
 */
export class DataTable {
    /**
     * @param {string} tableId The ID of the table element.
     * @param {object[]} columns An array of column configuration objects.
     * e.g., { data: 'name', title: 'User Name' }
     * @param {function} dataFetcher A function that returns a promise resolving to the data array.
     */
    constructor(tableId, columns, dataFetcher) {
        this.tableElement = document.getElementById(tableId);
        if (!this.tableElement) {
            throw new Error(`Table element with ID '${tableId}' not found.`);
        }
        this.columns = columns;
        this.dataFetcher = dataFetcher;
        this.tbody = this.tableElement.querySelector('tbody');
        this.thead = this.tableElement.querySelector('thead');
    }

    /**
     * Initializes the table, creates the header, and fetches the data.
     */
    async init() {
        this.createHeader();
        await this.loadData();
    }

    /**
     * Creates the table header row based on the column configuration.
     */
    createHeader() {
        this.thead.innerHTML = '';
        const headerRow = this.thead.insertRow();
        this.columns.forEach(col => {
            const th = document.createElement('th');
            th.textContent = col.title;
            th.className = 'px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider';
            headerRow.appendChild(th);
        });
    }

    /**
     * Fetches data using the provided dataFetcher and renders the table body.
     */
    async loadData() {
        try {
            const data = await this.dataFetcher();
            this.renderBody(data);
        } catch (error) {
            console.error('Error fetching data for table:', error);
            this.tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="text-center p-4">Failed to load data.</td></tr>`;
        }
    }

    /**
     * Renders the rows of the table body.
     * @param {object[]} data The array of data objects to render.
     */
    renderBody(data) {
        this.tbody.innerHTML = ''; // Clear existing data

        if (!data || data.length === 0) {
            this.tbody.innerHTML = `<tr><td colspan="${this.columns.length}" class="text-center p-4">No data available.</td></tr>`;
            return;
        }

        data.forEach(item => {
            const row = this.tbody.insertRow();
            this.columns.forEach(col => {
                const cell = row.insertCell();
                cell.className = 'px-6 py-4 whitespace-nowrap text-sm text-gray-700';
                
                // Handle complex data keys (e.g., 'user.name') - basic implementation
                let value = col.data.split('.').reduce((o, i) => o ? o[i] : '', item);
                
                // If a render function is provided for the column, use it
                if (col.render && typeof col.render === 'function') {
                    cell.innerHTML = col.render(value, item); // Use innerHTML for custom renderers
                } else {
                    cell.textContent = value; // Default to safe textContent
                }
            });
        });
    }

    /**
     * Refreshes the table data.
     */
    refresh() {
        this.loadData();
    }
}
