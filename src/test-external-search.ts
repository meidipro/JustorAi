// Test script for external search functionality
// Run this to verify the external search services work correctly

import { ExternalSearchService } from './services/external-search-providers';
import { EnhancedSearchService } from './services/enhanced-search';

async function testExternalSearch() {
  console.log('🔍 Testing External Search Services...\n');

  try {
    // Test external search providers
    const externalSearch = new ExternalSearchService();
    
    console.log('1. Testing Web Search Provider...');
    const webResults = await externalSearch.searchAll('arrest rights Bangladesh police', {
      maxResults: 3,
      language: 'en'
    });
    console.log(`   Found ${webResults.length} results from web search`);
    webResults.forEach((result, i) => {
      console.log(`   ${i + 1}. ${result.title} (${result.source}, reliability: ${result.reliability})`);
    });
    console.log('');

    // Test enhanced search service
    console.log('2. Testing Enhanced Search Service...');
    const enhancedSearch = new EnhancedSearchService();
    
    // Test with low confidence to trigger external search
    const mockInternalResponse = "I don't have specific information about arrest rights in Bangladesh.";
    const lowConfidence = 0.3;
    
    const enhancedResponse = await enhancedSearch.generateEnhancedResponse(
      'What are my rights if arrested by police in Bangladesh?',
      mockInternalResponse,
      lowConfidence,
      'test-user'
    );
    
    console.log(`   Search triggered: ${enhancedResponse.searchTriggered}`);
    console.log(`   Response type: ${enhancedResponse.responseType}`);
    console.log(`   Final confidence: ${enhancedResponse.confidence.toFixed(2)}`);
    console.log(`   Sources found: ${enhancedResponse.sources.length}`);
    if (enhancedResponse.searchMetrics) {
      console.log(`   Search time: ${enhancedResponse.searchMetrics.searchTime}ms`);
      console.log(`   Providers used: ${enhancedResponse.searchMetrics.providersUsed.join(', ')}`);
    }
    console.log('');

    // Test analytics
    console.log('3. Testing Search Analytics...');
    const analytics = enhancedSearch.getAnalytics();
    console.log(`   Total searches recorded: ${analytics.totalSearches}`);
    console.log(`   Average response time: ${analytics.averageResponseTime}ms`);
    console.log(`   Success rate: ${analytics.successRate}%`);
    
    const realTimeStats = enhancedSearch.getRealTimeStats();
    console.log(`   Searches in last 24h: ${realTimeStats.searchesLast24Hours}`);
    console.log(`   Cache hit rate: ${realTimeStats.currentCacheHitRate}%`);
    console.log('');

    // Test cache functionality
    console.log('4. Testing Cache Functionality...');
    const cacheStats = enhancedSearch.getCacheStats();
    console.log(`   Cache entries: ${cacheStats.size}`);
    
    // Test another search (should be faster due to caching)
    const startTime = Date.now();
    await enhancedSearch.generateEnhancedResponse(
      'What are my rights if arrested by police in Bangladesh?', // Same query
      mockInternalResponse,
      lowConfidence,
      'test-user-2'
    );
    const cachedSearchTime = Date.now() - startTime;
    console.log(`   Cached search time: ${cachedSearchTime}ms`);
    console.log('');

    // Test quality insights
    console.log('5. Testing Quality Insights...');
    const insights = enhancedSearch.getQualityInsights();
    console.log(`   Suggestions: ${insights.suggestions.length}`);
    insights.suggestions.forEach((suggestion, i) => {
      console.log(`   ${i + 1}. ${suggestion}`);
    });
    console.log(`   Low confidence queries: ${insights.lowConfidenceQueries.length}`);
    console.log('');

    console.log('✅ All external search tests completed successfully!\n');
    
    // Display sample response
    console.log('📄 Sample Enhanced Response:');
    console.log('─'.repeat(50));
    console.log(enhancedResponse.answer.substring(0, 300) + '...');
    console.log('─'.repeat(50));

  } catch (error) {
    console.error('❌ Test failed:', error);
    if (error instanceof Error) {
      console.error('Error details:', error.message);
      console.error('Stack trace:', error.stack);
    }
  }
}

// Test different query categories
async function testCategorySearch() {
  console.log('\n🔍 Testing Category-Specific Searches...\n');
  
  const enhancedSearch = new EnhancedSearchService();
  const testQueries = [
    { query: 'property ownership rights Bangladesh', category: 'property law' },
    { query: 'divorce procedure in Bangladesh', category: 'family law' },
    { query: 'employment rights and labor law', category: 'labor law' },
    { query: 'constitutional rights and freedoms', category: 'constitutional law' }
  ];

  for (const test of testQueries) {
    console.log(`Testing ${test.category}: "${test.query}"`);
    try {
      const response = await enhancedSearch.generateEnhancedResponse(
        test.query,
        'Generic legal advice.',
        0.4, // Low confidence to trigger external search
        'category-test-user'
      );
      
      console.log(`   External search triggered: ${response.searchTriggered}`);
      console.log(`   Sources found: ${response.sources.length}`);
      console.log(`   Response type: ${response.responseType}`);
      console.log('');
    } catch (error) {
      console.error(`   ❌ Failed: ${error instanceof Error ? error.message : error}`);
    }
  }
}

// Performance test
async function testPerformance() {
  console.log('\n⚡ Performance Testing...\n');
  
  const enhancedSearch = new EnhancedSearchService();
  const testQueries = [
    'legal aid services Bangladesh',
    'court procedures and filing',
    'human rights protection',
    'criminal law penalties',
    'civil procedure rules'
  ];

  const times: number[] = [];
  
  for (let i = 0; i < testQueries.length; i++) {
    const query = testQueries[i];
    console.log(`Test ${i + 1}: "${query}"`);
    
    const startTime = Date.now();
    try {
      await enhancedSearch.generateEnhancedResponse(
        query,
        'Generic response.',
        0.3,
        `perf-test-user-${i}`
      );
      const responseTime = Date.now() - startTime;
      times.push(responseTime);
      console.log(`   Response time: ${responseTime}ms`);
    } catch (error) {
      console.error(`   ❌ Failed: ${error instanceof Error ? error.message : error}`);
    }
  }
  
  if (times.length > 0) {
    const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
    const minTime = Math.min(...times);
    const maxTime = Math.max(...times);
    
    console.log('\n📊 Performance Summary:');
    console.log(`   Average response time: ${avgTime.toFixed(2)}ms`);
    console.log(`   Fastest response: ${minTime}ms`);
    console.log(`   Slowest response: ${maxTime}ms`);
    console.log(`   Total tests: ${times.length}`);
  }
}

// Run all tests
async function runAllTests() {
  console.log('🚀 Starting Comprehensive External Search Tests\n');
  console.log('=' .repeat(60));
  
  await testExternalSearch();
  await testCategorySearch();
  await testPerformance();
  
  console.log('\n' + '='.repeat(60));
  console.log('🎉 All tests completed! Check the console output above for results.');
}

// Export for use in browser console or Node.js
if (typeof window !== 'undefined') {
  // Browser environment
  (window as any).testExternalSearch = runAllTests;
  console.log('💡 External search tests loaded! Run testExternalSearch() in the console to test.');
} else {
  // Node.js environment
  runAllTests();
}

export { testExternalSearch, testCategorySearch, testPerformance, runAllTests };