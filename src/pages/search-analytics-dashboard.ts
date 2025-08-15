// Search Analytics Dashboard
// Provides admin interface to view search performance and insights

import { EnhancedSearchService } from '../services/enhanced-search';

export async function renderSearchAnalyticsDashboard(container: HTMLElement) {
    // This would normally require admin authentication
    
    const enhancedSearch = new EnhancedSearchService(); // In real app, get from singleton
    
    container.innerHTML = `
        <div class="analytics-dashboard">
            <header class="dashboard-header">
                <h1>🔍 Search Analytics Dashboard</h1>
                <p>Monitor external search performance and user engagement</p>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Real-Time Statistics</h3>
                    <div id="realtime-stats"></div>
                </div>
                
                <div class="stat-card">
                    <h3>Search Performance</h3>
                    <div id="performance-stats"></div>
                </div>
                
                <div class="stat-card">
                    <h3>Top Queries</h3>
                    <div id="top-queries"></div>
                </div>
                
                <div class="stat-card">
                    <h3>Category Breakdown</h3>
                    <div id="category-stats"></div>
                </div>
                
                <div class="stat-card">
                    <h3>Provider Effectiveness</h3>
                    <div id="provider-stats"></div>
                </div>
                
                <div class="stat-card">
                    <h3>Quality Insights</h3>
                    <div id="quality-insights"></div>
                </div>
            </div>
            
            <div class="cache-controls">
                <h3>Cache Management</h3>
                <button id="clear-cache-btn" class="btn-primary">Clear Search Cache</button>
                <button id="export-data-btn" class="btn-secondary">Export Analytics Data</button>
                <div id="cache-stats"></div>
            </div>
        </div>
        
        <style>
            .analytics-dashboard {
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .dashboard-header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            .dashboard-header h1 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .stat-card {
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stat-card h3 {
                margin: 0 0 15px 0;
                color: #495057;
                border-bottom: 2px solid #007bff;
                padding-bottom: 8px;
            }
            
            .stat-item {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
                padding: 4px 0;
            }
            
            .stat-value {
                font-weight: bold;
                color: #007bff;
            }
            
            .cache-controls {
                background: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
            }
            
            .btn-primary, .btn-secondary {
                padding: 10px 20px;
                margin: 0 10px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            
            .btn-primary {
                background: #007bff;
                color: white;
            }
            
            .btn-secondary {
                background: #6c757d;
                color: white;
            }
            
            .btn-primary:hover, .btn-secondary:hover {
                opacity: 0.8;
            }
            
            .quality-insight {
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 10px;
                margin: 8px 0;
                border-radius: 0 4px 4px 0;
            }
            
            .low-confidence-query {
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 8px;
                margin: 4px 0;
                border-radius: 0 4px 4px 0;
                font-size: 14px;
            }
        </style>
    `;

    // Get DOM elements
    const realtimeStatsEl = document.getElementById('realtime-stats')!;
    const performanceStatsEl = document.getElementById('performance-stats')!;
    const topQueriesEl = document.getElementById('top-queries')!;
    const categoryStatsEl = document.getElementById('category-stats')!;
    const providerStatsEl = document.getElementById('provider-stats')!;
    const qualityInsightsEl = document.getElementById('quality-insights')!;
    const cacheStatsEl = document.getElementById('cache-stats')!;
    const clearCacheBtn = document.getElementById('clear-cache-btn')!;
    const exportDataBtn = document.getElementById('export-data-btn')!;

    function updateDashboard() {
        try {
            // Real-time stats
            const realTimeStats = enhancedSearch.getRealTimeStats();
            realtimeStatsEl.innerHTML = `
                <div class="stat-item">
                    <span>Searches (24h):</span>
                    <span class="stat-value">${realTimeStats.searchesLast24Hours}</span>
                </div>
                <div class="stat-item">
                    <span>Avg Response Time:</span>
                    <span class="stat-value">${realTimeStats.averageResponseTimeLast24Hours}ms</span>
                </div>
                <div class="stat-item">
                    <span>Top Category Today:</span>
                    <span class="stat-value">${realTimeStats.mostSearchedCategoryToday}</span>
                </div>
                <div class="stat-item">
                    <span>Cache Hit Rate:</span>
                    <span class="stat-value">${realTimeStats.currentCacheHitRate}%</span>
                </div>
            `;

            // Performance stats
            const analytics = enhancedSearch.getAnalytics();
            performanceStatsEl.innerHTML = `
                <div class="stat-item">
                    <span>Total Searches:</span>
                    <span class="stat-value">${analytics.totalSearches}</span>
                </div>
                <div class="stat-item">
                    <span>Average Response Time:</span>
                    <span class="stat-value">${analytics.averageResponseTime}ms</span>
                </div>
                <div class="stat-item">
                    <span>Success Rate:</span>
                    <span class="stat-value">${analytics.successRate}%</span>
                </div>
                <div class="stat-item">
                    <span>User Satisfaction:</span>
                    <span class="stat-value">${analytics.userSatisfaction}%</span>
                </div>
            `;

            // Top queries
            topQueriesEl.innerHTML = analytics.topQueries.length > 0 
                ? analytics.topQueries.map(q => `
                    <div class="stat-item">
                        <span title="${q.query}">${q.query.substring(0, 30)}${q.query.length > 30 ? '...' : ''}</span>
                        <span class="stat-value">${q.count}</span>
                    </div>
                `).join('')
                : '<p>No search data available yet</p>';

            // Category stats
            categoryStatsEl.innerHTML = analytics.topCategories.length > 0
                ? analytics.topCategories.map(c => `
                    <div class="stat-item">
                        <span>${c.category.replace('_', ' ').toUpperCase()}</span>
                        <span class="stat-value">${c.count}</span>
                    </div>
                `).join('')
                : '<p>No category data available yet</p>';

            // Provider effectiveness
            providerStatsEl.innerHTML = analytics.providerEffectiveness.length > 0
                ? analytics.providerEffectiveness.map(p => `
                    <div class="stat-item">
                        <span>${p.provider}</span>
                        <span class="stat-value">${p.avgResults.toFixed(1)} results</span>
                    </div>
                    <div class="stat-item" style="margin-left: 20px; font-size: 12px; color: #666;">
                        <span>Avg Response Time:</span>
                        <span>${p.avgResponseTime.toFixed(0)}ms</span>
                    </div>
                `).join('')
                : '<p>No provider data available yet</p>';

            // Quality insights
            const insights = enhancedSearch.getQualityInsights();
            let insightsHTML = '';
            
            if (insights.suggestions.length > 0) {
                insightsHTML += '<h4>Suggestions:</h4>';
                insights.suggestions.forEach(suggestion => {
                    insightsHTML += `<div class="quality-insight">💡 ${suggestion}</div>`;
                });
            }
            
            if (insights.lowConfidenceQueries.length > 0) {
                insightsHTML += '<h4>Low Confidence Queries:</h4>';
                insights.lowConfidenceQueries.forEach(query => {
                    insightsHTML += `
                        <div class="low-confidence-query">
                            <strong>${query.query.substring(0, 40)}${query.query.length > 40 ? '...' : ''}</strong><br>
                            Confidence: ${(query.avgConfidence * 100).toFixed(1)}% (${query.count} searches)
                        </div>
                    `;
                });
            }
            
            qualityInsightsEl.innerHTML = insightsHTML || '<p>No quality insights available yet</p>';

            // Cache stats
            const cacheStats = enhancedSearch.getCacheStats();
            cacheStatsEl.innerHTML = `
                <div class="stat-item">
                    <span>Cache Size:</span>
                    <span class="stat-value">${cacheStats.size} entries</span>
                </div>
            `;

        } catch (error) {
            console.error('Error updating dashboard:', error);
            container.innerHTML = `
                <div class="error-message">
                    <h2>⚠️ Dashboard Error</h2>
                    <p>Unable to load analytics data. This might be because:</p>
                    <ul>
                        <li>No search data has been collected yet</li>
                        <li>Analytics service is not properly initialized</li>
                        <li>There was a technical error: ${error instanceof Error ? error.message : 'Unknown error'}</li>
                    </ul>
                    <p>Try performing some searches first, then return to this dashboard.</p>
                </div>
                <style>
                    .error-message {
                        padding: 20px;
                        background: #f8d7da;
                        border: 1px solid #f5c6cb;
                        border-radius: 8px;
                        color: #721c24;
                        max-width: 600px;
                        margin: 50px auto;
                    }
                </style>
            `;
        }
    }

    // Event listeners
    clearCacheBtn.addEventListener('click', () => {
        enhancedSearch.clearCache();
        alert('Search cache cleared successfully!');
        updateDashboard();
    });

    exportDataBtn.addEventListener('click', () => {
        try {
            const analytics = enhancedSearch.getAnalytics();
            const dataStr = JSON.stringify(analytics, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            const url = URL.createObjectURL(dataBlob);
            
            const link = document.createElement('a');
            link.href = url;
            link.download = `search-analytics-${new Date().toISOString().slice(0, 10)}.json`;
            link.click();
            
            URL.revokeObjectURL(url);
        } catch (error) {
            alert('Error exporting data: ' + (error instanceof Error ? error.message : 'Unknown error'));
        }
    });

    // Initial load and periodic updates
    updateDashboard();
    
    // Update dashboard every 30 seconds
    const updateInterval = setInterval(updateDashboard, 30000);
    
    // Cleanup function (call this when leaving the page)
    return () => {
        clearInterval(updateInterval);
    };
}