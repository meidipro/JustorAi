// Search Analytics Service
// Monitors search performance, usage patterns, and quality metrics

interface SearchMetrics {
  searchId: string;
  timestamp: Date;
  query: string;
  queryCategory: string;
  userId: string;
  responseTime: number;
  externalResultsFound: number;
  providersUsed: string[];
  confidenceScore: number;
  searchTriggered: boolean;
  responseType: 'internal' | 'enhanced' | 'hybrid';
  userFeedback?: 'good' | 'bad';
  errorOccurred?: boolean;
  errorMessage?: string;
}

interface SearchAnalytics {
  totalSearches: number;
  averageResponseTime: number;
  successRate: number;
  topQueries: { query: string; count: number }[];
  topCategories: { category: string; count: number }[];
  providerEffectiveness: { provider: string; avgResults: number; avgResponseTime: number }[];
  userSatisfaction: number; // Percentage of positive feedback
}

class SearchAnalyticsService {
  private metrics: SearchMetrics[] = [];
  private maxStoredMetrics = 1000; // Store last 1000 searches in memory
  
  /**
   * Record a search operation
   */
  recordSearch(metrics: Partial<SearchMetrics>): void {
    const searchMetric: SearchMetrics = {
      searchId: this.generateSearchId(),
      timestamp: new Date(),
      userId: metrics.userId || 'anonymous',
      query: metrics.query || '',
      queryCategory: metrics.queryCategory || 'unknown',
      responseTime: metrics.responseTime || 0,
      externalResultsFound: metrics.externalResultsFound || 0,
      providersUsed: metrics.providersUsed || [],
      confidenceScore: metrics.confidenceScore || 0,
      searchTriggered: metrics.searchTriggered || false,
      responseType: metrics.responseType || 'internal',
      errorOccurred: metrics.errorOccurred || false,
      errorMessage: metrics.errorMessage
    };

    this.metrics.push(searchMetric);
    
    // Keep only the most recent metrics to prevent memory issues
    if (this.metrics.length > this.maxStoredMetrics) {
      this.metrics = this.metrics.slice(-this.maxStoredMetrics);
    }

    // Log important metrics
    console.log(`📊 Search recorded: ${searchMetric.query.substring(0, 50)}... (${searchMetric.responseTime}ms, ${searchMetric.externalResultsFound} results)`);
  }

  /**
   * Record user feedback for a search
   */
  recordFeedback(searchId: string, feedback: 'good' | 'bad'): void {
    const metric = this.metrics.find(m => m.searchId === searchId);
    if (metric) {
      metric.userFeedback = feedback;
      console.log(`📊 Feedback recorded for search ${searchId}: ${feedback}`);
    }
  }

  /**
   * Get comprehensive search analytics
   */
  getAnalytics(timeRange?: { from: Date; to: Date }): SearchAnalytics {
    let relevantMetrics = this.metrics;
    
    if (timeRange) {
      relevantMetrics = this.metrics.filter(m => 
        m.timestamp >= timeRange.from && m.timestamp <= timeRange.to
      );
    }

    if (relevantMetrics.length === 0) {
      return this.getEmptyAnalytics();
    }

    // Calculate basic metrics
    const totalSearches = relevantMetrics.length;
    const averageResponseTime = relevantMetrics.reduce((sum, m) => sum + m.responseTime, 0) / totalSearches;
    const successfulSearches = relevantMetrics.filter(m => !m.errorOccurred).length;
    const successRate = (successfulSearches / totalSearches) * 100;

    // Top queries
    const queryCount = new Map<string, number>();
    relevantMetrics.forEach(m => {
      const count = queryCount.get(m.query) || 0;
      queryCount.set(m.query, count + 1);
    });
    const topQueries = Array.from(queryCount.entries())
      .map(([query, count]) => ({ query, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // Top categories
    const categoryCount = new Map<string, number>();
    relevantMetrics.forEach(m => {
      const count = categoryCount.get(m.queryCategory) || 0;
      categoryCount.set(m.queryCategory, count + 1);
    });
    const topCategories = Array.from(categoryCount.entries())
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);

    // Provider effectiveness
    const providerStats = new Map<string, { totalResults: number; totalTime: number; count: number }>();
    relevantMetrics.forEach(m => {
      m.providersUsed.forEach(provider => {
        const stats = providerStats.get(provider) || { totalResults: 0, totalTime: 0, count: 0 };
        stats.totalResults += m.externalResultsFound;
        stats.totalTime += m.responseTime;
        stats.count += 1;
        providerStats.set(provider, stats);
      });
    });

    const providerEffectiveness = Array.from(providerStats.entries())
      .map(([provider, stats]) => ({
        provider,
        avgResults: stats.totalResults / stats.count,
        avgResponseTime: stats.totalTime / stats.count
      }))
      .sort((a, b) => b.avgResults - a.avgResults);

    // User satisfaction
    const feedbackMetrics = relevantMetrics.filter(m => m.userFeedback);
    const positiveFeedback = feedbackMetrics.filter(m => m.userFeedback === 'good').length;
    const userSatisfaction = feedbackMetrics.length > 0 ? (positiveFeedback / feedbackMetrics.length) * 100 : 0;

    return {
      totalSearches,
      averageResponseTime: Math.round(averageResponseTime),
      successRate: Math.round(successRate * 100) / 100,
      topQueries,
      topCategories,
      providerEffectiveness,
      userSatisfaction: Math.round(userSatisfaction * 100) / 100
    };
  }

  /**
   * Get real-time search statistics
   */
  getRealTimeStats(): {
    searchesLast24Hours: number;
    averageResponseTimeLast24Hours: number;
    mostSearchedCategoryToday: string;
    currentCacheHitRate: number;
  } {
    const last24Hours = new Date(Date.now() - 24 * 60 * 60 * 1000);
    const recentMetrics = this.metrics.filter(m => m.timestamp >= last24Hours);

    const searchesLast24Hours = recentMetrics.length;
    const averageResponseTimeLast24Hours = recentMetrics.length > 0 
      ? recentMetrics.reduce((sum, m) => sum + m.responseTime, 0) / recentMetrics.length 
      : 0;

    // Most searched category today
    const categoryCount = new Map<string, number>();
    recentMetrics.forEach(m => {
      const count = categoryCount.get(m.queryCategory) || 0;
      categoryCount.set(m.queryCategory, count + 1);
    });
    const mostSearchedCategoryToday = Array.from(categoryCount.entries())
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'unknown';

    // Cache hit rate (approximate based on response times)
    const fastResponses = recentMetrics.filter(m => m.responseTime < 500).length;
    const currentCacheHitRate = recentMetrics.length > 0 ? (fastResponses / recentMetrics.length) * 100 : 0;

    return {
      searchesLast24Hours,
      averageResponseTimeLast24Hours: Math.round(averageResponseTimeLast24Hours),
      mostSearchedCategoryToday,
      currentCacheHitRate: Math.round(currentCacheHitRate * 100) / 100
    };
  }

  /**
   * Export analytics data for external analysis
   */
  exportData(format: 'json' | 'csv' = 'json'): string {
    if (format === 'csv') {
      const headers = ['searchId', 'timestamp', 'query', 'queryCategory', 'responseTime', 'externalResultsFound', 'providersUsed', 'confidenceScore', 'responseType', 'userFeedback'];
      const csvData = [headers.join(',')];
      
      this.metrics.forEach(m => {
        const row = [
          m.searchId,
          m.timestamp.toISOString(),
          `"${m.query.replace(/"/g, '""')}"`,
          m.queryCategory,
          m.responseTime.toString(),
          m.externalResultsFound.toString(),
          `"${m.providersUsed.join(', ')}"`,
          m.confidenceScore.toString(),
          m.responseType,
          m.userFeedback || ''
        ];
        csvData.push(row.join(','));
      });
      
      return csvData.join('\n');
    }
    
    return JSON.stringify(this.metrics, null, 2);
  }

  /**
   * Clear old analytics data
   */
  clearOldData(olderThan: Date): void {
    const initialCount = this.metrics.length;
    this.metrics = this.metrics.filter(m => m.timestamp >= olderThan);
    const removedCount = initialCount - this.metrics.length;
    console.log(`📊 Cleared ${removedCount} old search metrics`);
  }

  /**
   * Get search quality insights
   */
  getQualityInsights(): {
    lowConfidenceQueries: { query: string; avgConfidence: number; count: number }[];
    highLatencyCategories: { category: string; avgResponseTime: number }[];
    underperformingProviders: { provider: string; successRate: number }[];
    suggestions: string[];
  } {
    // Low confidence queries
    const queryConfidence = new Map<string, { total: number; count: number }>();
    this.metrics.forEach(m => {
      const stats = queryConfidence.get(m.query) || { total: 0, count: 0 };
      stats.total += m.confidenceScore;
      stats.count += 1;
      queryConfidence.set(m.query, stats);
    });

    const lowConfidenceQueries = Array.from(queryConfidence.entries())
      .map(([query, stats]) => ({
        query,
        avgConfidence: stats.total / stats.count,
        count: stats.count
      }))
      .filter(item => item.avgConfidence < 0.7 && item.count > 1)
      .sort((a, b) => a.avgConfidence - b.avgConfidence)
      .slice(0, 5);

    // High latency categories
    const categoryLatency = new Map<string, { total: number; count: number }>();
    this.metrics.forEach(m => {
      const stats = categoryLatency.get(m.queryCategory) || { total: 0, count: 0 };
      stats.total += m.responseTime;
      stats.count += 1;
      categoryLatency.set(m.queryCategory, stats);
    });

    const highLatencyCategories = Array.from(categoryLatency.entries())
      .map(([category, stats]) => ({
        category,
        avgResponseTime: stats.total / stats.count
      }))
      .filter(item => item.avgResponseTime > 3000)
      .sort((a, b) => b.avgResponseTime - a.avgResponseTime)
      .slice(0, 3);

    // Generate suggestions
    const suggestions: string[] = [];
    if (lowConfidenceQueries.length > 0) {
      suggestions.push(`Consider improving knowledge base for queries like: "${lowConfidenceQueries[0].query}"`);
    }
    if (highLatencyCategories.length > 0) {
      suggestions.push(`Optimize search performance for ${highLatencyCategories[0].category} category`);
    }
    
    const analytics = this.getAnalytics();
    if (analytics.successRate < 95) {
      suggestions.push('Search success rate is below 95%, investigate API reliability');
    }
    if (analytics.userSatisfaction < 80) {
      suggestions.push('User satisfaction is below 80%, review response quality');
    }

    return {
      lowConfidenceQueries,
      highLatencyCategories,
      underperformingProviders: [], // Would need more data to implement
      suggestions
    };
  }

  private generateSearchId(): string {
    return `search_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
  }

  private getEmptyAnalytics(): SearchAnalytics {
    return {
      totalSearches: 0,
      averageResponseTime: 0,
      successRate: 0,
      topQueries: [],
      topCategories: [],
      providerEffectiveness: [],
      userSatisfaction: 0
    };
  }
}

export { SearchAnalyticsService };
export type { SearchMetrics, SearchAnalytics };