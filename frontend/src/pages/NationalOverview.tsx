import { useEffect, useState } from 'react';
import { api, type NationalOverview as NationalOverviewType,type NationalTrends, type RiskDistribution } from '../services/api';

function StatCard({ title, value, subtitle, trend }: { title: string; value: string; subtitle?: string; trend?: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-600">
      <div className="text-sm font-medium text-gray-600 mb-1">{title}</div>
      <div className="text-3xl font-bold text-gray-900 mb-1">{value}</div>
      {subtitle && <div className="text-sm text-gray-500">{subtitle}</div>}
      {trend && <div className="text-xs text-green-600 mt-1">{trend}</div>}
    </div>
  );
}

function RiskDistributionChart({ distribution }: { distribution: RiskDistribution['overall_distribution'] }) {
  const total = Object.values(distribution).reduce((sum, val) => sum + (val || 0), 0);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h3>
      <div className="space-y-3">
        {Object.entries(distribution).map(([category, count]) => {
          const percentage = total > 0 ? ((count || 0) / total * 100).toFixed(1) : '0.0';
          const colorClass = 
            category === 'High Risk' ? 'bg-red-500' :
            category === 'Medium Risk' ? 'bg-yellow-500' :
            'bg-green-500';
          
          return (
            <div key={category}>
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium text-gray-700">{category}</span>
                <span className="text-gray-600">{count} ({percentage}%)</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`${colorClass} h-3 rounded-full transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function HighRiskStates({ stateRiskSummary }: { stateRiskSummary: RiskDistribution['state_risk_summary'] }) {
  const topRiskStates = [...stateRiskSummary]
    .sort((a, b) => b.avg_risk_score - a.avg_risk_score)
    .slice(0, 10);
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 High-Risk States</h3>
      <div className="space-y-2">
        {topRiskStates.map((state, index) => (
          <div key={state.state} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-blue-100 text-blue-700 rounded-full flex items-center justify-center text-xs font-bold">
                {index + 1}
              </div>
              <div>
                <div className="font-medium text-gray-900">{state.state}</div>
                <div className="text-xs text-gray-500">{state.num_districts} districts</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-semibold text-red-600">
                {(state.avg_risk_score * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500">avg risk</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TrendsChart({ trends }: { trends: NationalTrends['trends'] }) {
  const recentTrends = trends.slice(-12);
  const maxPenetration = Math.max(...recentTrends.map(t => t.penetration_rate));
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Penetration Rate Trend</h3>
      <div className="space-y-2">
        {recentTrends.map((trend) => {
          const barWidth = maxPenetration > 0 ? (trend.penetration_rate / maxPenetration * 100) : 0;
          
          return (
            <div key={trend.date} className="flex items-center space-x-2">
              <div className="w-24 text-xs text-gray-600 text-right">
                {new Date(trend.date).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })}
              </div>
              <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                <div
                  className="bg-blue-600 h-6 rounded-full transition-all duration-300"
                  style={{ width: `${barWidth}%` }}
                />
                <div className="absolute inset-0 flex items-center justify-end pr-2 text-xs font-medium text-white">
                  {(trend.penetration_rate * 100).toFixed(1)}%
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default function NationalOverview() {
  const [overview, setOverview] = useState<NationalOverviewType | null>(null);
  const [trends, setTrends] = useState<NationalTrends | null>(null);
  const [riskDist, setRiskDist] = useState<RiskDistribution | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [overviewData, trendsData, riskData] = await Promise.all([
          api.getNationalOverview(),
          api.getNationalTrends(),
          api.getRiskDistribution()
        ]);
        setOverview(overviewData);
        setTrends(trendsData);
        setRiskDist(riskData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading national analytics...</p>
        </div>
      </div>
    );
  }

  if (!overview || !trends || !riskDist) {
    return <div className="text-center py-12 text-red-600">Failed to load data</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">National Overview</h1>
        <p className="text-gray-600 mt-1">Comprehensive Aadhaar enrollment analytics across India</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Enrollments"
          value={overview.total_enrollments.toLocaleString('en-IN')}
          subtitle={`of ${overview.total_population.toLocaleString('en-IN')} population`}
        />
        <StatCard
          title="Penetration Rate"
          value={`${(overview.overall_penetration_rate * 100).toFixed(1)}%`}
          subtitle={`Coverage gap: ${(overview.coverage_gap * 100).toFixed(1)}%`}
        />
        <StatCard
          title="States Covered"
          value={overview.num_states.toString()}
          subtitle={`${overview.num_districts} districts`}
        />
        <StatCard
          title="Youth Coverage"
          value={`${(overview.youth_penetration_rate * 100).toFixed(1)}%`}
          subtitle={`Adult: ${(overview.adult_penetration_rate * 100).toFixed(1)}%`}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RiskDistributionChart distribution={riskDist.overall_distribution} />
        <HighRiskStates stateRiskSummary={riskDist.state_risk_summary} />
      </div>

      <TrendsChart trends={trends.trends} />

      <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
        <div className="flex items-start">
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-900">National Risk Assessment</h3>
            <p className="mt-1 text-sm text-blue-700">
              Average national risk score: <span className="font-bold">{(riskDist.avg_national_risk * 100).toFixed(1)}%</span>
              {' '}| Total districts analyzed: <span className="font-bold">{riskDist.total_districts}</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}