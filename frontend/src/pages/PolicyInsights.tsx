import { useEffect, useState } from 'react';
import { api, type PolicyInsights as PolicyInsightsType, type StateInsights, type PolicyInsight } from '../services/api';

function InsightCard({ insight }: { insight: PolicyInsight }) {
  const severityColors = {
    critical: 'bg-red-50 border-red-500',
    high: 'bg-orange-50 border-orange-500',
    medium: 'bg-yellow-50 border-yellow-500',
    low: 'bg-blue-50 border-blue-500'
  };
  
  const severityBadgeColors = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-blue-100 text-blue-800'
  };
  
  const severityIcons = {
    critical: '🔴',
    high: '🟠',
    medium: '🟡',
    low: '🔵'
  };
  
  return (
    <div className={`border-l-4 ${severityColors[insight.severity as keyof typeof severityColors]} p-6 rounded-lg`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{severityIcons[insight.severity as keyof typeof severityIcons]}</span>
          <h3 className="text-lg font-semibold text-gray-900">{insight.category}</h3>
        </div>
        <span className={`px-3 py-1 text-xs font-bold uppercase rounded ${severityBadgeColors[insight.severity as keyof typeof severityBadgeColors]}`}>
          {insight.severity}
        </span>
      </div>
      
      <div className="space-y-3">
        <div>
          <div className="text-sm font-medium text-gray-700 mb-1">Analysis</div>
          <p className="text-gray-800">{insight.insight}</p>
        </div>
        
        <div>
          <div className="text-sm font-medium text-gray-700 mb-1">Recommendation</div>
          <p className="text-gray-800 bg-white p-3 rounded border border-gray-200">
            {insight.recommendation}
          </p>
        </div>
      </div>
    </div>
  );
}

function StateSelector({ 
  states, 
  selectedState, 
  onStateChange 
}: { 
  states: string[]; 
  selectedState: string; 
  onStateChange: (state: string) => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">State-Specific Insights</h3>
      <select
        value={selectedState}
        onChange={(e) => onStateChange(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">-- Select State for Detailed Insights --</option>
        {states.map(state => (
          <option key={state} value={state}>{state}</option>
        ))}
      </select>
    </div>
  );
}

function SummaryStats({ 
  totalInsights, 
  criticalIssues 
}: { 
  totalInsights: number; 
  criticalIssues: number;
}) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-600">
        <div className="text-sm font-medium text-gray-600">Total Insights</div>
        <div className="text-3xl font-bold text-gray-900 mt-2">{totalInsights}</div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-600">
        <div className="text-sm font-medium text-gray-600">Critical Issues</div>
        <div className="text-3xl font-bold text-red-600 mt-2">{criticalIssues}</div>
      </div>
      
      <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-600">
        <div className="text-sm font-medium text-gray-600">Action Items</div>
        <div className="text-3xl font-bold text-green-600 mt-2">{totalInsights}</div>
      </div>
    </div>
  );
}

export default function PolicyInsights() {
  const [policyInsights, setPolicyInsights] = useState<PolicyInsightsType | null>(null);
  const [stateInsights, setStateInsights] = useState<StateInsights | null>(null);
  const [states, setStates] = useState<string[]>([]);
  const [selectedState, setSelectedState] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [loadingState, setLoadingState] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        const [insights, statesList] = await Promise.all([
          api.getPolicyInsights(),
          api.getStates()
        ]);
        setPolicyInsights(insights);
        setStates(statesList.states);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  useEffect(() => {
    if (selectedState) {
      async function fetchStateInsights() {
        setLoadingState(true);
        try {
          const insights = await api.getStateInsights(selectedState);
          setStateInsights(insights);
        } catch (error) {
          console.error('Error fetching state insights:', error);
        } finally {
          setLoadingState(false);
        }
      }
      fetchStateInsights();
    } else {
      setStateInsights(null);
    }
  }, [selectedState]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading policy insights...</p>
        </div>
      </div>
    );
  }

  if (!policyInsights) {
    return <div className="text-center py-12 text-red-600">Failed to load insights</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Policy Insights</h1>
        <p className="text-gray-600 mt-1">Auto-generated policy recommendations based on national and state-level analytics</p>
      </div>

      <SummaryStats
        totalInsights={policyInsights.total_insights}
        criticalIssues={policyInsights.critical_issues}
      />

      <div className="bg-linear-to-r from-blue-900 to-blue-700 text-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">National Policy Insights</h2>
            <p className="text-blue-100 mt-1">
              Generated on: {new Date(policyInsights.generated_at).toLocaleString('en-IN')}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-200">Analysis Coverage</div>
            <div className="text-3xl font-bold">National</div>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {policyInsights.insights.length === 0 ? (
          <div className="bg-green-50 border-l-4 border-green-500 p-6 rounded-lg">
            <p className="text-green-800 font-medium">
              No critical national issues identified. Overall enrollment performance is satisfactory.
            </p>
          </div>
        ) : (
          policyInsights.insights.map((insight, index) => (
            <InsightCard key={index} insight={insight} />
          ))
        )}
      </div>

      <StateSelector
        states={states}
        selectedState={selectedState}
        onStateChange={setSelectedState}
      />

      {loadingState && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-gray-600">Loading state insights...</p>
          </div>
        </div>
      )}

      {!loadingState && stateInsights && (
        <>
          <div className="bg-linear-to-r from-orange-600 to-orange-500 text-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">{stateInsights.state} - State Insights</h2>
                <p className="text-orange-100 mt-1">
                  Generated on: {new Date(stateInsights.generated_at).toLocaleString('en-IN')}
                </p>
              </div>
              <div className="text-right">
                <div className="text-sm text-orange-200">Total Insights</div>
                <div className="text-3xl font-bold">{stateInsights.total_insights}</div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {stateInsights.insights.map((insight, index) => (
              <InsightCard key={index} insight={insight} />
            ))}
          </div>
        </>
      )}

      <div className="bg-gray-100 border border-gray-300 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">About Policy Insights</h3>
        <p className="text-gray-700 text-sm leading-relaxed">
          This system automatically analyzes enrollment data, risk scores, and demographic patterns to generate 
          evidence-based policy recommendations. Insights are categorized by severity and include specific 
          recommendations for intervention. The recommendation engine uses rule-based logic to identify patterns 
          such as low penetration rates, stagnation in growth, youth-adult enrollment gaps, and volatility in 
          enrollment trends. All recommendations are designed to be actionable and measurable, with clear expected 
          impacts for policy implementation.
        </p>
      </div>
    </div>
  );
}