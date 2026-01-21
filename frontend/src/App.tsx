import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import NationalOverview from './pages/NationalOverview';
import StateDistrictExplorer from './pages/StateDistrictExplorer';
import RiskHeatmap from './pages/RiskHeatmap';
import PolicyInsights from './pages/PolicyInsights';

function Navigation() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', label: 'National Overview' },
    { path: '/explorer', label: 'State & District Explorer' },
    { path: '/heatmap', label: 'Risk Heatmap' },
    { path: '/insights', label: 'Policy Insights' }
  ];
  
  return (
    <nav className="bg-blue-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-orange-500 rounded flex items-center justify-center font-bold text-lg">
              NI³S
            </div>
            <div>
              <div className="font-bold text-lg">National Identity Inclusion Intelligence System</div>
              <div className="text-xs text-blue-200">UIDAI Decision Support Platform</div>
            </div>
          </div>
        </div>
        <div className="flex space-x-1 pb-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`px-4 py-2 rounded-t text-sm font-medium transition-colors ${
                location.pathname === item.path
                  ? 'bg-white text-blue-900'
                  : 'text-blue-100 hover:bg-blue-800'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="max-w-7xl mx-auto px-4 py-6">
          <Routes>
            <Route path="/" element={<NationalOverview />} />
            <Route path="/explorer" element={<StateDistrictExplorer />} />
            <Route path="/heatmap" element={<RiskHeatmap />} />
            <Route path="/insights" element={<PolicyInsights />} />
          </Routes>
        </main>
        <footer className="bg-gray-800 text-gray-300 mt-12 py-6">
          <div className="max-w-7xl mx-auto px-4 text-center text-sm">
            <p>NI³S - National Identity Inclusion Intelligence System</p>
            <p className="text-gray-400 mt-1">Government of India | Digital India Initiative</p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;