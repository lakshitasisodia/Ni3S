import { useEffect, useState } from 'react';
import { api, type DistrictFull } from '../services/api';

function MetricCard({ label, value, color = 'blue' }: { label: string; value: string; color?: string }) {
  const colorClasses = {
    blue: 'border-blue-500 bg-blue-50',
    green: 'border-green-500 bg-green-50',
    red: 'border-red-500 bg-red-50',
    yellow: 'border-yellow-500 bg-yellow-50'
  };
  
  return (
    <div className={`border-l-4 ${colorClasses[color as keyof typeof colorClasses]} p-3 rounded`}>
      <div className="text-xs text-gray-600 font-medium">{label}</div>
      <div className="text-xl font-bold text-gray-900 mt-1">{value}</div>
    </div>
  );
}

function RiskGauge({ score, category }: { score: number; category: string }) {
  const percentage = score * 100;
  const getColor = () => {
    if (score < 0.3) return 'text-green-600';
    if (score < 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };
  
  const getBarColor = () => {
    if (score < 0.3) return 'bg-green-500';
    if (score < 0.6) return 'bg-yellow-500';
    return 'bg-red-500';
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">District Risk Score</h3>
      <div className="text-center mb-4">
        <div className={`text-5xl font-bold ${getColor()}`}>
          {percentage.toFixed(1)}%
        </div>
        <div className="text-sm text-gray-600 mt-1">{category}</div>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-4">
        <div
          className={`${getBarColor()} h-4 rounded-full transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex justify-between text-xs text-gray-500 mt-2">
        <span>Low Risk</span>
        <span>High Risk</span>
      </div>
    </div>
  );
}

function RiskBreakdown({ components }: { components: DistrictFull['risk']['risk_components'] }) {
  const items = [
    { label: 'Penetration Risk', value: components.penetration_risk, weight: '35%' },
    { label: 'Growth Risk', value: components.growth_risk, weight: '25%' },
    { label: 'Youth Risk', value: components.youth_risk, weight: '20%' },
    { label: 'Volatility Risk', value: components.volatility_risk, weight: '10%' },
    { label: 'Stagnation Risk', value: components.stagnation_risk, weight: '10%' }
  ];
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Components</h3>
      <div className="space-y-3">
        {items.map(item => (
          <div key={item.label}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-700">{item.label}</span>
              <span className="text-gray-600">{(item.value * 100).toFixed(1)}% (weight: {item.weight})</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${item.value * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function RecommendationsList({ recommendations }: { recommendations: DistrictFull['recommendations'] }) {
  const priorityColors = {
    critical: 'bg-red-100 border-red-500 text-red-900',
    high: 'bg-orange-100 border-orange-500 text-orange-900',
    medium: 'bg-yellow-100 border-yellow-500 text-yellow-900',
    low: 'bg-green-100 border-green-500 text-green-900'
  };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Policy Recommendations ({recommendations.total_recommendations})
      </h3>
      {recommendations.recommendations.length === 0 ? (
        <p className="text-gray-600 text-sm">No critical recommendations. District performance is satisfactory.</p>
      ) : (
        <div className="space-y-3">
          {recommendations.recommendations.map((rec, index) => (
            <div
              key={index}
              className={`border-l-4 p-4 rounded ${priorityColors[rec.priority as keyof typeof priorityColors]}`}
            >
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold">{rec.intervention}</h4>
                <span className="text-xs font-bold uppercase px-2 py-1 rounded">
                  {rec.priority}
                </span>
              </div>
              <p className="text-sm mb-2">{rec.description}</p>
              <p className="text-xs italic">Expected Impact: {rec.expected_impact}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function StateDistrictExplorer() {
  const [states, setStates] = useState<string[]>([]);
  const [selectedState, setSelectedState] = useState<string>('');
  const [districts, setDistricts] = useState<string[]>([]);
  const [selectedDistrict, setSelectedDistrict] = useState<string>('');
  const [districtData, setDistrictData] = useState<DistrictFull | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function fetchStates() {
      const data = await api.getStates();
      setStates(data.states);
    }
    fetchStates();
  }, []);

  useEffect(() => {
    if (selectedState) {
      async function fetchDistricts() {
        const data = await api.getDistricts(selectedState);
        setDistricts(data.districts);
        setSelectedDistrict('');
        setDistrictData(null);
      }
      fetchDistricts();
    }
  }, [selectedState]);

  useEffect(() => {
    if (selectedState && selectedDistrict) {
      async function fetchDistrictData() {
        setLoading(true);
        try {
          const data = await api.getDistrictFull(selectedState, selectedDistrict);
          setDistrictData(data);
        } catch (error) {
          console.error('Error fetching district data:', error);
        } finally {
          setLoading(false);
        }
      }
      fetchDistrictData();
    }
  }, [selectedState, selectedDistrict]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">State & District Explorer</h1>
        <p className="text-gray-600 mt-1">Detailed analytics and risk assessment for specific districts</p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Select State</label>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">-- Choose State --</option>
              {states.map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Select District</label>
            <select
              value={selectedDistrict}
              onChange={(e) => setSelectedDistrict(e.target.value)}
              disabled={!selectedState}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              <option value="">-- Choose District --</option>
              {districts.map(district => (
                <option key={district} value={district}>{district}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-gray-600">Loading district analytics...</p>
          </div>
        </div>
      )}

      {!loading && districtData && (
        <>
          <div className="bg-blue-900 text-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold">{districtData.analytics.district}, {districtData.analytics.state}</h2>
            <p className="text-blue-200 mt-1">District-level enrollment and risk analytics</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="Total Enrollments"
              value={districtData.analytics.total_enrollments.toLocaleString('en-IN')}
            />
            <MetricCard
              label="Penetration Rate"
              value={`${(districtData.analytics.latest_penetration_rate * 100).toFixed(1)}%`}
              color={districtData.analytics.latest_penetration_rate > 0.6 ? 'green' : 'yellow'}
            />
            <MetricCard
              label="Youth Inclusion"
              value={`${(districtData.analytics.youth_inclusion_rate * 100).toFixed(1)}%`}
              color={districtData.analytics.youth_inclusion_rate > 0.5 ? 'green' : 'red'}
            />
            <MetricCard
              label="Growth Slope"
              value={districtData.analytics.growth_slope.toFixed(2)}
              color={districtData.analytics.growth_slope > 0 ? 'green' : 'red'}
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RiskGauge
              score={districtData.risk.composite_risk_score}
              category={districtData.risk.risk_category}
            />
            <RiskBreakdown components={districtData.risk.risk_components} />
          </div>

          <RecommendationsList recommendations={districtData.recommendations} />

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Additional Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="border border-gray-200 rounded p-3">
                <div className="text-sm text-gray-600">Adult Inclusion Rate</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {(districtData.analytics.adult_inclusion_rate * 100).toFixed(1)}%
                </div>
              </div>
              <div className="border border-gray-200 rounded p-3">
                <div className="text-sm text-gray-600">Youth-Adult Gap</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {(districtData.analytics.youth_adult_gap * 100).toFixed(1)}%
                </div>
              </div>
              <div className="border border-gray-200 rounded p-3">
                <div className="text-sm text-gray-600">Stagnation Periods</div>
                <div className="text-2xl font-bold text-gray-900 mt-1">
                  {districtData.analytics.stagnation_periods}
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {!loading && !districtData && selectedState && selectedDistrict && (
        <div className="text-center py-12 text-gray-600">
          Unable to load district data. Please try again.
        </div>
      )}

      {!selectedState && (
        <div className="text-center py-12 text-gray-500">
          Please select a state and district to view analytics
        </div>
      )}
    </div>
  );
}