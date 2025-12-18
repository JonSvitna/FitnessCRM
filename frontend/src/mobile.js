/**
 * Mobile optimization and touch interactions
 * Phase 6: Mobile & Integrations - M6.2: Mobile Optimization
 */

// Touch-optimized button sizes and spacing
document.addEventListener('DOMContentLoaded', () => {
  // Add touch-friendly classes to interactive elements
  enhanceTouchTargets();
  
  // Initialize swipe gestures
  initSwipeGestures();
  
  // Enhance tables for mobile
  enhanceMobileTables();
  
  // Add pull-to-refresh
  initPullToRefresh();
  
  // Optimize images for mobile
  optimizeImages();
  
  // Add mobile-specific event listeners
  addMobileEventListeners();
});

// Enhance touch targets (minimum 44x44px for accessibility)
function enhanceTouchTargets() {
  // Add touch-friendly class to buttons
  const buttons = document.querySelectorAll('button, .btn-primary, .btn-secondary, .btn-outline, a[role="button"]');
  buttons.forEach(btn => {
    if (!btn.classList.contains('touch-friendly')) {
      btn.classList.add('touch-friendly');
    }
  });
  
  // Enhance form inputs
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach(input => {
    if (!input.classList.contains('touch-input')) {
      input.classList.add('touch-input');
    }
  });
}

// Initialize swipe gestures
function initSwipeGestures() {
  let touchStartX = 0;
  let touchStartY = 0;
  let touchEndX = 0;
  let touchEndY = 0;
  
  const sidebar = document.getElementById('sidebar');
  const swipeThreshold = 50; // Minimum distance for swipe
  
  document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
    touchStartY = e.changedTouches[0].screenY;
  }, { passive: true });
  
  document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
  }, { passive: true });
  
  function handleSwipe() {
    const deltaX = touchEndX - touchStartX;
    const deltaY = touchEndY - touchStartY;
    
    // Check if horizontal swipe is more significant than vertical
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > swipeThreshold) {
      // Swipe right to open sidebar (from left edge)
      if (deltaX > 0 && touchStartX < 20 && sidebar) {
        sidebar.classList.add('sidebar-mobile-open');
        const overlay = document.getElementById('mobile-overlay');
        if (overlay) overlay.classList.remove('hidden');
      }
      // Swipe left to close sidebar
      else if (deltaX < 0 && sidebar && sidebar.classList.contains('sidebar-mobile-open')) {
        sidebar.classList.remove('sidebar-mobile-open');
        const overlay = document.getElementById('mobile-overlay');
        if (overlay) overlay.classList.add('hidden');
      }
    }
    
    // Vertical swipe for pull-to-refresh (handled separately)
    if (Math.abs(deltaY) > Math.abs(deltaX) && Math.abs(deltaY) > swipeThreshold) {
      // Handled by pull-to-refresh
    }
  }
}

// Enhance tables for mobile (convert to cards on small screens)
function enhanceMobileTables() {
  const tables = document.querySelectorAll('table');
  
  tables.forEach(table => {
    if (!table.classList.contains('mobile-enhanced')) {
      table.classList.add('mobile-enhanced');
      
      // Add wrapper for mobile card view
      const wrapper = document.createElement('div');
      wrapper.className = 'table-mobile-wrapper hidden md:block';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
      
      // Create mobile card view
      createMobileCardView(table);
    }
  });
}

// Create mobile card view for tables
function createMobileCardView(table) {
  const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
  const rows = table.querySelectorAll('tbody tr');
  
  if (rows.length === 0) return;
  
  const cardContainer = document.createElement('div');
  cardContainer.className = 'table-mobile-cards md:hidden space-y-4';
  
  rows.forEach(row => {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow p-4 border border-gray-200';
    
    const cells = row.querySelectorAll('td');
    cells.forEach((cell, index) => {
      if (headers[index]) {
        const item = document.createElement('div');
        item.className = 'mb-3 last:mb-0';
        
        const label = document.createElement('div');
        label.className = 'text-xs font-semibold text-gray-500 uppercase mb-1';
        label.textContent = headers[index];
        
        const value = document.createElement('div');
        value.className = 'text-sm text-gray-900';
        value.innerHTML = cell.innerHTML;
        
        item.appendChild(label);
        item.appendChild(value);
        card.appendChild(item);
      }
    });
    
    // Add action buttons if present
    const actions = row.querySelector('.actions, [data-actions]');
    if (actions) {
      const actionContainer = document.createElement('div');
      actionContainer.className = 'mt-4 pt-4 border-t border-gray-200 flex space-x-2';
      actionContainer.innerHTML = actions.innerHTML;
      card.appendChild(actionContainer);
    }
    
    cardContainer.appendChild(card);
  });
  
  table.parentNode.insertBefore(cardContainer, table);
}

// Pull-to-refresh functionality
let pullToRefresh = {
  startY: 0,
  currentY: 0,
  isPulling: false,
  threshold: 80,
  
  init() {
    let touchStartY = 0;
    let isAtTop = false;
    
    window.addEventListener('touchstart', (e) => {
      touchStartY = e.touches[0].clientY;
      isAtTop = window.scrollY === 0;
      
      if (isAtTop) {
        this.startY = touchStartY;
        this.isPulling = true;
      }
    }, { passive: true });
    
    window.addEventListener('touchmove', (e) => {
      if (!this.isPulling || !isAtTop) return;
      
      this.currentY = e.touches[0].clientY;
      const pullDistance = this.currentY - this.startY;
      
      if (pullDistance > 0 && pullDistance < 150) {
        this.showPullIndicator(pullDistance);
      }
    }, { passive: true });
    
    window.addEventListener('touchend', () => {
      if (this.isPulling && this.currentY - this.startY > this.threshold) {
        this.triggerRefresh();
      }
      this.hidePullIndicator();
      this.isPulling = false;
    }, { passive: true });
  },
  
  showPullIndicator(distance) {
    let indicator = document.getElementById('pull-to-refresh-indicator');
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'pull-to-refresh-indicator';
      indicator.className = 'fixed top-0 left-0 right-0 bg-orange-500 text-white text-center py-2 z-50 transform -translate-y-full transition-transform';
      indicator.innerHTML = '<div class="flex items-center justify-center space-x-2"><svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg><span>Pull to refresh</span></div>';
      document.body.appendChild(indicator);
    }
    
    const progress = Math.min(distance / this.threshold, 1);
    indicator.style.transform = `translateY(${(progress - 1) * 100}%)`;
  },
  
  hidePullIndicator() {
    const indicator = document.getElementById('pull-to-refresh-indicator');
    if (indicator) {
      indicator.style.transform = 'translateY(-100%)';
      setTimeout(() => {
        if (indicator.parentNode) {
          indicator.parentNode.removeChild(indicator);
        }
      }, 300);
    }
  },
  
  async triggerRefresh() {
    // Dispatch custom event for pages to handle refresh
    window.dispatchEvent(new CustomEvent('pulltorefresh'));
    
    // Default: reload current page data
    if (typeof window.loadDashboard === 'function') {
      await window.loadDashboard();
    } else if (typeof window.location !== 'undefined') {
      // Fallback: reload page
      window.location.reload();
    }
  }
};

function initPullToRefresh() {
  pullToRefresh.init();
}

// Optimize images for mobile
function optimizeImages() {
  const images = document.querySelectorAll('img');
  
  images.forEach(img => {
    // Add loading="lazy" for better performance
    if (!img.hasAttribute('loading')) {
      img.setAttribute('loading', 'lazy');
    }
    
    // Add responsive sizing
    if (!img.classList.contains('responsive-img')) {
      img.classList.add('responsive-img');
    }
  });
}

// Add mobile-specific event listeners
function addMobileEventListeners() {
  // Prevent zoom on double tap (iOS)
  let lastTouchEnd = 0;
  document.addEventListener('touchend', (e) => {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
      e.preventDefault();
    }
    lastTouchEnd = now;
  }, false);
  
  // Handle orientation change
  window.addEventListener('orientationchange', () => {
    // Close mobile menu on orientation change
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    if (sidebar) sidebar.classList.remove('sidebar-mobile-open');
    if (overlay) overlay.classList.add('hidden');
    
    // Trigger resize after orientation change
    setTimeout(() => {
      window.dispatchEvent(new Event('resize'));
    }, 100);
  });
  
  // Optimize scroll performance
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        // Scroll-based optimizations can go here
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });
}

// Export for use in other modules
export { pullToRefresh };

