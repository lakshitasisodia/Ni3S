import { useEffect, useState } from 'react';
import { api, type HeatmapItem, type RiskDistrictItem } from '../services/api';

function FilterPanel({ 
  states, 
  selectedState, 
  setSelectedState,
  riskFilter,
  setRiskFilter 
}: { 
  states: string[]; 
  selectedState: string; 
  setSelectedState: (s: string) => void;
  riskFilter: string;
  setRiskFilter: (r: string) => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All States</option>
            {states.map(state => (
              <option key={state} value={state}>{state}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Risk Category</label>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Risk Levels</option>
            <option value="High Risk">High Risk Only</option>
            <option value="Medium Risk">Medium Risk Only</option>
            <option value="Low Risk">Low Risk Only</option>
          </select>
        </div>
      </div>
    </div>
  );
}

function HeatmapGrid({ items }: { items: HeatmapItem[] }) {
  const getRiskColor = (category: string) => {
    if (category === 'High Risk') return 'bg-red-500 hover:bg-red-600';
    if (category === 'Medium Risk') return 'bg-yellow-500 hover:bg-yellow-600';
    return 'bg-green-500 hover:bg-green-600';
  };
  
  // const getTextColor = (category: string) => {
  //   if (category === 'High Risk') return 'text-red-900';
  //   if (category === 'Medium Risk') return 'text-yellow-900';
  //   return 'text-green-900';
  // };
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        District Risk Heatmap ({items.length} districts)
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-96 overflow-y-auto">
        {items.map((item, index) => (
          <div
            key={`${item.state}-${item.district}-${index}`}
            className={`${getRiskColor(item.risk_category)} text-white p-3 rounded cursor-pointer transition-all transform hover:scale-105`}
            title={`${item.district}, ${item.state}\nRisk: ${(item.risk_score * 100).toFixed(1)}%\nPenetration: ${(item.penetration_rate * 100).toFixed(1)}%`}
          >
            <div className="text-xs font-medium truncate">{item.district}</div>
            <div className="text-xs opacity-90 truncate">{item.state}</div>
            <div className="text-lg font-bold mt-1">{(item.risk_score * 100).toFixed(0)}%</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function TopRiskTable({ items }: { items: RiskDistrictItem[] }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 50 High-Risk Districts</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">State</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">District</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Score</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Penetration</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.map((item, index) => (
              <tr key={`${item.state}-${item.district}`} className="hover:bg-gray-50">
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                  #{index + 1}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">{item.state}</td>
                <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{item.district}</td>
                <td className="px-4 py-3 whitespace-nowrap text-sm">
                  <span className="font-bold text-red-600">{(item.risk_score * 100).toFixed(1)}%</span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded ${
                    item.risk_category === 'High Risk' ? 'bg-red-100 text-red-800' :
                    item.risk_category === 'Medium Risk' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {item.risk_category}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700">
                  {(item.penetration_rate * 100).toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default function RiskHeatmap() {
  const [heatmapData, setHeatmapData] = useState<HeatmapItem[]>([]);
  const [topRiskData, setTopRiskData] = useState<RiskDistrictItem[]>([]);
  const [allStates, setAllStates] = useState<string[]>([]);
  const [selectedState, setSelectedState] = useState<string>('');
  const [riskFilter, setRiskFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [heatmap, topRisk, states] = await Promise.all([
          api.getRiskHeatmap(),
          api.getRiskRankings(50),
          api.getStates()
        ]);
        setHeatmapData(heatmap.heatmap_data);
        setTopRiskData(topRisk.high_risk_districts);
        setAllStates(states.states);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const filteredHeatmapData = heatmapData.filter(item => {
    if (selectedState && item.state !== selectedState) return false;
    if (riskFilter && item.risk_category !== riskFilter) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading risk heatmap...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Risk Heatmap</h1>
        <p className="text-gray-600 mt-1">Visual representation of district-level risk across India</p>
      </div>

      <FilterPanel
        states={allStates}
        selectedState={selectedState}
        setSelectedState={setSelectedState}
        riskFilter={riskFilter}
        setRiskFilter={setRiskFilter}
      />

      <div className="bg-blue-50 border-l-4 border-blue-600 p-4 rounded">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span className="text-sm text-gray-700">Low Risk (0-30%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-yellow-500 rounded"></div>
            <span className="text-sm text-gray-700">Medium Risk (30-60%)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 bg-red-500 rounded"></div>
            <span className="text-sm text-gray-700">High Risk (60-100%)</span>
          </div>
        </div>
      </div>

      <HeatmapGrid items={filteredHeatmapData} />

      <TopRiskTable items={topRiskData} />
    </div>
  );
}