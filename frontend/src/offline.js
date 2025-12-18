/**
 * Offline functionality and data sync
 * Phase 6: Mobile & Integrations - M6.1: Offline Data Sync
 */

// Import API functions dynamically to avoid circular dependencies
let apiModules = null;
async function getAPIs() {
  if (!apiModules) {
    apiModules = await import('./api.js');
  }
  return apiModules;
}

// Offline queue for actions that need to sync when back online
const offlineQueue = {
  actions: [],
  
  // Load queue from localStorage
  load() {
    try {
      const stored = localStorage.getItem('offlineQueue');
      if (stored) {
        this.actions = JSON.parse(stored);
      }
    } catch (e) {
      console.error('[Offline] Error loading queue:', e);
      this.actions = [];
    }
  },
  
  // Save queue to localStorage
  save() {
    try {
      localStorage.setItem('offlineQueue', JSON.stringify(this.actions));
    } catch (e) {
      console.error('[Offline] Error saving queue:', e);
    }
  },
  
  // Add action to queue
  add(action) {
    this.actions.push({
      ...action,
      timestamp: new Date().toISOString(),
      id: Date.now() + Math.random()
    });
    this.save();
    console.log('[Offline] Action queued:', action);
  },
  
  // Process queue when back online
  async process() {
    if (this.actions.length === 0) return;
    
    console.log(`[Offline] Processing ${this.actions.length} queued actions...`);
    
    const processed = [];
    const failed = [];
    
    for (const action of this.actions) {
      try {
        // Replay the action
        const result = await this.replayAction(action);
        if (result.success) {
          processed.push(action.id);
        } else {
          failed.push(action);
        }
      } catch (error) {
        console.error('[Offline] Error processing action:', error);
        failed.push(action);
      }
    }
    
    // Remove processed actions
    this.actions = failed;
    this.save();
    
    console.log(`[Offline] Processed ${processed.length} actions, ${failed.length} failed`);
    
    // Notify user if actions were processed
    if (processed.length > 0) {
      this.showSyncNotification(processed.length);
    }
  },
  
  // Replay a queued action
  async replayAction(action) {
    const { api } = await import('./api.js');
    
    switch (action.type) {
      case 'create_client':
        return await api.clientAPI.create(action.data);
      case 'update_client':
        return await api.clientAPI.update(action.id, action.data);
      case 'create_trainer':
        return await api.trainerAPI.create(action.data);
      case 'update_trainer':
        return await api.trainerAPI.update(action.id, action.data);
      case 'create_session':
        return await api.sessionAPI.create(action.data);
      case 'create_message':
        return await api.messageAPI.createMessage(action.threadId, action.data);
      case 'send_sms':
        return await api.smsAPI.send(action.data);
      default:
        console.warn('[Offline] Unknown action type:', action.type);
        return { success: false };
    }
  },
  
  // Show sync notification
  showSyncNotification(count) {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('FitnessCRM', {
        body: `Synced ${count} action${count > 1 ? 's' : ''} while you were offline`,
        icon: '/icons/icon-192x192.png',
        tag: 'offline-sync'
      });
    }
  }
};

// Initialize offline queue
offlineQueue.load();

// Monitor online/offline status
window.addEventListener('online', () => {
  console.log('[Offline] Back online, processing queue...');
  offlineQueue.process();
  
  // Also trigger background sync if service worker supports it
  if ('serviceWorker' in navigator && 'sync' in ServiceWorkerRegistration.prototype) {
    navigator.serviceWorker.ready.then(registration => {
      registration.sync.register('sync-data').catch(err => {
        console.error('[Offline] Background sync registration failed:', err);
      });
    });
  }
});

window.addEventListener('offline', () => {
  console.log('[Offline] Gone offline');
  showOfflineIndicator();
});

// Show offline indicator
function showOfflineIndicator() {
  let indicator = document.getElementById('offline-indicator');
  if (!indicator) {
    indicator = document.createElement('div');
    indicator.id = 'offline-indicator';
    indicator.className = 'fixed top-0 left-0 right-0 bg-yellow-500 text-white px-4 py-2 text-center z-50';
    indicator.textContent = 'You are offline. Changes will sync when you reconnect.';
    document.body.appendChild(indicator);
  }
}

// Hide offline indicator
function hideOfflineIndicator() {
  const indicator = document.getElementById('offline-indicator');
  if (indicator) {
    indicator.remove();
  }
}

// Check online status on load
if (navigator.onLine) {
  hideOfflineIndicator();
  // Process any queued actions
  offlineQueue.process();
} else {
  showOfflineIndicator();
}

// Export for use in other modules
export { offlineQueue };

// Wrap API calls to queue offline actions
export function queueOfflineAction(type, data, id = null, threadId = null) {
  offlineQueue.add({ type, data, id, threadId });
}

