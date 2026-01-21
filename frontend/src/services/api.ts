// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
// API Service Class
// ============================================

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async getNationalOverview(): Promise<NationalOverview> {
    const response = await fetch(`${this.baseUrl}/api/national/overview`);
    if (!response.ok) throw new Error('Failed to fetch national overview');
    return response.json();
  }

  async getNationalTrends(): Promise<NationalTrends> {
    const response = await fetch(`${this.baseUrl}/api/national/trends`);
    if (!response.ok) throw new Error('Failed to fetch national trends');
    return response.json();
  }

  async getStates(): Promise<{ states: string[] }> {
    const response = await fetch(`${this.baseUrl}/api/states`);
    if (!response.ok) throw new Error('Failed to fetch states');
    return response.json();
  }

  async getDistricts(state: string): Promise<{ state: string; districts: string[] }> {
    const response = await fetch(
      `${this.baseUrl}/api/states/${encodeURIComponent(state)}/districts`
    );
    if (!response.ok) throw new Error(`Failed to fetch districts for ${state}`);
    return response.json();
  }

  async getStateOverview(state: string): Promise<StateOverview> {
    const response = await fetch(
      `${this.baseUrl}/api/states/${encodeURIComponent(state)}/overview`
    );
    if (!response.ok) throw new Error(`Failed to fetch state overview for ${state}`);
    return response.json();
  }

  async getDistrictFull(state: string, district: string): Promise<DistrictFull> {
    const response = await fetch(
      `${this.baseUrl}/api/districts/${encodeURIComponent(state)}/${encodeURIComponent(district)}`
    );
    if (!response.ok) throw new Error(`Failed to fetch district data for ${district}, ${state}`);
    return response.json();
  }

  async getRiskRankings(limit: number = 50): Promise<{ high_risk_districts: RiskDistrictItem[] }> {
    const response = await fetch(`${this.baseUrl}/api/risk/rankings?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch risk rankings');
    return response.json();
  }

  async getRiskHeatmap(): Promise<{ heatmap_data: HeatmapItem[] }> {
    const response = await fetch(`${this.baseUrl}/api/risk/heatmap`);
    if (!response.ok) throw new Error('Failed to fetch risk heatmap');
    return response.json();
  }

  async getRiskDistribution(): Promise<RiskDistribution> {
    const response = await fetch(`${this.baseUrl}/api/risk/distribution`);
    if (!response.ok) throw new Error('Failed to fetch risk distribution');
    return response.json();
  }

  async getPolicyInsights(): Promise<PolicyInsights> {
    const response = await fetch(`${this.baseUrl}/api/insights/policy`);
    if (!response.ok) throw new Error('Failed to fetch policy insights');
    return response.json();
  }

  async getStateInsights(state: string): Promise<StateInsights> {
    const response = await fetch(
      `${this.baseUrl}/api/insights/state/${encodeURIComponent(state)}`
    );
    if (!response.ok) throw new Error(`Failed to fetch state insights for ${state}`);
    return response.json();
  }
}

// Export a single instance
export const api = new ApiService();

// Also export the class if needed elsewhere
export default ApiService;