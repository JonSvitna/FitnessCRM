/**
 * Keyboard shortcuts system
 * Phase 7: Advanced Features - M7.2: Enhanced UX & Performance
 */

const shortcuts = {
  // Navigation shortcuts
  'g d': () => showSection('dashboard-section', 'Dashboard'),
  'g t': () => showSection('trainers-section', 'Trainers'),
  'g c': () => showSection('clients-section', 'Clients'),
  'g s': () => showSection('settings-section', 'Settings'),
  'g a': () => showSection('activity-section', 'Activity Log'),
  
  // Action shortcuts
  'n': (e) => {
    // Create new item based on current section
    const activeSection = document.querySelector('.section:not(.hidden)');
    if (activeSection) {
      const sectionId = activeSection.id;
      if (sectionId === 'trainers-section') {
        document.getElementById('new-trainer-btn')?.click();
      } else if (sectionId === 'clients-section') {
        document.getElementById('new-client-btn')?.click();
      }
    }
  },
  
  // Search shortcut
  '/': (e) => {
    e.preventDefault();
    const activeSection = document.querySelector('.section:not(.hidden)');
    if (activeSection) {
      const searchInput = activeSection.querySelector('input[type="text"][placeholder*="Search"]');
      if (searchInput) {
        searchInput.focus();
      }
    }
  },
  
  // Escape to close modals
  'Escape': () => {
    const modals = document.querySelectorAll('.fixed.inset-0.bg-black.bg-opacity-50');
    modals.forEach(modal => {
      if (!modal.classList.contains('hidden')) {
        const closeBtn = modal.querySelector('[id*="close"], [id*="cancel"]');
        if (closeBtn) closeBtn.click();
      }
    });
  }
};

let currentKeys = [];
let shortcutTimer = null;

export function initKeyboardShortcuts() {
  document.addEventListener('keydown', (e) => {
    // Ignore if typing in input/textarea
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
      // Allow Escape and shortcuts that start with /
      if (e.key === 'Escape' || e.key === '/') {
        // Continue
      } else {
        return;
      }
    }

    // Handle single key shortcuts
    if (shortcuts[e.key]) {
      shortcuts[e.key](e);
      return;
    }

    // Handle multi-key shortcuts (e.g., 'g' then 'd' for 'go dashboard')
    if (e.key === 'g') {
      currentKeys = ['g'];
      shortcutTimer = setTimeout(() => {
        currentKeys = [];
      }, 1000);
      return;
    }

    if (currentKeys.length > 0 && currentKeys[0] === 'g') {
      const shortcut = `g ${e.key}`;
      if (shortcuts[shortcut]) {
        e.preventDefault();
        shortcuts[shortcut](e);
        currentKeys = [];
        clearTimeout(shortcutTimer);
      }
    }
  });

  // Show shortcuts help
  window.showShortcutsHelp = function() {
    const shortcutsList = Object.entries(shortcuts).map(([keys, handler]) => {
      const displayKeys = keys.split(' ').map(k => 
        k === 'Escape' ? 'Esc' : k.toUpperCase()
      ).join(' + ');
      return `<div class="flex justify-between py-2 border-b"><span class="font-mono">${displayKeys}</span><span class="text-gray-600">Action</span></div>`;
    }).join('');

    const helpHTML = `
      <div class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
        <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
          <div class="p-6 border-b">
            <div class="flex justify-between items-center">
              <h3 class="text-2xl font-bold">Keyboard Shortcuts</h3>
              <button onclick="this.closest('.fixed').remove()" class="text-gray-500 hover:text-gray-700">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
          </div>
          <div class="p-6 space-y-2">
            <div class="font-semibold mb-4">Navigation</div>
            <div class="flex justify-between py-2"><span class="font-mono">G + D</span><span class="text-gray-600">Go to Dashboard</span></div>
            <div class="flex justify-between py-2"><span class="font-mono">G + T</span><span class="text-gray-600">Go to Trainers</span></div>
            <div class="flex justify-between py-2"><span class="font-mono">G + C</span><span class="text-gray-600">Go to Clients</span></div>
            <div class="flex justify-between py-2"><span class="font-mono">G + S</span><span class="text-gray-600">Go to Settings</span></div>
            <div class="font-semibold mt-6 mb-4">Actions</div>
            <div class="flex justify-between py-2"><span class="font-mono">N</span><span class="text-gray-600">New Item</span></div>
            <div class="flex justify-between py-2"><span class="font-mono">/</span><span class="text-gray-600">Focus Search</span></div>
            <div class="flex justify-between py-2"><span class="font-mono">Esc</span><span class="text-gray-600">Close Modal</span></div>
          </div>
        </div>
      </div>
    `;

    document.body.insertAdjacentHTML('beforeend', helpHTML);
  };

  // Add ? to show shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === '?' && !e.target.matches('input, textarea')) {
      e.preventDefault();
      window.showShortcutsHelp();
    }
  });
}

