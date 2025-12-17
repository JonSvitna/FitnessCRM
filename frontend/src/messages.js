/**
 * Messages/Messaging Interface
 * Phase 5: Communication - M5.1: In-App Messaging
 */

import { messageAPI, trainerAPI, clientAPI } from './api.js';
import { showToast } from './main.js';

// Global state
let currentUser = { type: 'trainer', id: 1 }; // TODO: Get from auth/session
let currentThreadId = null;
let socket = null;
let threads = [];
let messages = {};

// Initialize Socket.IO connection
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
socket = io(API_BASE_URL);

socket.on('connect', () => {
  console.log('Connected to Socket.IO');
});

socket.on('disconnect', () => {
  console.log('Disconnected from Socket.IO');
});

socket.on('message_received', (messageData) => {
  if (messageData.thread_id === currentThreadId) {
    addMessageToUI(messageData);
    scrollToBottom();
  }
  // Update thread list badge
  updateThreadUnreadCount(messageData.thread_id);
  loadThreads();
});

// DOM Elements
const threadsList = document.getElementById('threads-list');
const chatPanel = document.getElementById('chat-panel');
const chatHeader = document.getElementById('chat-header');
const messagesArea = document.getElementById('messages-area');
const messageInputArea = document.getElementById('message-input-area');
const messageForm = document.getElementById('message-form');
const messageInput = document.getElementById('message-input');
const threadSearch = document.getElementById('thread-search');
const newThreadBtn = document.getElementById('new-thread-btn');
const newThreadModal = document.getElementById('new-thread-modal');
const newThreadForm = document.getElementById('new-thread-form');
const cancelThreadBtn = document.getElementById('cancel-thread-btn');
const archiveThreadBtn = document.getElementById('archive-thread-btn');
const unreadBadge = document.getElementById('unread-badge');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initializeSidebar();
  loadThreads();
  loadUnreadCount();
  setupEventListeners();
  
  // Load trainers and clients for new thread form
  loadRecipients();
});

function initializeSidebar() {
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const mobileOverlay = document.getElementById('mobile-overlay');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-expanded');
      document.getElementById('main-content').classList.toggle('main-content-expanded');
    });
  }

  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
      sidebar.classList.toggle('sidebar-mobile-open');
      mobileOverlay.classList.toggle('hidden');
    });
  }

  if (mobileOverlay) {
    mobileOverlay.addEventListener('click', () => {
      sidebar.classList.remove('sidebar-mobile-open');
      mobileOverlay.classList.add('hidden');
    });
  }
}

function setupEventListeners() {
  // New thread button
  newThreadBtn.addEventListener('click', () => {
    newThreadModal.classList.remove('hidden');
  });

  // Cancel new thread
  cancelThreadBtn.addEventListener('click', () => {
    newThreadModal.classList.add('hidden');
    newThreadForm.reset();
  });

  // New thread form submission
  newThreadForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await createNewThread();
  });

  // Message form submission
  messageForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await sendMessage();
  });

  // Thread search
  threadSearch.addEventListener('input', (e) => {
    filterThreads(e.target.value);
  });

  // Archive thread
  archiveThreadBtn.addEventListener('click', async () => {
    if (currentThreadId) {
      await archiveThread(currentThreadId);
    }
  });

  // Auto-resize textarea
  messageInput.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = messageInput.scrollHeight + 'px';
  });
}

async function loadThreads() {
  try {
    const response = await messageAPI.getThreads({
      user_type: currentUser.type,
      user_id: currentUser.id,
      archived: false
    });

    threads = response.data.threads || [];
    renderThreads();
  } catch (error) {
    console.error('Error loading threads:', error);
    showToast('Failed to load conversations', 'error');
  }
}

function renderThreads() {
  if (threads.length === 0) {
    threadsList.innerHTML = `
      <div class="p-8 text-center text-gray-500">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path>
        </svg>
        <p>No conversations yet</p>
        <button class="mt-4 text-orange-500 hover:text-orange-600 font-medium" onclick="document.getElementById('new-thread-btn').click()">
          Start a conversation
        </button>
      </div>
    `;
    return;
  }

  threadsList.innerHTML = threads.map(thread => {
    const otherUser = currentUser.type === 'trainer' ? thread.client : thread.trainer;
    const unreadCount = currentUser.type === 'trainer' ? thread.trainer_unread_count : thread.client_unread_count;
    const lastMessagePreview = thread.last_message_by === currentUser.type ? 'You: ' : '';
    
    return `
      <div class="thread-item p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${thread.id === currentThreadId ? 'bg-orange-50 border-l-4 border-l-orange-500' : ''}" 
           data-thread-id="${thread.id}">
        <div class="flex items-start space-x-3">
          <div class="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
            ${getInitials(otherUser?.name || 'Unknown')}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between mb-1">
              <h4 class="font-semibold text-gray-900 truncate">${otherUser?.name || 'Unknown'}</h4>
              ${unreadCount > 0 ? `<span class="bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">${unreadCount}</span>` : ''}
            </div>
            <p class="text-sm text-gray-500 truncate">${lastMessagePreview}${thread.subject || 'No subject'}</p>
            <p class="text-xs text-gray-400 mt-1">${formatTime(thread.last_message_at)}</p>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Add click listeners
  document.querySelectorAll('.thread-item').forEach(item => {
    item.addEventListener('click', () => {
      const threadId = parseInt(item.dataset.threadId);
      selectThread(threadId);
    });
  });
}

function filterThreads(query) {
  const items = document.querySelectorAll('.thread-item');
  items.forEach(item => {
    const text = item.textContent.toLowerCase();
    item.style.display = text.includes(query.toLowerCase()) ? '' : 'none';
  });
}

async function selectThread(threadId) {
  currentThreadId = threadId;
  
  // Update UI
  document.querySelectorAll('.thread-item').forEach(item => {
    item.classList.remove('bg-orange-50', 'border-l-4', 'border-l-orange-500');
    if (parseInt(item.dataset.threadId) === threadId) {
      item.classList.add('bg-orange-50', 'border-l-4', 'border-l-orange-500');
    }
  });

  // Show chat panel
  chatPanel.classList.remove('hidden');
  messageInputArea.classList.remove('hidden');

  // Load thread details and messages
  await loadThread(threadId);
  
  // Join Socket.IO room
  socket.emit('join_thread', { thread_id: threadId });
  
  // Mark as read
  await markThreadAsRead(threadId);
}

async function loadThread(threadId) {
  try {
    const response = await messageAPI.getThread(threadId, { page: 1, per_page: 50 });
    const thread = response.data.thread;
    
    // Update chat header
    const otherUser = currentUser.type === 'trainer' ? thread.client : thread.trainer;
    document.getElementById('chat-name').textContent = otherUser?.name || 'Unknown';
    document.getElementById('chat-subtitle').textContent = otherUser?.email || '';
    document.getElementById('chat-initials').textContent = getInitials(otherUser?.name || '--');
    
    // Render messages
    messages[threadId] = thread.messages || [];
    renderMessages(thread.messages || []);
    
    scrollToBottom();
  } catch (error) {
    console.error('Error loading thread:', error);
    showToast('Failed to load conversation', 'error');
  }
}

function renderMessages(messagesList) {
  if (messagesList.length === 0) {
    messagesArea.innerHTML = `
      <div class="text-center text-gray-500 py-8">
        <p>No messages yet. Start the conversation!</p>
      </div>
    `;
    return;
  }

  messagesArea.innerHTML = messagesList.map(message => {
    const isOwn = message.sender_type === currentUser.type && message.sender_id === currentUser.id;
    return `
      <div class="flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4">
        <div class="max-w-xs lg:max-w-md ${isOwn ? 'bg-orange-500 text-white' : 'bg-white text-gray-900'} rounded-lg px-4 py-2 shadow-sm">
          <p class="text-sm whitespace-pre-wrap">${escapeHtml(message.content)}</p>
          <p class="text-xs mt-1 ${isOwn ? 'text-orange-100' : 'text-gray-400'}">
            ${formatTime(message.created_at)} ${message.read && isOwn ? '✓✓' : ''}
          </p>
        </div>
      </div>
    `;
  }).join('');
}

function addMessageToUI(message) {
  const isOwn = message.sender_type === currentUser.type && message.sender_id === currentUser.id;
  const messageHtml = `
    <div class="flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4">
      <div class="max-w-xs lg:max-w-md ${isOwn ? 'bg-orange-500 text-white' : 'bg-white text-gray-900'} rounded-lg px-4 py-2 shadow-sm">
        <p class="text-sm whitespace-pre-wrap">${escapeHtml(message.content)}</p>
        <p class="text-xs mt-1 ${isOwn ? 'text-orange-100' : 'text-gray-400'}">
          ${formatTime(message.created_at)} ${message.read && isOwn ? '✓✓' : ''}
        </p>
      </div>
    </div>
  `;
  messagesArea.insertAdjacentHTML('beforeend', messageHtml);
}

async function sendMessage() {
  const content = messageInput.value.trim();
  if (!content || !currentThreadId) return;

  try {
    const response = await messageAPI.createMessage(currentThreadId, {
      sender_type: currentUser.type,
      sender_id: currentUser.id,
      content: content
    });

    const message = response.data.message;
    
    // Add to UI
    addMessageToUI(message);
    
    // Broadcast via Socket.IO
    socket.emit('new_message', {
      thread_id: currentThreadId,
      message: message
    });

    // Clear input
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Reload threads to update last message
    loadThreads();
    
    scrollToBottom();
  } catch (error) {
    console.error('Error sending message:', error);
    showToast('Failed to send message', 'error');
  }
}

async function createNewThread() {
  const recipientId = parseInt(document.getElementById('recipient-select').value);
  const subject = document.getElementById('thread-subject').value.trim();
  const initialMessage = document.getElementById('initial-message').value.trim();

  if (!recipientId || !initialMessage) {
    showToast('Please select a recipient and enter a message', 'error');
    return;
  }

  try {
    const recipientType = document.getElementById('recipient-select').dataset.recipientType;
    const trainerId = currentUser.type === 'trainer' ? currentUser.id : recipientId;
    const clientId = currentUser.type === 'client' ? currentUser.id : recipientId;

    const response = await messageAPI.createThread({
      trainer_id: trainerId,
      client_id: clientId,
      subject: subject,
      initial_message: initialMessage,
      sender_type: currentUser.type
    });

    const thread = response.data.thread;
    
    // Close modal
    newThreadModal.classList.add('hidden');
    newThreadForm.reset();
    
    // Reload threads and select new thread
    await loadThreads();
    await selectThread(thread.id);
    
    showToast('Message sent successfully', 'success');
  } catch (error) {
    console.error('Error creating thread:', error);
    showToast('Failed to send message', 'error');
  }
}

async function markThreadAsRead(threadId) {
  try {
    await messageAPI.markThreadRead(threadId, {
      user_type: currentUser.type
    });
    loadUnreadCount();
    loadThreads();
  } catch (error) {
    console.error('Error marking thread as read:', error);
  }
}

async function archiveThread(threadId) {
  try {
    await messageAPI.archiveThread(threadId, {
      user_type: currentUser.type,
      archived: true
    });
    showToast('Conversation archived', 'success');
    currentThreadId = null;
    chatPanel.classList.add('hidden');
    loadThreads();
  } catch (error) {
    console.error('Error archiving thread:', error);
    showToast('Failed to archive conversation', 'error');
  }
}

async function loadUnreadCount() {
  try {
    const response = await messageAPI.getUnreadCount({
      user_type: currentUser.type,
      user_id: currentUser.id
    });
    const count = response.data.unread_count || 0;
    if (count > 0) {
      unreadBadge.textContent = count;
      unreadBadge.classList.remove('hidden');
    } else {
      unreadBadge.classList.add('hidden');
    }
  } catch (error) {
    console.error('Error loading unread count:', error);
  }
}

function updateThreadUnreadCount(threadId) {
  // This will be called when a new message is received
  loadUnreadCount();
}

async function loadRecipients() {
  try {
    const [trainersRes, clientsRes] = await Promise.all([
      trainerAPI.getAll(),
      clientAPI.getAll()
    ]);

    const select = document.getElementById('recipient-select');
    select.innerHTML = '<option value="">Select recipient...</option>';

    // Add trainers if current user is not a trainer
    if (currentUser.type !== 'trainer') {
      trainersRes.data.trainers?.forEach(trainer => {
        const option = document.createElement('option');
        option.value = trainer.id;
        option.textContent = trainer.name;
        option.dataset.recipientType = 'trainer';
        select.appendChild(option);
      });
    }

    // Add clients if current user is not a client
    if (currentUser.type !== 'client') {
      clientsRes.data.clients?.forEach(client => {
        const option = document.createElement('option');
        option.value = client.id;
        option.textContent = client.name;
        option.dataset.recipientType = 'client';
        select.appendChild(option);
      });
    }
  } catch (error) {
    console.error('Error loading recipients:', error);
  }
}

// Utility functions
function getInitials(name) {
  if (!name) return '--';
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}

function formatTime(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function scrollToBottom() {
  messagesArea.scrollTop = messagesArea.scrollHeight;
}

// Auto-refresh unread count every 30 seconds
setInterval(() => {
  loadUnreadCount();
}, 30000);

