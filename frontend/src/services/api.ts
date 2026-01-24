// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Retry configuration
const MAX_RETRIES = 12; // 12 retries * 3 seconds = ~36 seconds max wait
const RETRY_DELAY = 3000; // 3 seconds between retries

// ============================================
// TypeScript Interfaces
// ============================================

export interface NationalOverview {
  total_enrollments: number;
  total_population: number;
  overall_penetration_rate: number;
  youth_penetration_rate: number;
  adult_penetration_rate: number;
  num_states: number;
  num_districts: number;
  coverage_gap: number;
  latest_date: string;
}

export interface TrendData {
  date: string;
  enrollments: number;
  population: number;
  penetration_rate: number;
}

export interface NationalTrends {
  trends: TrendData[];
}

export interface StateOverview {
  state: string;
  total_enrollments: number;
  total_population: number;
  avg_penetration_rate: number;
  num_districts: number;
}

export interface DistrictAnalytics {
  state: string;
  district: string;
  total_enrollments: number;
  total_population: number;
  avg_penetration_rate: number;
  latest_penetration_rate: number;
  youth_inclusion_rate: number;
  adult_inclusion_rate: number;
  youth_adult_gap: number;
  growth_slope: number;
  growth_volatility: number;
  stagnation_periods: number;
  trends: TrendData[];
}

export interface RiskComponents {
  penetration_risk: number;
  growth_risk: number;
  youth_risk: number;
  volatility_risk: number;
  stagnation_risk: number;
}

export interface RiskScore {
  state: string;
  district: string;
  composite_risk_score: number;
  risk_category: string;
  risk_components: RiskComponents;
}

export interface Recommendation {
  intervention: string;
  priority: string;
  description: string;
  expected_impact: string;
}

export interface Recommendations {
  recommendations: Recommendation[];
  total_recommendations: number;
  priority_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
}

export interface DistrictFull {
  analytics: DistrictAnalytics;
  risk: RiskScore;
  recommendations: Recommendations;
}

export interface RiskDistrictItem {
  state: string;
  district: string;
  risk_score: number;
  risk_category: string;
  penetration_rate: number;
  youth_inclusion_rate: number;
}

export interface HeatmapItem {
  state: string;
  district: string;
  risk_score: number;
  risk_category: string;
  penetration_rate: number;
  total_population: number;
}

export interface RiskDistribution {
  overall_distribution: {
    'Low Risk'?: number;
    'Medium Risk'?: number;
    'High Risk'?: number;
  };
  state_risk_summary: {
    state: string;
    avg_risk_score: number;
    max_risk_score: number;
    num_districts: number;
  }[];
  total_districts: number;
  avg_national_risk: number;
}

export interface PolicyInsight {
  category: string;
  severity: string;
  insight: string;
  recommendation: string;
}

export interface PolicyInsights {
  insights: PolicyInsight[];
  total_insights: number;
  critical_issues: number;
  generated_at: string;
}

export interface StateInsights {
  state: string;
  insights: PolicyInsight[];
  total_insights: number;
  generated_at: string;
}

// ============================================
// Helper Functions
// ============================================

const wait = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

async function fetchWithRetry<T>(
  url: string,
  options: RequestInit = {},
  retries: number = MAX_RETRIES
): Promise<T> {
  try {
    const response = await fetch(url, options);
    
    // If 503 (Service Unavailable - backend still initializing), retry
    if (response.status === 503) {
      if (retries > 0) {
        console.log(`Backend is initializing... Retrying in ${RETRY_DELAY/1000}s (${retries} attempts left)`);
        await wait(RETRY_DELAY);
        return fetchWithRetry<T>(url, options, retries - 1);
      } else {
        throw new Error('Backend initialization timeout. The backend is taking longer than expected to load data. Please refresh the page in a moment.');
      }
    }
    
    // If other HTTP error, throw immediately
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'Unknown error');
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }
    
    return response.json();
  } catch (error) {
    // Network errors - retry a few times
    if (retries > 0 && error instanceof TypeError && error.message.includes('fetch')) {
      console.log(`Network error, retrying... (${retries} attempts left)`);
      await wait(RETRY_DELAY);
      return fetchWithRetry<T>(url, options, retries - 1);
    }
    throw error;
  }
}

// ============================================
// API Service Class
// ============================================

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async getNationalOverview(): Promise<NationalOverview> {
    return fetchWithRetry<NationalOverview>(`${this.baseUrl}/api/national/overview`);
  }

  async getNationalTrends(): Promise<NationalTrends> {
    return fetchWithRetry<NationalTrends>(`${this.baseUrl}/api/national/trends`);
  }

  async getStates(): Promise<{ states: string[] }> {
    return fetchWithRetry<{ states: string[] }>(`${this.baseUrl}/api/states`);
  }

  async getDistricts(state: string): Promise<{ state: string; districts: string[] }> {
    return fetchWithRetry<{ state: string; districts: string[] }>(
      `${this.baseUrl}/api/states/${encodeURIComponent(state)}/districts`
    );
  }

  async getStateOverview(state: string): Promise<StateOverview> {
    return fetchWithRetry<StateOverview>(
      `${this.baseUrl}/api/states/${encodeURIComponent(state)}/overview`
    );
  }

  async getDistrictFull(state: string, district: string): Promise<DistrictFull> {
    return fetchWithRetry<DistrictFull>(
      `${this.baseUrl}/api/districts/${encodeURIComponent(state)}/${encodeURIComponent(district)}`
    );
  }

  async getRiskRankings(limit: number = 50): Promise<{ high_risk_districts: RiskDistrictItem[] }> {
    return fetchWithRetry<{ high_risk_districts: RiskDistrictItem[] }>(
      `${this.baseUrl}/api/risk/rankings?limit=${limit}`
    );
  }

  async getRiskHeatmap(): Promise<{ heatmap_data: HeatmapItem[] }> {
    return fetchWithRetry<{ heatmap_data: HeatmapItem[] }>(
      `${this.baseUrl}/api/risk/heatmap`
    );
  }

  async getRiskDistribution(): Promise<RiskDistribution> {
    return fetchWithRetry<RiskDistribution>(`${this.baseUrl}/api/risk/distribution`);
  }

  async getPolicyInsights(): Promise<PolicyInsights> {
    return fetchWithRetry<PolicyInsights>(`${this.baseUrl}/api/insights/policy`);
  }

  async getStateInsights(state: string): Promise<StateInsights> {
    return fetchWithRetry<StateInsights>(
      `${this.baseUrl}/api/insights/state/${encodeURIComponent(state)}`
    );
  }

  // Health check endpoint (useful for checking if backend is ready)
  async healthCheck(): Promise<{ status: string; server: string; data_loaded: boolean }> {
    return fetchWithRetry<{ status: string; server: string; data_loaded: boolean }>(
      `${this.baseUrl}/health`,
      {},
      3 // Only retry health check 3 times
    );
  }
}

// Export a single instance
export const api = new ApiService();

// Also export the class if needed elsewhere
export default ApiService;