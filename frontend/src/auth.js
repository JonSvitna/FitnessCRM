/**
 * Authentication Module
 * Handles login, logout, token management, and auth checks
 */

import { authAPI } from './api.js';

// Token management
export const auth = {
  getToken: () => localStorage.getItem('auth_token'),
  setToken: (token) => localStorage.setItem('auth_token', token),
  removeToken: () => localStorage.removeItem('auth_token'),
  getUser: () => {
    const userStr = localStorage.getItem('auth_user');
    return userStr ? JSON.parse(userStr) : null;
  },
  setUser: (user) => localStorage.setItem('auth_user', JSON.stringify(user)),
  removeUser: () => localStorage.removeItem('auth_user'),
  isAuthenticated: () => !!localStorage.getItem('auth_token'),
};

// Validate redirect URL to prevent open redirect attacks
function isValidRedirectUrl(url) {
  if (!url) return false;
  
  // Only allow internal paths that start with /
  if (!url.startsWith('/')) return false;
  
  // Block URLs that try to redirect to external sites (e.g., //example.com)
  if (url.startsWith('//')) return false;
  
  // Block URLs with explicit protocols (http:, https:, javascript:, data:, etc.)
  // Check for protocol at the start (allowing colons elsewhere in the URL)
  if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(url)) return false;
  
  return true;
}

/**
 * Get the appropriate redirect URL based on user role and optional explicit redirect
 * 
 * @param {Object|null} user - The user object with a 'role' property
 * @param {string|null} explicitRedirect - Optional explicit redirect URL from query parameters
 * @returns {string} The validated redirect URL
 * 
 * Security: The explicitRedirect parameter is validated to prevent open redirect attacks.
 * Only internal paths (starting with '/') are allowed. External URLs and protocol-based
 * redirects are blocked.
 * 
 * Role-based defaults:
 * - 'trainer' -> /trainer.html
 * - 'client' or 'user' -> /client.html
 * - 'admin' -> /index.html
 * - default/unknown -> /index.html
 */
export function getRedirectUrl(user, explicitRedirect = null) {
  // Validate and use explicit redirect if provided
  if (explicitRedirect && isValidRedirectUrl(explicitRedirect)) {
    return explicitRedirect;
  }
  
  // Default redirect based on user role
  if (user && user.role) {
    if (user.role === 'trainer') {
      return '/trainer.html';
    } else if (user.role === 'client' || user.role === 'user') {
      return '/client.html';
    } else if (user.role === 'admin') {
      return '/index.html';
    }
  }
  
  // Default to admin dashboard
  return '/index.html';
}

// Check if user is authenticated
export async function checkAuth() {
  const token = auth.getToken();
  if (!token) {
    return false;
  }

  try {
    const response = await authAPI.getCurrentUser();
    if (response.data && response.data.user) {
      auth.setUser(response.data.user);
      return true;
    }
  } catch (error) {
    console.error('Auth check failed:', error);
    auth.removeToken();
    auth.removeUser();
    return false;
  }

  return false;
}

// Redirect to login if not authenticated
export async function requireAuth() {
  const isAuth = await checkAuth();
  if (!isAuth) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

// Require specific role to access a page
export async function requireRole(allowedRoles) {
  const isAuth = await checkAuth();
  if (!isAuth) {
    window.location.href = '/login.html';
    return false;
  }
  
  const user = auth.getUser();
  if (!user || !allowedRoles.includes(user.role)) {
    // Redirect to appropriate portal based on role
    if (user) {
      // Use shared redirect logic for consistency
      const redirectTo = getRedirectUrl(user);
      window.location.href = redirectTo;
    } else {
      window.location.href = '/login.html';
    }
    return false;
  }
  
  return true;
}

// Initialize login page
if (document.getElementById('login-form')) {
  const loginForm = document.getElementById('login-form');
  const errorMessage = document.getElementById('error-message');
  const loginButton = document.getElementById('login-button');
  const loginButtonText = document.getElementById('login-button-text');
  const loginButtonLoading = document.getElementById('login-button-loading');
  const togglePassword = document.getElementById('toggle-password');
  const passwordInput = document.getElementById('password');
  const eyeIcon = document.getElementById('eye-icon');
  const eyeOffIcon = document.getElementById('eye-off-icon');

  // Toggle password visibility
  if (togglePassword) {
    togglePassword.addEventListener('click', () => {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      eyeIcon.classList.toggle('hidden');
      eyeOffIcon.classList.toggle('hidden');
    });
  }

  // Handle login form submission
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Hide error message
    errorMessage.classList.add('hidden');
    
    // Show loading state
    loginButton.disabled = true;
    loginButtonText.classList.add('hidden');
    loginButtonLoading.classList.remove('hidden');

    try {
      const response = await authAPI.login({ email, password });
      
      if (response.data && response.data.token) {
        // Store token and user
        auth.setToken(response.data.token);
        const user = response.data.user;
        if (user) {
          auth.setUser(user);
        }

        // Get redirect URL based on user role
        const explicitRedirect = new URLSearchParams(window.location.search).get('redirect');
        const redirectTo = getRedirectUrl(user, explicitRedirect);
        
        window.location.href = redirectTo;
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Show error message with helpful guidance
      let errorText = error.response?.data?.error || error.message || 'Login failed. Please check your credentials.';
      
      // Add helpful message for common issues
      if (error.response?.status === 401) {
        errorText += '\n\nIf this is a trainer/client account, make sure a password has been set via the admin dashboard.';
      }
      
      errorMessage.textContent = errorText;
      errorMessage.classList.remove('hidden');
      
      // Reset button state
      loginButton.disabled = false;
      loginButtonText.classList.remove('hidden');
      loginButtonLoading.classList.add('hidden');
    }
  });

  // Check if already logged in
  if (auth.isAuthenticated()) {
    checkAuth().then((isAuth) => {
      if (isAuth) {
        // Get redirect URL based on user role
        const user = auth.getUser();
        const explicitRedirect = new URLSearchParams(window.location.search).get('redirect');
        const redirectTo = getRedirectUrl(user, explicitRedirect);
        
        window.location.href = redirectTo;
      }
    }).catch((error) => {
      console.error('Auth check error:', error);
    });
  }
}

// Logout function
export function logout() {
  auth.removeToken();
  auth.removeUser();
  // Clear saved section on logout
  localStorage.removeItem('currentSection');
  localStorage.removeItem('currentSectionTitle');
  window.location.href = '/login.html';
}

// Export for use in other modules
window.auth = auth;
window.logout = logout;

