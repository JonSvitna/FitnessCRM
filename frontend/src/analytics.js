import { api } from './api.js';

// Chart instances
let charts = {};

// Tab switching
function setupTabs() {
  const tabs = document.querySelectorAll('.tab-button');
  const contents = document.querySelectorAll('.tab-content');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const tabId = tab.id.replace('tab-', '');
      
      // Update active states
      tabs.forEach(t => t.classList.remove('tab-button-active'));
      tab.classList.add('tab-button-active');
      
      // Show corresponding content
      contents.forEach(content => {
        if (content.id === `content-${tabId}`) {
          content.classList.remove('hidden');
          // Load data for this tab
          loadTabData(tabId);
        } else {
          content.classList.add('hidden');
        }
      });
    });
  });
}

// Loading overlay
function showLoading() {
  document.getElementById('loading-overlay').classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loading-overlay').classList.add('hidden');
}

// Load tab data
async function loadTabData(tabId) {
  showLoading();
  try {
    switch (tabId) {
      case 'overview':
        await loadOverviewData();
        break;
      case 'revenue':
        await loadRevenueData();
        break;
      case 'clients':
        await loadClientsData();
        break;
      case 'trainers':
        await loadTrainersData();
        break;
      case 'reports':
        await loadReportsData();
        break;
    }
  } catch (error) {
    console.error('Error loading tab data:', error);
    showNotification('Error loading data. Please try again.', 'error');
  } finally {
    hideLoading();
  }
}

// Overview Data
async function loadOverviewData() {
  try {
    const response = await api.get('/analytics/dashboard');
    const data = response.data;

    // Update metrics
    document.getElementById('overview-total-clients').textContent = data.clients.total;
    document.getElementById('overview-new-clients').textContent = data.clients.new_this_month;
    document.getElementById('overview-total-revenue').textContent = `$${data.revenue.total.toFixed(2)}`;
    document.getElementById('overview-month-revenue').textContent = data.revenue.this_month.toFixed(2);
    document.getElementById('overview-total-sessions').textContent = data.sessions.total;
    document.getElementById('overview-attendance-rate').textContent = data.sessions.attendance_rate;
    document.getElementById('overview-active-trainers').textContent = data.trainers.active;
    document.getElementById('overview-retention').textContent = data.clients.retention_rate;

    // Load revenue trend
    const revenueResponse = await api.get('/payments/revenue/dashboard');
    const revenueData = revenueResponse.data;
    
    // Create revenue trend chart
    createRevenueTrendChart(revenueData.monthly_trend);
    
    // Load client growth
    const clientResponse = await api.get('/analytics/clients/retention');
    const clientData = clientResponse.data;
    
    createClientGrowthChart(clientData.growth_trend);
  } catch (error) {
    console.error('Error loading overview data:', error);
  }
}

// Revenue Data
async function loadRevenueData() {
  try {
    const response = await api.get('/payments/revenue/dashboard');
    const data = response.data;

    // Update metrics
    document.getElementById('revenue-total').textContent = `$${data.total_revenue.toFixed(2)}`;
    document.getElementById('revenue-month').textContent = `$${data.revenue_this_month.toFixed(2)}`;
    document.getElementById('revenue-average').textContent = `$${data.average_payment.toFixed(2)}`;

    // Revenue by type chart
    createRevenueByTypeChart(data.revenue_by_type);

    // Monthly revenue chart
    createMonthlyRevenueChart(data.monthly_trend);

    // Top clients
    const reportResponse = await api.get('/payments/revenue/report');
    const reportData = reportResponse.data;
    displayTopClients(reportData.top_clients);
  } catch (error) {
    console.error('Error loading revenue data:', error);
  }
}

// Client Analytics Data
async function loadClientsData() {
  try {
    // Retention data
    const retentionResponse = await api.get('/analytics/clients/retention');
    const retentionData = retentionResponse.data;

    document.getElementById('clients-total').textContent = retentionData.total_clients;
    document.getElementById('clients-active').textContent = retentionData.active_clients;
    document.getElementById('clients-retention').textContent = retentionData.retention_rate;
    document.getElementById('clients-churn').textContent = retentionData.churn_rate;

    // Status breakdown chart
    createClientStatusChart(retentionData.status_breakdown);

    // Engagement data
    const engagementResponse = await api.get('/analytics/clients/engagement');
    const engagementData = engagementResponse.data;

    document.getElementById('engagement-attendance').textContent = engagementData.attendance_rate;
    document.getElementById('engagement-avg-sessions').textContent = engagementData.avg_sessions_per_client.toFixed(1);
    document.getElementById('engagement-workout-logs').textContent = engagementData.workout_logs_completed;

    // Activity levels chart
    createActivityLevelsChart(engagementData.activity_levels);
  } catch (error) {
    console.error('Error loading clients data:', error);
  }
}

// Trainer Performance Data
async function loadTrainersData() {
  try {
    const response = await api.get('/analytics/trainers/performance');
    const data = response.data;

    // Display trainer cards
    const grid = document.getElementById('trainer-performance-grid');
    grid.innerHTML = data.trainers.map(trainer => `
      <div class="card hover:shadow-lg transition-shadow">
        <h4 class="font-semibold text-gray-800 mb-3">${trainer.trainer_name}</h4>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-600">Sessions:</span>
            <span class="font-semibold">${trainer.sessions_completed}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Hours:</span>
            <span class="font-semibold">${trainer.total_hours}h</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Revenue:</span>
            <span class="font-semibold text-green-600">$${trainer.revenue_generated.toFixed(2)}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Clients:</span>
            <span class="font-semibold">${trainer.active_clients}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">Utilization:</span>
            <span class="font-semibold ${trainer.utilization_rate > 75 ? 'text-green-600' : trainer.utilization_rate > 50 ? 'text-yellow-600' : 'text-red-600'}">
              ${trainer.utilization_rate.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    `).join('');

    // Create comparison chart
    createTrainerComparisonChart(data.trainers);
  } catch (error) {
    console.error('Error loading trainers data:', error);
  }
}

// Custom Reports Data
async function loadReportsData() {
  try {
    // Load templates
    const templatesResponse = await api.get('/reports/templates');
    const templates = templatesResponse.data.templates;

    const templatesGrid = document.getElementById('report-templates');
    templatesGrid.innerHTML = templates.map(template => `
      <div class="card hover:shadow-lg transition-shadow cursor-pointer" onclick="generateFromTemplate('${template.id}')">
        <h4 class="font-semibold text-gray-800 mb-2">${template.name}</h4>
        <p class="text-sm text-gray-600 mb-3">${template.description}</p>
        <button class="btn-secondary text-sm py-2">Generate Report</button>
      </div>
    `).join('');

    // Load available metrics
    const metricsResponse = await api.get('/reports/available-metrics');
    const metrics = metricsResponse.data.metrics;

    const metricsContainer = document.getElementById('metrics-checkboxes');
    metricsContainer.innerHTML = metrics.map(metric => `
      <label class="flex items-center space-x-2 cursor-pointer">
        <input type="checkbox" value="${metric.id}" class="metric-checkbox form-checkbox h-5 w-5 text-primary-600 rounded focus:ring-primary-500">
        <span class="text-sm text-gray-700">${metric.name}</span>
      </label>
    `).join('');
  } catch (error) {
    console.error('Error loading reports data:', error);
  }
}

// Chart creation functions
function createRevenueTrendChart(data) {
  const ctx = document.getElementById('revenue-trend-chart');
  if (!ctx) return;

  if (charts.revenueTrend) {
    charts.revenueTrend.destroy();
  }

  charts.revenueTrend = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => d.month),
      datasets: [{
        label: 'Revenue',
        data: data.map(d => d.revenue),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => '$' + value.toFixed(0)
          }
        }
      }
    }
  });
}

function createClientGrowthChart(data) {
  const ctx = document.getElementById('client-growth-chart');
  if (!ctx) return;

  if (charts.clientGrowth) {
    charts.clientGrowth.destroy();
  }

  charts.clientGrowth = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.month),
      datasets: [{
        label: 'New Clients',
        data: data.map(d => d.new_clients),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  });
}

function createRevenueByTypeChart(data) {
  const ctx = document.getElementById('revenue-by-type-chart');
  if (!ctx) return;

  if (charts.revenueByType) {
    charts.revenueByType.destroy();
  }

  const labels = Object.keys(data);
  const values = Object.values(data);

  charts.revenueByType = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels.map(l => l.replace('_', ' ').toUpperCase()),
      datasets: [{
        data: values,
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(168, 85, 247, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

function createMonthlyRevenueChart(data) {
  const ctx = document.getElementById('revenue-monthly-chart');
  if (!ctx) return;

  if (charts.monthlyRevenue) {
    charts.monthlyRevenue.destroy();
  }

  charts.monthlyRevenue = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => d.month),
      datasets: [{
        label: 'Monthly Revenue',
        data: data.map(d => d.revenue),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => '$' + value.toFixed(0)
          }
        }
      }
    }
  });
}

function createClientStatusChart(data) {
  const ctx = document.getElementById('client-status-chart');
  if (!ctx) return;

  if (charts.clientStatus) {
    charts.clientStatus.destroy();
  }

  const labels = Object.keys(data);
  const values = Object.values(data);

  charts.clientStatus = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels.map(l => l.toUpperCase()),
      datasets: [{
        data: values,
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(251, 191, 36, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

function createActivityLevelsChart(data) {
  const ctx = document.getElementById('client-activity-chart');
  if (!ctx) return;

  if (charts.activityLevels) {
    charts.activityLevels.destroy();
  }

  charts.activityLevels = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Highly Active', 'Moderately Active', 'Low Active', 'Inactive'],
      datasets: [{
        label: 'Number of Clients',
        data: [
          data.highly_active,
          data.moderately_active,
          data.low_active,
          data.inactive
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  });
}

function createTrainerComparisonChart(trainers) {
  const ctx = document.getElementById('trainer-comparison-chart');
  if (!ctx) return;

  if (charts.trainerComparison) {
    charts.trainerComparison.destroy();
  }

  charts.trainerComparison = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: trainers.map(t => t.trainer_name),
      datasets: [
        {
          label: 'Sessions',
          data: trainers.map(t => t.sessions_completed),
          backgroundColor: 'rgba(59, 130, 246, 0.8)'
        },
        {
          label: 'Revenue ($)',
          data: trainers.map(t => t.revenue_generated),
          backgroundColor: 'rgba(34, 197, 94, 0.8)'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

function displayTopClients(clients) {
  const container = document.getElementById('top-clients-list');
  if (!container) return;

  container.innerHTML = clients.map((client, index) => `
    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
      <div class="flex items-center space-x-3">
        <span class="flex items-center justify-center w-8 h-8 rounded-full ${
          index < 3 ? 'bg-orange-500 text-white font-bold' : 'bg-gray-300 text-gray-700'
        } text-sm">
          ${index + 1}
        </span>
        <span class="font-medium text-gray-800">${client.client_name}</span>
      </div>
      <span class="font-semibold text-green-600">$${client.total.toFixed(2)}</span>
    </div>
  `).join('');
}

// Custom report generation
async function generateCustomReport() {
  const reportName = document.getElementById('custom-report-name').value || 'Custom Report';
  const startDate = document.getElementById('custom-report-start').value;
  const endDate = document.getElementById('custom-report-end').value;
  
  const selectedMetrics = Array.from(document.querySelectorAll('.metric-checkbox:checked'))
    .map(cb => cb.value);

  if (selectedMetrics.length === 0) {
    showNotification('Please select at least one metric', 'error');
    return;
  }

  showLoading();
  try {
    const response = await api.post('/reports/custom', {
      name: reportName,
      metrics: selectedMetrics,
      start_date: startDate,
      end_date: endDate
    });

    const reportData = response.data;
    displayCustomReportResults(reportData);
    
    // Enable export button
    document.getElementById('export-report-btn').disabled = false;
    document.getElementById('export-report-btn').dataset.reportData = JSON.stringify(reportData);
    
    showNotification('Report generated successfully!', 'success');
  } catch (error) {
    console.error('Error generating report:', error);
    showNotification('Error generating report. Please try again.', 'error');
  } finally {
    hideLoading();
  }
}

function displayCustomReportResults(data) {
  const container = document.getElementById('custom-report-results');
  const content = document.getElementById('report-results-content');
  
  container.classList.remove('hidden');
  
  let html = `
    <div class="mb-4">
      <h4 class="font-semibold text-gray-800">${data.report_name}</h4>
      <p class="text-sm text-gray-600">Generated: ${new Date(data.generated_at).toLocaleString()}</p>
      <p class="text-sm text-gray-600">Date Range: ${data.date_range.start} to ${data.date_range.end}</p>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  `;
  
  for (const [key, value] of Object.entries(data.metrics)) {
    if (typeof value === 'object' && !Array.isArray(value)) {
      html += `
        <div class="col-span-full card bg-gray-50">
          <h5 class="font-semibold text-gray-700 mb-2">${key.replace(/_/g, ' ').toUpperCase()}</h5>
          ${Object.entries(value).map(([k, v]) => `
            <div class="flex justify-between text-sm py-1">
              <span class="text-gray-600">${k}:</span>
              <span class="font-medium">${typeof v === 'number' ? v.toFixed(2) : v}</span>
            </div>
          `).join('')}
        </div>
      `;
    } else if (Array.isArray(value)) {
      html += `
        <div class="col-span-full card bg-gray-50">
          <h5 class="font-semibold text-gray-700 mb-2">${key.replace(/_/g, ' ').toUpperCase()}</h5>
          <div class="max-h-60 overflow-y-auto">
            ${value.map(item => {
              if (typeof item === 'object') {
                // Format objects in a readable way
                return `<div class="text-sm py-2 border-b border-gray-200 last:border-0">
                  ${Object.entries(item).map(([k, v]) => 
                    `<span class="inline-block mr-4"><strong>${k}:</strong> ${v}</span>`
                  ).join('')}
                </div>`;
              }
              return `<div class="text-sm py-1 border-b border-gray-200 last:border-0">${item}</div>`;
            }).join('')}
          </div>
        </div>
      `;
    } else {
      html += `
        <div class="card bg-gradient-to-br from-blue-50 to-blue-100">
          <p class="text-sm text-blue-700 mb-1">${key.replace(/_/g, ' ').toUpperCase()}</p>
          <p class="text-2xl font-bold text-blue-900">${typeof value === 'number' ? value.toFixed(2) : value}</p>
        </div>
      `;
    }
  }
  
  html += '</div>';
  content.innerHTML = html;
}

async function exportCustomReport() {
  const reportDataStr = document.getElementById('export-report-btn').dataset.reportData;
  if (!reportDataStr) {
    showNotification('No report to export', 'error');
    return;
  }

  showLoading();
  try {
    const reportData = JSON.parse(reportDataStr);
    const response = await api.post('/reports/custom/export', {
      report_data: reportData
    }, {
      responseType: 'blob'
    });

    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `custom_report_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    showNotification('Report exported successfully!', 'success');
  } catch (error) {
    console.error('Error exporting report:', error);
    showNotification('Error exporting report. Please try again.', 'error');
  } finally {
    hideLoading();
  }
}

window.generateFromTemplate = async function(templateId) {
  showLoading();
  try {
    const response = await api.post(`/reports/templates/${templateId}`);
    const reportData = response.data;
    
    // Switch to reports tab if not already there
    document.getElementById('tab-reports').click();
    
    // Display results
    displayCustomReportResults(reportData);
    
    showNotification('Report generated from template!', 'success');
  } catch (error) {
    console.error('Error generating report from template:', error);
    showNotification('Error generating report. Please try again.', 'error');
  } finally {
    hideLoading();
  }
};

function showNotification(message, type = 'info') {
  // Simple notification - could be enhanced with a notification library
  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500',
    warning: 'bg-yellow-500'
  };
  
  // Default to info if invalid type provided
  const bgColor = colors[type] || colors.info;
  
  const notification = document.createElement('div');
  notification.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-opacity`;
  notification.textContent = message;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.opacity = '0';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  setupTabs();
  loadOverviewData(); // Load initial data
  
  // Set up event listeners
  document.getElementById('generate-report-btn')?.addEventListener('click', generateCustomReport);
  document.getElementById('export-report-btn')?.addEventListener('click', exportCustomReport);
  
  // Set default dates (last 30 days)
  const today = new Date();
  const thirtyDaysAgo = new Date(today);
  thirtyDaysAgo.setDate(today.getDate() - 30);
  
  document.getElementById('custom-report-end').valueAsDate = today;
  document.getElementById('custom-report-start').valueAsDate = thirtyDaysAgo;
});
