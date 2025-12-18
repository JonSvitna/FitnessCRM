/**
 * Dark mode support
 * Phase 7: Advanced Features - M7.2: Enhanced UX & Performance
 */

const DARK_MODE_KEY = 'fitnesscrm_dark_mode';

export function initDarkMode() {
  // Check saved preference
  const savedMode = localStorage.getItem(DARK_MODE_KEY);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  const isDark = savedMode === 'dark' || (!savedMode && prefersDark);
  
  if (isDark) {
    document.documentElement.classList.add('dark');
  }

  // Create toggle button
  createDarkModeToggle();

  // Listen for system preference changes
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem(DARK_MODE_KEY)) {
      if (e.matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  });
}

function createDarkModeToggle() {
  // Check if toggle already exists
  if (document.getElementById('dark-mode-toggle')) return;

  const toggle = document.createElement('button');
  toggle.id = 'dark-mode-toggle';
  toggle.className = 'fixed bottom-4 left-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full p-3 shadow-lg z-50 hover:shadow-xl transition-all';
  toggle.innerHTML = `
    <svg id="dark-mode-icon-sun" class="w-5 h-5 text-yellow-500 hidden dark:block" fill="currentColor" viewBox="0 0 20 20">
      <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
    </svg>
    <svg id="dark-mode-icon-moon" class="w-5 h-5 text-gray-700 dark:hidden" fill="currentColor" viewBox="0 0 20 20">
      <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
    </svg>
  `;

  toggle.addEventListener('click', toggleDarkMode);
  document.body.appendChild(toggle);
}

function toggleDarkMode() {
  const isDark = document.documentElement.classList.contains('dark');
  
  if (isDark) {
    document.documentElement.classList.remove('dark');
    localStorage.setItem(DARK_MODE_KEY, 'light');
  } else {
    document.documentElement.classList.add('dark');
    localStorage.setItem(DARK_MODE_KEY, 'dark');
  }
}

export function isDarkMode() {
  return document.documentElement.classList.contains('dark');
}

