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
      if (user.role === 'trainer') {
        window.location.href = '/trainer.html';
      } else if (user.role === 'client' || user.role === 'user') {
        window.location.href = '/client.html';
      } else if (user.role === 'admin') {
        window.location.href = '/index.html';
      } else {
        window.location.href = '/login.html';
      }
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

        // Redirect based on user role (with safe fallback)
        let redirectTo = '/index.html'; // Default to admin dashboard
        
        if (user && user.role) {
          if (user.role === 'trainer') {
            redirectTo = '/trainer.html';
          } else if (user.role === 'client' || user.role === 'user') {
            redirectTo = '/client.html';
          } else if (user.role === 'admin') {
            redirectTo = '/index.html';
          }
        }
        
        // Override with explicit redirect parameter if provided
        const explicitRedirect = new URLSearchParams(window.location.search).get('redirect');
        if (explicitRedirect) {
          redirectTo = explicitRedirect;
        }
        
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
        window.location.href = '/index.html';
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

