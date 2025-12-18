/**
 * Advanced search functionality
 * Phase 7: Advanced Features - M7.2: Enhanced UX & Performance
 */

// Global search state
const searchState = {
  activeFilters: {},
  searchQuery: '',
  debounceTimer: null
};

// Debounce search input
export function debounceSearch(callback, delay = 300) {
  return function(...args) {
    clearTimeout(searchState.debounceTimer);
    searchState.debounceTimer = setTimeout(() => {
      callback.apply(this, args);
    }, delay);
  };
}

// Advanced search with multiple filters
export function createAdvancedSearch(config) {
  const {
    containerId,
    searchInputId,
    filtersId,
    resultsContainerId,
    searchFunction,
    filterOptions = []
  } = config;

  const container = document.getElementById(containerId);
  if (!container) return;

  // Create search UI
  const searchHTML = `
    <div class="mb-4 space-y-4">
      <!-- Search Input -->
      <div class="relative">
        <input 
          type="text" 
          id="${searchInputId}" 
          placeholder="Search..." 
          class="input-field pl-10 pr-4"
        >
        <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" 
             fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
        </svg>
        <button id="${searchInputId}-clear" 
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 hidden">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>

      <!-- Advanced Filters -->
      <div id="${filtersId}" class="grid grid-cols-1 md:grid-cols-3 gap-4">
        ${filterOptions.map(filter => `
          <div>
            <label class="form-label">${filter.label}</label>
            <select id="${filter.id}" class="input-field">
              <option value="">All ${filter.label}</option>
              ${filter.options.map(opt => `
                <option value="${opt.value}">${opt.label}</option>
              `).join('')}
            </select>
          </div>
        `).join('')}
      </div>

      <!-- Active Filters Display -->
      <div id="${filtersId}-active" class="flex flex-wrap gap-2"></div>
    </div>
  `;

  container.insertAdjacentHTML('afterbegin', searchHTML);

  // Setup event listeners
  const searchInput = document.getElementById(searchInputId);
  const clearBtn = document.getElementById(`${searchInputId}-clear`);
  const filterSelects = filterOptions.map(f => document.getElementById(f.id));
  const activeFiltersContainer = document.getElementById(`${filtersId}-active`);

  // Search input handler
  const debouncedSearch = debounceSearch(() => {
    performSearch();
  }, 300);

  searchInput.addEventListener('input', (e) => {
    searchState.searchQuery = e.target.value;
    clearBtn.classList.toggle('hidden', !e.target.value);
    debouncedSearch();
  });

  // Clear search
  clearBtn.addEventListener('click', () => {
    searchInput.value = '';
    searchState.searchQuery = '';
    clearBtn.classList.add('hidden');
    performSearch();
  });

  // Filter handlers
  filterSelects.forEach((select, index) => {
    if (select) {
      select.addEventListener('change', () => {
        updateActiveFilters();
        performSearch();
      });
    }
  });

  function updateActiveFilters() {
    searchState.activeFilters = {};
    filterSelects.forEach((select, index) => {
      if (select && select.value) {
        const filterConfig = filterOptions[index];
        searchState.activeFilters[filterConfig.key] = select.value;
      }
    });
    renderActiveFilters();
  }

  function renderActiveFilters() {
    activeFiltersContainer.innerHTML = Object.entries(searchState.activeFilters).map(([key, value]) => {
      const filterConfig = filterOptions.find(f => f.key === key);
      const option = filterConfig?.options.find(o => o.value === value);
      return `
        <span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-orange-100 text-orange-800">
          ${filterConfig?.label}: ${option?.label || value}
          <button onclick="removeFilter('${key}')" class="ml-2 hover:text-orange-900">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </span>
      `;
    }).join('');
  }

  window.removeFilter = function(key) {
    const filterConfig = filterOptions.find(f => f.key === key);
    if (filterConfig) {
      const select = document.getElementById(filterConfig.id);
      if (select) {
        select.value = '';
        updateActiveFilters();
        performSearch();
      }
    }
  };

  function performSearch() {
    if (searchFunction) {
      searchFunction({
        query: searchState.searchQuery,
        filters: searchState.activeFilters
      });
    }
  }

  // Initial search
  performSearch();
}

// Export search state for use in other modules
export { searchState };

