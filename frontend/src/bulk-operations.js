/**
 * Bulk operations functionality
 * Phase 7: Advanced Features - M7.2: Enhanced UX & Performance
 */

// Bulk selection state
const bulkState = {
  selectedItems: new Set(),
  selectAll: false
};

export function initBulkOperations(config) {
  const {
    containerId,
    itemSelector,
    checkboxSelector,
    selectAllId,
    bulkActionsId,
    onSelectionChange,
    bulkActions = []
  } = config;

  const container = document.getElementById(containerId);
  if (!container) return;

  // Create bulk actions bar
  const bulkActionsHTML = `
    <div id="${bulkActionsId}" class="hidden fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-white border border-gray-200 rounded-lg shadow-lg px-6 py-4 z-50">
      <div class="flex items-center space-x-4">
        <span id="${bulkActionsId}-count" class="font-semibold text-gray-700">0 selected</span>
        <div class="flex space-x-2">
          ${bulkActions.map(action => `
            <button 
              onclick="executeBulkAction('${action.id}')" 
              class="btn-${action.type || 'secondary'} text-sm px-4 py-2"
            >
              ${action.label}
            </button>
          `).join('')}
          <button 
            onclick="clearBulkSelection()" 
            class="btn-outline text-sm px-4 py-2"
          >
            Clear
          </button>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', bulkActionsHTML);

  // Setup select all checkbox
  const selectAllCheckbox = document.getElementById(selectAllId);
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', (e) => {
      bulkState.selectAll = e.target.checked;
      toggleAllItems(bulkState.selectAll);
      updateBulkActionsBar();
    });
  }

  // Setup item checkboxes
  container.addEventListener('change', (e) => {
    if (e.target.matches(checkboxSelector)) {
      const itemId = e.target.value;
      if (e.target.checked) {
        bulkState.selectedItems.add(itemId);
      } else {
        bulkState.selectedItems.delete(itemId);
        bulkState.selectAll = false;
        if (selectAllCheckbox) selectAllCheckbox.checked = false;
      }
      updateBulkActionsBar();
      if (onSelectionChange) {
        onSelectionChange(Array.from(bulkState.selectedItems));
      }
    }
  });

  function toggleAllItems(select) {
    const checkboxes = container.querySelectorAll(checkboxSelector);
    checkboxes.forEach(checkbox => {
      checkbox.checked = select;
      const itemId = checkbox.value;
      if (select) {
        bulkState.selectedItems.add(itemId);
      } else {
        bulkState.selectedItems.delete(itemId);
      }
    });
    updateBulkActionsBar();
    if (onSelectionChange) {
      onSelectionChange(Array.from(bulkState.selectedItems));
    }
  }

  function updateBulkActionsBar() {
    const bulkBar = document.getElementById(bulkActionsId);
    const countSpan = document.getElementById(`${bulkActionsId}-count`);
    
    if (bulkBar && countSpan) {
      const count = bulkState.selectedItems.size;
      countSpan.textContent = `${count} selected`;
      
      if (count > 0) {
        bulkBar.classList.remove('hidden');
      } else {
        bulkBar.classList.add('hidden');
      }
    }
  }

  window.clearBulkSelection = function() {
    bulkState.selectedItems.clear();
    bulkState.selectAll = false;
    
    const checkboxes = container.querySelectorAll(checkboxSelector);
    checkboxes.forEach(checkbox => {
      checkbox.checked = false;
    });
    
    if (selectAllCheckbox) {
      selectAllCheckbox.checked = false;
    }
    
    updateBulkActionsBar();
    if (onSelectionChange) {
      onSelectionChange([]);
    }
  };

  window.executeBulkAction = function(actionId) {
    const action = bulkActions.find(a => a.id === actionId);
    if (action && action.handler) {
      action.handler(Array.from(bulkState.selectedItems));
    }
  };

  // Export for external use
  return {
    getSelectedItems: () => Array.from(bulkState.selectedItems),
    clearSelection: window.clearBulkSelection
  };
}

export { bulkState };

