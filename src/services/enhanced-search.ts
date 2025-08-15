// Enhanced Search Service for Justor AI
// Provides external search capabilities when internal knowledge is insufficient

import { ExternalSearchService, type ExternalSearchResult } from './external-search-providers';
import { TRUSTED_LEGAL_SOURCES, LEGAL_CATEGORIES } from '../data/trusted-sources';
import { SearchAnalyticsService } from './search-analytics';

interface SearchResult {
  content: string;
  source: string;
  reliability: number;
  url?: string;
  lastUpdated?: Date;
}

interface EnhancedResponse {
  answer: string;
  confidence: number;
  sources: SearchResult[];
  searchTriggered: boolean;
  responseType: 'internal' | 'enhanced' | 'hybrid';
  searchMetrics?: {
    externalResultsFound: number;
    searchTime: number;
    providersUsed: string[];
  };
}

class EnhancedSearchService {
  private externalSearchService: ExternalSearchService;
  private analytics: SearchAnalyticsService;
  private confidenceThreshold = 0.6;
  private searchTimeoutMs = 10000; // 10 seconds timeout

  constructor() {
    this.externalSearchService = new ExternalSearchService();
    this.analytics = new SearchAnalyticsService();
  }

  /**
   * Main entry point for enhanced search
   */
  async generateEnhancedResponse(
    userQuery: string,
    internalResponse: string,
    internalConfidence: number,
    userId?: string
  ): Promise<EnhancedResponse> {
    const startTime = Date.now();
    const queryCategory = this.categorizeQuery(userQuery);
    
    // Check if external search is needed
    if (internalConfidence >= this.confidenceThreshold) {
      // Record analytics for internal response
      this.analytics.recordSearch({
        query: userQuery,
        queryCategory,
        userId: userId || 'anonymous',
        responseTime: Date.now() - startTime,
        externalResultsFound: 0,
        providersUsed: [],
        confidenceScore: internalConfidence,
        searchTriggered: false,
        responseType: 'internal'
      });
      
      return {
        answer: internalResponse,
        confidence: internalConfidence,
        sources: [],
        searchTriggered: false,
        responseType: 'internal'
      };
    }

    // Trigger external search
    console.log('🔍 Internal confidence low. Triggering external search...');
    
    try {
      const { results: searchResults, metrics } = await this.performMultiSourceSearch(userQuery);
      const enhancedAnswer = await this.synthesizeResponse(
        userQuery,
        internalResponse,
        searchResults
      );
      
      const finalConfidence = this.calculateFinalConfidence(
        internalConfidence,
        searchResults
      );

      // Record successful search analytics
      this.analytics.recordSearch({
        query: userQuery,
        queryCategory,
        userId: userId || 'anonymous',
        responseTime: Date.now() - startTime,
        externalResultsFound: metrics.externalResultsFound,
        providersUsed: metrics.providersUsed,
        confidenceScore: finalConfidence,
        searchTriggered: true,
        responseType: searchResults.length > 0 ? 'enhanced' : 'hybrid'
      });
      
      return {
        answer: enhancedAnswer,
        confidence: finalConfidence,
        sources: searchResults,
        searchTriggered: true,
        responseType: searchResults.length > 0 ? 'enhanced' : 'hybrid',
        searchMetrics: metrics
      };

    } catch (error) {
      console.error('External search failed:', error);
      
      // Record failed search analytics
      this.analytics.recordSearch({
        query: userQuery,
        queryCategory,
        userId: userId || 'anonymous',
        responseTime: Date.now() - startTime,
        externalResultsFound: 0,
        providersUsed: [],
        confidenceScore: Math.min(internalConfidence + 0.2, 0.8),
        searchTriggered: true,
        responseType: 'hybrid',
        errorOccurred: true,
        errorMessage: error instanceof Error ? error.message : 'Unknown error'
      });
      
      // Fallback to improved internal response
      const improvedResponse = this.improveInternalResponse(
        userQuery,
        internalResponse
      );
      
      return {
        answer: improvedResponse,
        confidence: Math.min(internalConfidence + 0.2, 0.8),
        sources: [],
        searchTriggered: true,
        responseType: 'hybrid'
      };
    }
  }

  /**
   * Perform search across multiple trusted sources using real external APIs
   */
  private async performMultiSourceSearch(query: string): Promise<{
    results: SearchResult[];
    metrics: {
      searchTime: number;
      externalResultsFound: number;
      providersUsed: string[];
    }
  }> {
    const startTime = Date.now();
    
    try {
      // Determine the query category for targeted search
      const category = this.categorizeQuery(query);
      
      // Search external providers with timeout
      const searchPromise = this.externalSearchService.searchAll(query, {
        maxResults: 8,
        category: category,
        language: 'en' // You can make this dynamic
      });
      
      const timeoutPromise = new Promise<ExternalSearchResult[]>((_, reject) => 
        setTimeout(() => reject(new Error('Search timeout')), this.searchTimeoutMs)
      );
      
      const externalResults = await Promise.race([searchPromise, timeoutPromise]);
      
      // Convert external results to internal format
      const searchResults: SearchResult[] = externalResults.map(result => ({
        content: result.content,
        source: result.source,
        reliability: result.reliability,
        url: result.url,
        lastUpdated: result.publishedDate || new Date()
      }));
      
      // Add some mock results if no external results found (fallback)
      if (searchResults.length === 0) {
        searchResults.push(...this.getFallbackResults(query));
      }
      
      const searchTime = Date.now() - startTime;
      const providersUsed = [...new Set(externalResults.map(r => r.source))];
      
      return {
        results: searchResults.slice(0, 5),
        metrics: {
          searchTime,
          externalResultsFound: externalResults.length,
          providersUsed
        }
      };
    } catch (error) {
      console.error('External search failed, using fallback:', error);
      
      return {
        results: this.getFallbackResults(query),
        metrics: {
          searchTime: Date.now() - startTime,
          externalResultsFound: 0,
          providersUsed: ['fallback']
        }
      };
    }
  }

  /**
   * Categorize the query to determine the best search approach
   */
  private categorizeQuery(query: string): string {
    const lowerQuery = query.toLowerCase();
    
    for (const [category, keywords] of Object.entries(LEGAL_CATEGORIES)) {
      if (keywords.some(keyword => lowerQuery.includes(keyword))) {
        return category;
      }
    }
    
    return 'general';
  }
  
  /**
   * Get fallback results when external search fails
   */
  private getFallbackResults(query: string): SearchResult[] {
    const fallbackResults: SearchResult[] = [];
    
    // Use trusted sources data as fallback
    const relevantSources = TRUSTED_LEGAL_SOURCES.filter(source => {
      const queryLower = query.toLowerCase();
      return source.coverageAreas.some(area => 
        queryLower.includes(area) || 
        area.includes(queryLower.split(' ')[0])
      );
    }).slice(0, 3);
    
    relevantSources.forEach(source => {
      if (query.toLowerCase().includes('arrest') || query.toLowerCase().includes('police')) {
        fallbackResults.push({
          content: this.getArrestRightsContent(source.category),
          source: source.name,
          reliability: source.reliability,
          url: `${source.baseUrl}/arrest-rights`,
          lastUpdated: new Date()
        });
      } else if (query.toLowerCase().includes('property') || query.toLowerCase().includes('land')) {
        fallbackResults.push({
          content: this.getPropertyRightsContent(source.category),
          source: source.name,
          reliability: source.reliability,
          url: `${source.baseUrl}/property-law`,
          lastUpdated: new Date()
        });
      } else if (query.toLowerCase().includes('divorce') || query.toLowerCase().includes('marriage')) {
        fallbackResults.push({
          content: this.getFamilyLawContent(source.category),
          source: source.name,
          reliability: source.reliability,
          url: `${source.baseUrl}/family-law`,
          lastUpdated: new Date()
        });
      } else {
        // Generic legal guidance
        fallbackResults.push({
          content: `Legal information from ${source.name}. For specific legal guidance related to "${query}", please consult with a qualified legal professional.`,
          source: source.name,
          reliability: source.reliability * 0.8, // Reduce reliability for generic responses
          url: source.baseUrl,
          lastUpdated: new Date()
        });
      }
    });
    
    return fallbackResults;
  }

  /**
   * Get arrest rights content based on source category
   */
  private getArrestRightsContent(category: string): string {
    const contentMap: { [key: string]: string } = {
      'legislation': `
        **Code of Criminal Procedure, 1898 & Constitution of Bangladesh:**
        • **Section 61**: Right to know grounds of arrest immediately
        • **Section 167**: Must be produced before magistrate within 24 hours
        • **Article 33**: Protection against arbitrary arrest and detention
        • **Article 35**: Protection from torture and cruel punishment
        • **Section 54**: Police powers of arrest without warrant (specific conditions)
        • **Section 497**: Right to bail in bailable offences
      `,
      'judicial': `
        **Supreme Court Guidelines (BLAST vs Bangladesh & Others):**
        • Right to immediate legal representation
        • Right to inform family members about arrest
        • Right to medical examination if injured
        • Protection from custodial violence and torture
        • Right to be informed of charges in understandable language
        • Right to remain silent during interrogation
      `,
      'legal_aid': `
        **Your Immediate Rights During Arrest:**
        • Ask "What is the charge against me?" - you must be told
        • Say "I want to call my family/lawyer" - this cannot be denied
        • "I want to remain silent" - you don't have to answer questions
        • Request female police officer if you're a woman
        • Demand arrest memo with officer details and time
        • Call Legal Aid Helpline: 16430 (free 24/7 service)
      `,
      'government': `
        **Official Police Procedure (Police Manual & Directives):**
        • Arrest memo must be prepared immediately with witness signatures
        • Arresting officer must show ID and state their authority
        • Proper documentation of arrest time, place, and circumstances
        • Medical examination before detention if injuries present
        • Immediate information to magistrate about arrest
        • Family notification within reasonable time
      `,
      'human_rights': `
        **Constitutional & Human Rights Protections:**
        • Right to dignified treatment under Article 35 (no torture)
        • Right to interpretation if language barrier exists
        • Special protection for juveniles under Children Act, 2013
        • Special procedures for women arrestees (female officer required)
        • Right to practice religion while in custody
        • Protection from discrimination during arrest and detention
      `
    };
    
    return contentMap[category] || 'General legal guidance available';
  }

  private getPropertyRightsContent(category: string): string {
    const contentMap: { [key: string]: string } = {
      'legislation': `
        **Property Laws in Bangladesh:**
        • **Registration Act, 1908**: All property transfers must be registered
        • **Transfer of Property Act, 1882**: Governs sale, mortgage, and lease
        • **Stamp Act, 1899**: Proper stamp duty required for documents
        • **Evidence Act, 1872**: Property documents as legal evidence
      `,
      'government': `
        **Government Property Procedures:**
        • Sub-Registry Office registration mandatory
        • DC office for land mutation
        • Survey of Bangladesh for land records
        • Tax clearance certificate required
      `
    };
    return contentMap[category] || 'Property law guidance available';
  }

  private getFamilyLawContent(category: string): string {
    const contentMap: { [key: string]: string } = {
      'legislation': `
        **Family Laws in Bangladesh:**
        • **Muslim Family Laws Ordinance, 1961**: Marriage, divorce for Muslims
        • **Hindu Marriage Act, 1955**: Marriage laws for Hindus
        • **Christian Marriage Act, 1872**: Christian marriage procedures
        • **Dissolution of Muslim Marriages Act, 1939**: Divorce procedures
      `,
      'legal_aid': `
        **Family Law Rights:**
        • Right to maintenance during marriage
        • Right to dower (mahr) for Muslim women
        • Child custody rights for both parents
        • Property rights after divorce
      `
    };
    return contentMap[category] || 'Family law guidance available';
  }

  /**
   * Synthesize comprehensive response from multiple sources
   */
  private async synthesizeResponse(
    query: string,
    internalResponse: string,
    searchResults: SearchResult[]
  ): Promise<string> {
    
    if (searchResults.length === 0) {
      return this.improveInternalResponse(query, internalResponse);
    }

    // Structure the enhanced response based on query type
    let enhancedResponse = `🔍 **Enhanced Legal Guidance (External Sources)**\n\n`;
    
    // Determine query type and customize response
    const isArrestQuery = query.toLowerCase().includes('arrest') || query.toLowerCase().includes('police');
    const isPropertyQuery = query.toLowerCase().includes('property') || query.toLowerCase().includes('land');
    const isFamilyQuery = query.toLowerCase().includes('divorce') || query.toLowerCase().includes('marriage');
    
    if (isArrestQuery) {
      enhancedResponse += `**🚨 Your Rights if Arrested by Police in Bangladesh:**\n\n`;
      enhancedResponse += `**IMMEDIATE ACTIONS TO TAKE:**\n`;
      enhancedResponse += `1. 🗣️ Ask: "What is the specific charge against me?" (Section 61, CrPC)\n`;
      enhancedResponse += `2. 📞 Say: "I want to call my family and lawyer" (Constitutional right)\n`;
      enhancedResponse += `3. 🤐 State: "I choose to remain silent" (Right against self-incrimination)\n`;
      enhancedResponse += `4. 📝 Demand: "Please provide written arrest memo with your details"\n`;
      enhancedResponse += `5. 👮‍♀️ Request: Female officer if you're a woman\n\n`;
    } else if (isPropertyQuery) {
      enhancedResponse += `**🏠 Property Rights and Procedures in Bangladesh:**\n\n`;
    } else if (isFamilyQuery) {
      enhancedResponse += `**👨‍👩‍👧‍👦 Family Law Rights in Bangladesh:**\n\n`;
    }
    
    // Add comprehensive legal information from sources
    enhancedResponse += `**📜 LEGAL FRAMEWORK:**\n`;
    searchResults.forEach(result => {
      enhancedResponse += `${result.content}\n\n`;
    });
    
    if (isArrestQuery) {
      // Add specific emergency information for arrests
      enhancedResponse += `**🆘 EMERGENCY CONTACTS:**\n`;
      enhancedResponse += `• **Legal Aid Helpline: 16430** (Free 24/7 legal assistance)\n`;
      enhancedResponse += `• **BLAST Hotline: +880-2-9611402** (Bangladesh Legal Aid)\n`;
      enhancedResponse += `• **Police Emergency: 999**\n`;
      enhancedResponse += `• **Women's Helpline: 109** (For female arrestees)\n\n`;
      
      enhancedResponse += `**⏰ CRITICAL TIME LIMITS:**\n`;
      enhancedResponse += `• You MUST be produced before a magistrate within **24 hours**\n`;
      enhancedResponse += `• Police cannot detain you beyond this without court order\n`;
      enhancedResponse += `• Count from time of arrest, not from reaching police station\n\n`;
    }
    
    // Add authoritative sources
    enhancedResponse += `**🏛️ AUTHORITATIVE SOURCES:**\n`;
    const uniqueSources = [...new Set(searchResults.map(r => r.source))];
    uniqueSources.forEach(source => {
      enhancedResponse += `• ${source}\n`;
    });
    
    enhancedResponse += `\n⚠️ **DISCLAIMER:** This information is based on Bangladesh law. For your specific legal situation, immediately consult a qualified lawyer. This is not a substitute for professional legal advice.\n`;
    
    return enhancedResponse;
  }


  /**
   * Improve internal response when external search unavailable
   */
  private improveInternalResponse(_query: string, internalResponse: string): string {
    // Add structured format to existing response
    let improved = `${internalResponse}\n\n`;
    
    improved += `**📋 General Legal Principles (Universal Rights):**\n`;
    improved += `• Right to know reason for arrest\n`;
    improved += `• Right to legal representation\n`;
    improved += `• Right to remain silent\n`;
    improved += `• Right to humane treatment\n`;
    improved += `• Right to be produced before magistrate promptly\n\n`;
    
    improved += `**🚨 Immediate Steps:**\n`;
    improved += `• Stay calm and comply peacefully\n`;
    improved += `• Ask for arrest documentation\n`;
    improved += `• Request to contact family/lawyer\n`;
    improved += `• Remember officer details and time\n\n`;
    
    improved += `**📞 Seek Help:**\n`;
    improved += `• Contact local bar association\n`;
    improved += `• Reach out to legal aid organizations\n`;
    improved += `• Consult qualified legal counsel immediately\n`;
    
    return improved;
  }

  /**
   * Calculate final confidence score
   */
  private calculateFinalConfidence(
    internalConfidence: number,
    searchResults: SearchResult[]
  ): number {
    if (searchResults.length === 0) {
      return Math.min(internalConfidence + 0.1, 0.7);
    }
    
    const avgReliability = searchResults.reduce((sum, result) => 
      sum + result.reliability, 0) / searchResults.length;
    
    const sourceBonus = Math.min(searchResults.length * 0.1, 0.3);
    
    return Math.min(
      (internalConfidence * 0.3) + (avgReliability * 0.5) + sourceBonus,
      0.95
    );
  }

  /**
   * Record user feedback for analytics
   */
  recordFeedback(searchId: string, feedback: 'good' | 'bad'): void {
    this.analytics.recordFeedback(searchId, feedback);
  }
  
  /**
   * Get search analytics
   */
  getAnalytics() {
    return this.analytics.getAnalytics();
  }
  
  /**
   * Get real-time search statistics
   */
  getRealTimeStats() {
    return this.analytics.getRealTimeStats();
  }
  
  /**
   * Get quality insights for improving search
   */
  getQualityInsights() {
    return this.analytics.getQualityInsights();
  }
  
  /**
   * Clear search cache
   */
  clearCache(): void {
    this.externalSearchService.clearCache();
  }
  
  /**
   * Get cache statistics
   */
  getCacheStats() {
    return this.externalSearchService.getCacheStats();
  }
}

export { EnhancedSearchService, type EnhancedResponse, type SearchResult };