/**
 * Sidebar Section Management
 * Handles collapsible sections with pinning functionality
 */

// Load section state from localStorage
function loadSectionState(sectionId) {
  const stored = localStorage.getItem(`sidebar-section-${sectionId}`);
  if (stored) {
    return JSON.parse(stored);
  }
  return {
    expanded: true,
    pinned: false
  };
}

// Save section state to localStorage
function saveSectionState(sectionId, state) {
  localStorage.setItem(`sidebar-section-${sectionId}`, JSON.stringify(state));
}

// Initialize collapsible sections
export function initCollapsibleSections() {
  const sections = document.querySelectorAll('.sidebar-section-header');
  
  sections.forEach(header => {
    const sectionId = header.dataset.sectionId;
    if (!sectionId) return;
    
    const itemsContainer = header.nextElementSibling;
    if (!itemsContainer || !itemsContainer.classList.contains('sidebar-section-items')) return;
    
    // Load saved state
    const state = loadSectionState(sectionId);
    
    // Set initial state
    if (state.expanded) {
      itemsContainer.classList.add('expanded');
      itemsContainer.classList.remove('collapsed');
    } else {
      itemsContainer.classList.add('collapsed');
      itemsContainer.classList.remove('expanded');
    }
    
    // Find toggle and pin buttons
    const toggleBtn = header.querySelector('.sidebar-section-toggle');
    const pinBtn = header.querySelector('.sidebar-section-pin');
    
    // Update toggle icon
    updateToggleIcon(toggleBtn, state.expanded);
    
    // Update pin icon
    if (pinBtn) {
      if (state.pinned) {
        pinBtn.classList.add('pinned');
        pinBtn.innerHTML = `
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z"></path>
          </svg>
        `;
      } else {
        pinBtn.classList.remove('pinned');
        pinBtn.innerHTML = `
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path>
          </svg>
        `;
      }
    }
    
    // Toggle expand/collapse
    if (toggleBtn) {
      toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isExpanded = itemsContainer.classList.contains('expanded');
        
        if (isExpanded) {
          itemsContainer.classList.remove('expanded');
          itemsContainer.classList.add('collapsed');
          state.expanded = false;
        } else {
          itemsContainer.classList.remove('collapsed');
          itemsContainer.classList.add('expanded');
          state.expanded = true;
        }
        
        updateToggleIcon(toggleBtn, state.expanded);
        saveSectionState(sectionId, state);
      });
    }
    
    // Toggle pin
    if (pinBtn) {
      pinBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        state.pinned = !state.pinned;
        
        if (state.pinned) {
          pinBtn.classList.add('pinned');
          pinBtn.innerHTML = `
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z"></path>
            </svg>
          `;
          // Auto-expand when pinned
          itemsContainer.classList.remove('collapsed');
          itemsContainer.classList.add('expanded');
          state.expanded = true;
          updateToggleIcon(toggleBtn, true);
        } else {
          pinBtn.classList.remove('pinned');
          pinBtn.innerHTML = `
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z"></path>
            </svg>
          `;
        }
        
        saveSectionState(sectionId, state);
      });
    }
    
    // Click header to toggle (if not clicking buttons)
    header.addEventListener('click', (e) => {
      if (e.target.closest('.sidebar-section-toggle') || e.target.closest('.sidebar-section-pin')) {
        return;
      }
      
      const isExpanded = itemsContainer.classList.contains('expanded');
      
      if (isExpanded) {
        itemsContainer.classList.remove('expanded');
        itemsContainer.classList.add('collapsed');
        state.expanded = false;
      } else {
        itemsContainer.classList.remove('collapsed');
        itemsContainer.classList.add('expanded');
        state.expanded = true;
      }
      
      updateToggleIcon(toggleBtn, state.expanded);
      saveSectionState(sectionId, state);
    });
  });
}

function updateToggleIcon(btn, isExpanded) {
  if (!btn) return;
  
  if (isExpanded) {
    btn.innerHTML = `
      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
      </svg>
    `;
  } else {
    btn.innerHTML = `
      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
      </svg>
    `;
  }
}

