// Delhi Land Records MVP - Main JavaScript
const API_BASE = '/api';

// Utility Functions
function formatCurrency(amount) {
    if (!amount) return 'N/A';
    return `₹${amount.toLocaleString('en-IN')}`;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
}

function getStatusBadgeClass(status) {
    const classMap = {
        'Clear': 'status-clear',
        'Mortgaged': 'status-mortgaged',
        'Disputed': 'status-disputed',
        'Unknown': 'status-unknown'
    };
    return classMap[status] || 'status-unknown';
}

// API Functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

async function searchProperties(filters, page = 1, pageSize = 20) {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
            params.append(key, value);
        }
    });

    params.append('page', page);
    params.append('page_size', pageSize);

    return await apiCall(`/properties/search?${params.toString()}`);
}

async function getProperty(id) {
    return await apiCall(`/properties/${id}`);
}

async function compareProperties(propertyIds) {
    return await apiCall('/properties/compare', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ property_ids: propertyIds })
    });
}

async function getLocalityStats(locality) {
    return await apiCall(`/statistics/locality/${encodeURIComponent(locality)}`);
}

async function getSummaryStats() {
    return await apiCall('/statistics/summary');
}

async function getMetadata() {
    return await apiCall('/metadata');
}

// Home Page Functions
async function loadHomePageStats() {
    try {
        const metadata = await getMetadata();
        const summary = await getSummaryStats();

        // Total properties
        document.getElementById('total-properties').textContent =
            metadata.total_records.toLocaleString('en-IN');

        // Calculate clear titles
        let clearTitles = 0;
        Object.values(summary).forEach(locality => {
            clearTitles += Math.round(locality.total_properties * locality.clear_title_percentage / 100);
        });
        document.getElementById('clear-titles').textContent = clearTitles.toLocaleString('en-IN');

        // Calculate average price
        const avgPrices = Object.values(summary)
            .map(l => l.avg_price_per_sqm)
            .filter(p => p !== null);
        const avgPrice = avgPrices.reduce((a, b) => a + b, 0) / avgPrices.length;
        document.getElementById('avg-price').textContent = formatCurrency(Math.round(avgPrice));

        // Update locality counts
        const localityMap = {
            'Greater Kailash I': 'gk1-count',
            'Greater Kailash II': 'gk2-count',
            'Greater Kailash III': 'gk3-count',
            'Chitranjan Park': 'crp-count'
        };

        Object.entries(summary).forEach(([locality, stats]) => {
            const elementId = localityMap[locality];
            if (elementId) {
                document.getElementById(elementId).textContent =
                    `${stats.total_properties} properties`;
            }
        });

    } catch (error) {
        console.error('Failed to load home page stats:', error);
    }
}

function setupQuickSearch() {
    const form = document.getElementById('quickSearchForm');
    const input = document.getElementById('quickSearchInput');

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (query) {
            window.location.href = `/search?plot_number=${encodeURIComponent(query)}`;
        }
    });
}

function setupLocalityButtons() {
    const buttons = document.querySelectorAll('.locality-btn');
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            const locality = button.dataset.locality;
            window.location.href = `/search?locality=${encodeURIComponent(locality)}`;
        });
    });
}

// Search Page Functions
let selectedProperties = new Set();
let currentPage = 1;
let currentFilters = {};

function setupSearchPage() {
    loadSearchFromURL();
    setupSearchForm();
    setupCompareButton();
}

function loadSearchFromURL() {
    const params = new URLSearchParams(window.location.search);
    const filters = {};

    ['locality', 'plot_number', 'min_area', 'max_area', 'min_price', 'max_price',
     'encumbrance_status', 'property_type'].forEach(key => {
        const value = params.get(key);
        if (value) {
            filters[key] = value;
            const element = document.getElementById(key.replace('_', ''));
            if (element) element.value = value;
        }
    });

    performSearch(filters);
}

function setupSearchForm() {
    const form = document.getElementById('searchForm');
    const clearBtn = document.getElementById('clearFilters');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const filters = {};

        formData.forEach((value, key) => {
            if (value) filters[key] = value;
        });

        currentPage = 1;
        await performSearch(filters);
    });

    clearBtn.addEventListener('click', () => {
        form.reset();
        currentPage = 1;
        selectedProperties.clear();
        performSearch({});
    });
}

async function performSearch(filters, page = 1) {
    currentFilters = filters;

    showLoading();

    try {
        const results = await searchProperties(filters, page);

        hideLoading();
        displayResults(results);
        updatePagination(results.total, page, results.page_size);

    } catch (error) {
        hideLoading();
        showError('Failed to search properties');
    }
}

function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('resultsGrid').innerHTML = '';
    document.getElementById('emptyState').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
}

function displayResults(results) {
    const grid = document.getElementById('resultsGrid');
    const emptyState = document.getElementById('emptyState');

    document.getElementById('totalResults').textContent = results.total;

    if (results.properties.length === 0) {
        emptyState.classList.remove('hidden');
        grid.innerHTML = '';
        return;
    }

    emptyState.classList.add('hidden');

    grid.innerHTML = results.properties.map(property => createPropertyCard(property)).join('');

    // Add event listeners to cards
    grid.querySelectorAll('.property-card').forEach(card => {
        const propertyId = parseInt(card.dataset.propertyId);

        card.querySelector('.card-body').addEventListener('click', () => {
            window.location.href = `/property/${propertyId}`;
        });

        const checkbox = card.querySelector('.compare-checkbox');
        checkbox.addEventListener('change', () => {
            if (checkbox.checked) {
                if (selectedProperties.size < 4) {
                    selectedProperties.add(propertyId);
                    card.classList.add('selected');
                } else {
                    checkbox.checked = false;
                    alert('You can compare up to 4 properties at a time');
                }
            } else {
                selectedProperties.delete(propertyId);
                card.classList.remove('selected');
            }
            updateCompareButton();
        });
    });
}

function createPropertyCard(property) {
    const pricePerSqm = property.market_value_estimate
        ? (property.market_value_estimate / property.area_sqm).toFixed(0)
        : null;

    return `
        <div class="property-card" data-property-id="${property.id}">
            <div class="p-4 card-body">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="text-lg font-semibold text-gray-800">${property.plot_number}</h3>
                    <span class="status-badge ${getStatusBadgeClass(property.encumbrance_status)}">
                        ${property.encumbrance_status}
                    </span>
                </div>

                <p class="text-gray-600 mb-2">${property.locality}</p>

                <div class="space-y-1 text-sm mb-3">
                    <div class="flex justify-between">
                        <span class="text-gray-600">Area:</span>
                        <span class="font-medium">${property.area_sqm} sqm</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Type:</span>
                        <span class="font-medium">${property.property_type}</span>
                    </div>
                    ${property.market_value_estimate ? `
                    <div class="flex justify-between">
                        <span class="text-gray-600">Price:</span>
                        <span class="font-medium">${formatCurrency(property.market_value_estimate)}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">Per sqm:</span>
                        <span class="font-medium">${formatCurrency(pricePerSqm)}/sqm</span>
                    </div>
                    ` : ''}
                </div>

                <div class="text-xs text-gray-500">
                    Last verified: ${formatDate(property.last_verified)}
                </div>
            </div>

            <div class="px-4 py-3 bg-gray-50 border-t">
                <label class="flex items-center cursor-pointer">
                    <input type="checkbox" class="compare-checkbox mr-2">
                    <span class="text-sm text-gray-700">Add to comparison</span>
                </label>
            </div>
        </div>
    `;
}

function updatePagination(total, currentPage, pageSize) {
    const pagination = document.getElementById('pagination');
    const totalPages = Math.ceil(total / pageSize);

    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = '';

    // Previous button
    html += `
        <button class="pagination-btn" ${currentPage === 1 ? 'disabled' : ''}
                onclick="performSearch(currentFilters, ${currentPage - 1})">
            Previous
        </button>
    `;

    // Page numbers
    for (let i = 1; i <= Math.min(totalPages, 10); i++) {
        html += `
            <button class="pagination-btn ${i === currentPage ? 'active' : ''}"
                    onclick="performSearch(currentFilters, ${i})">
                ${i}
            </button>
        `;
    }

    // Next button
    html += `
        <button class="pagination-btn" ${currentPage === totalPages ? 'disabled' : ''}
                onclick="performSearch(currentFilters, ${currentPage + 1})">
            Next
        </button>
    `;

    pagination.innerHTML = html;
}

function setupCompareButton() {
    const btn = document.getElementById('compareButton');
    btn.addEventListener('click', () => {
        if (selectedProperties.size >= 2) {
            const ids = Array.from(selectedProperties).join(',');
            window.location.href = `/compare?ids=${ids}`;
        }
    });
}

function updateCompareButton() {
    const btn = document.getElementById('compareButton');
    const count = document.getElementById('selectedCount');

    count.textContent = selectedProperties.size;
    btn.disabled = selectedProperties.size < 2;
}

function showError(message) {
    alert(message); // In production, use a better notification system
}

// Global error handler
window.addEventListener('unhandledrejection', event => {
    console.error('Unhandled promise rejection:', event.reason);
});
