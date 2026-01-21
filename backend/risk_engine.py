import pandas as pd
import numpy as np
from typing import Dict, List, Any
from analytics_engine import AnalyticsEngine

class RiskEngine:
    def __init__(self, analytics_engine: AnalyticsEngine):
        self.analytics = analytics_engine
        self.district_features = analytics_engine.get_district_features_df()
        self.risk_scores = self._compute_district_risk_scores()
        
    def _compute_district_risk_scores(self) -> pd.DataFrame:
        print("Computing District Risk Scores (DRS)...")
        
        df = self.district_features.copy()
        
        penetration_max = df['latest_penetration_rate'].max()
        df['penetration_risk'] = np.where(
            penetration_max > 0,
            1 - (df['latest_penetration_rate'] / penetration_max),
            0.5
        )
        
        growth_max = df['growth_slope'].max()
        growth_min = df['growth_slope'].min()
        growth_range = growth_max - growth_min
        
        if growth_range > 0:
            df['growth_risk'] = (growth_max - df['growth_slope']) / growth_range
        else:
            df['growth_risk'] = 0.5
        
        youth_max = df['youth_inclusion_rate'].max()
        df['youth_risk'] = np.where(
            youth_max > 0,
            1 - (df['youth_inclusion_rate'] / youth_max),
            0.5
        )
        
        volatility_max = df['growth_volatility'].max()
        df['volatility_risk'] = np.where(
            volatility_max > 0,
            df['growth_volatility'] / volatility_max,
            0
        )
        
        stagnation_max = df['stagnation_periods'].max()
        df['stagnation_risk'] = np.where(
            stagnation_max > 0,
            df['stagnation_periods'] / stagnation_max,
            0
        )
        
        df['composite_risk_score'] = (
            0.35 * df['penetration_risk'] +
            0.25 * df['growth_risk'] +
            0.20 * df['youth_risk'] +
            0.10 * df['volatility_risk'] +
            0.10 * df['stagnation_risk']
        )
        
        df['composite_risk_score'] = df['composite_risk_score'].clip(0, 1)
        
        df['risk_category'] = pd.cut(
            df['composite_risk_score'],
            bins=[0, 0.3, 0.6, 1.0],
            labels=['Low Risk', 'Medium Risk', 'High Risk'],
            include_lowest=True
        )
        
        print(f"  Risk scores computed for {len(df)} districts")
        return df
    
    def get_district_risk_score(self, state_name: str, district_name: str) -> Dict[str, Any]:
        risk_data = self.risk_scores[
            (self.risk_scores['state'] == state_name) & 
            (self.risk_scores['district'] == district_name)
        ]
        
        if risk_data.empty:
            return {'error': 'District not found'}
        
        row = risk_data.iloc[0]
        
        return {
            'state': state_name,
            'district': district_name,
            'composite_risk_score': round(row['composite_risk_score'], 4),
            'risk_category': str(row['risk_category']),
            'risk_components': {
                'penetration_risk': round(row['penetration_risk'], 4),
                'growth_risk': round(row['growth_risk'], 4),
                'youth_risk': round(row['youth_risk'], 4),
                'volatility_risk': round(row['volatility_risk'], 4),
                'stagnation_risk': round(row['stagnation_risk'], 4)
            }
        }
    
    def get_top_risk_districts(self, limit: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        top_risk = self.risk_scores.nlargest(limit, 'composite_risk_score')
        
        districts_list = []
        for _, row in top_risk.iterrows():
            districts_list.append({
                'state': row['state'],
                'district': row['district'],
                'risk_score': round(row['composite_risk_score'], 4),
                'risk_category': str(row['risk_category']),
                'penetration_rate': round(row['latest_penetration_rate'], 4),
                'youth_inclusion_rate': round(row['youth_inclusion_rate'], 4)
            })
        
        return {'high_risk_districts': districts_list}
    
    def get_heatmap_data(self) -> Dict[str, List[Dict[str, Any]]]:
        heatmap_list = []
        
        for _, row in self.risk_scores.iterrows():
            heatmap_list.append({
                'state': row['state'],
                'district': row['district'],
                'risk_score': round(row['composite_risk_score'], 4),
                'risk_category': str(row['risk_category']),
                'penetration_rate': round(row['latest_penetration_rate'], 4),
                'total_population': int(row['total_population'])
            })
        
        return {'heatmap_data': heatmap_list}
    
    def get_risk_distribution(self) -> Dict[str, Any]:
        distribution = self.risk_scores['risk_category'].value_counts().to_dict()
        
        distribution_cleaned = {str(k): int(v) for k, v in distribution.items()}
        
        risk_by_state = self.risk_scores.groupby('state')['composite_risk_score'].agg(['mean', 'max', 'count']).reset_index()
        risk_by_state.columns = ['state', 'avg_risk_score', 'max_risk_score', 'num_districts']
        
        state_risk_list = []
        for _, row in risk_by_state.iterrows():
            state_risk_list.append({
                'state': row['state'],
                'avg_risk_score': round(row['avg_risk_score'], 4),
                'max_risk_score': round(row['max_risk_score'], 4),
                'num_districts': int(row['num_districts'])
            })
        
        return {
            'overall_distribution': distribution_cleaned,
            'state_risk_summary': state_risk_list,
            'total_districts': len(self.risk_scores),
            'avg_national_risk': round(self.risk_scores['composite_risk_score'].mean(), 4)
        }
    
    def get_high_risk_states(self, threshold: float = 0.6) -> List[str]:
        high_risk_districts = self.risk_scores[self.risk_scores['composite_risk_score'] >= threshold]
        state_counts = high_risk_districts['state'].value_counts()
        return state_counts.index.tolist()