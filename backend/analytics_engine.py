import pandas as pd
import numpy as np
from typing import Dict, List, Any
from scipy.stats import linregress

class AnalyticsEngine:
    def __init__(self, master_data: pd.DataFrame):
        self.master_data = master_data
        self.district_features = self._compute_district_features()
        
    def _compute_district_features(self) -> pd.DataFrame:
        print("Computing district-level intelligence features...")
        
        features_list = []
        
        grouped = self.master_data.groupby(['state', 'district'])
        
        for (state, district), group in grouped:
            group_sorted = group.sort_values('date')
            
            # FIXED: Use the latest date's values instead of sum/max across dates
            latest_record = group_sorted.iloc[-1]
            
            total_enrollments = latest_record['total_enrollments']
            total_population = latest_record['total_population']
            
            # Use latest penetration rate
            latest_penetration = latest_record['penetration_rate']
            avg_penetration = group['penetration_rate'].mean()
            
            # Youth metrics from latest record
            youth_enrollment = latest_record['age_5_17']
            youth_population = latest_record['demo_age_5_17']
            youth_inclusion_rate = youth_enrollment / youth_population if youth_population > 0 else 0
            youth_inclusion_rate = min(youth_inclusion_rate, 1.0)  # Cap at 100%
            
            # Adult metrics from latest record
            adult_enrollment = latest_record['age_18_greater']
            adult_population = latest_record['demo_age_17_']
            adult_inclusion_rate = adult_enrollment / adult_population if adult_population > 0 else 0
            adult_inclusion_rate = min(adult_inclusion_rate, 1.0)  # Cap at 100%
            
            # Time series for growth analysis
            enrollment_series = group_sorted[['date', 'total_enrollments']].copy()
            
            growth_slope = 0
            growth_volatility = 0
            
            if len(enrollment_series) >= 2:
                x = np.arange(len(enrollment_series))
                y = enrollment_series['total_enrollments'].values
                
                if np.std(y) > 0:
                    slope, intercept, r_value, p_value, std_err = linregress(x, y)
                    growth_slope = slope
                
                if len(y) > 1:
                    # Calculate growth rates avoiding division by zero
                    growth_rates = []
                    for i in range(1, len(y)):
                        if y[i-1] > 0:
                            growth_rates.append((y[i] - y[i-1]) / y[i-1])
                    
                    if growth_rates:
                        growth_volatility = np.std(growth_rates)
            
            time_span_days = (group_sorted['date'].max() - group_sorted['date'].min()).days
            stagnation_periods = self._detect_stagnation(group_sorted)
            
            features_list.append({
                'state': state,
                'district': district,
                'total_enrollments': int(total_enrollments),
                'total_population': int(total_population),
                'avg_penetration_rate': avg_penetration,
                'latest_penetration_rate': latest_penetration,
                'youth_inclusion_rate': youth_inclusion_rate,
                'adult_inclusion_rate': adult_inclusion_rate,
                'youth_adult_gap': abs(youth_inclusion_rate - adult_inclusion_rate),
                'growth_slope': growth_slope,
                'growth_volatility': growth_volatility,
                'stagnation_periods': stagnation_periods,
                'time_span_days': time_span_days,
                'data_points': len(group)
            })
        
        features_df = pd.DataFrame(features_list)
        print(f"  District features computed for {len(features_df)} districts")
        
        # Data quality checks
        print(f"\n  Quality metrics:")
        print(f"  - Districts with >100% penetration: {(features_df['latest_penetration_rate'] > 1.0).sum()}")
        print(f"  - Avg penetration rate: {features_df['latest_penetration_rate'].mean():.2%}")
        print(f"  - Avg youth inclusion: {features_df['youth_inclusion_rate'].mean():.2%}")
        print(f"  - Avg adult inclusion: {features_df['adult_inclusion_rate'].mean():.2%}")
        
        return features_df
    
    def _detect_stagnation(self, group_sorted: pd.DataFrame) -> int:
        """Detect periods where enrollment growth has stagnated"""
        
        if len(group_sorted) < 3:
            return 0
        
        enrollment_series = group_sorted['total_enrollments'].values
        
        stagnation_count = 0
        threshold_pct = 0.01  # Less than 1% growth is considered stagnation
        
        for i in range(1, len(enrollment_series)):
            if enrollment_series[i-1] > 0:
                growth_rate = (enrollment_series[i] - enrollment_series[i-1]) / enrollment_series[i-1]
                if abs(growth_rate) < threshold_pct:
                    stagnation_count += 1
        
        return stagnation_count
    
    def get_national_overview(self) -> Dict[str, Any]:
        """
        FIXED: Use latest snapshot instead of summing across all dates
        """
        
        # Get the latest date in the dataset
        latest_date = self.master_data['date'].max()
        latest_data = self.master_data[self.master_data['date'] == latest_date]
        
        # Sum across all districts for the latest date
        total_enrollments = int(latest_data['total_enrollments'].sum())
        total_population = int(latest_data['total_population'].sum())
        
        overall_penetration = total_enrollments / total_population if total_population > 0 else 0
        overall_penetration = min(overall_penetration, 1.0)  # Cap at 100%
        
        # Youth metrics
        total_youth_enrolled = int(latest_data['age_5_17'].sum())
        total_youth_population = int(latest_data['demo_age_5_17'].sum())
        youth_penetration = total_youth_enrolled / total_youth_population if total_youth_population > 0 else 0
        youth_penetration = min(youth_penetration, 1.0)
        
        # Adult metrics
        total_adult_enrolled = int(latest_data['age_18_greater'].sum())
        total_adult_population = int(latest_data['demo_age_17_'].sum())
        adult_penetration = total_adult_enrolled / total_adult_population if total_adult_population > 0 else 0
        adult_penetration = min(adult_penetration, 1.0)
        
        num_states = self.master_data['state'].nunique()
        num_districts = self.master_data[['state', 'district']].drop_duplicates().shape[0]
        
        return {
            'total_enrollments': total_enrollments,
            'total_population': total_population,
            'overall_penetration_rate': round(overall_penetration, 4),
            'youth_penetration_rate': round(youth_penetration, 4),
            'adult_penetration_rate': round(adult_penetration, 4),
            'num_states': num_states,
            'num_districts': num_districts,
            'coverage_gap': round(1 - overall_penetration, 4),
            'latest_date': latest_date.strftime('%Y-%m-%d')
        }
    
   
    def get_national_trends(self) -> Dict[str, Any]:
        time_series = self.master_data.groupby('date').agg({
            'total_enrollments': 'sum',
            'total_population': 'sum'
        }).reset_index()
        
        time_series = time_series.sort_values('date')
        
        # Calculate penetration rate from aggregated data (not mean of district rates)
        time_series['penetration_rate'] = np.where(
            time_series['total_population'] > 0,
            time_series['total_enrollments'] / time_series['total_population'],
            0
        )
        
        # Cap penetration rate at 100%
        time_series['penetration_rate'] = time_series['penetration_rate'].clip(upper=1.0)
        
        trends = []
        for _, row in time_series.iterrows():
            trends.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'enrollments': int(row['total_enrollments']),
                'population': int(row['total_population']),
                'penetration_rate': round(row['penetration_rate'], 4)
            })
        
        return {'trends': trends}

    def get_states_list(self) -> Dict[str, List[str]]:
        states = sorted(self.master_data['state'].unique().tolist())
        return {'states': states}
    
    def get_districts_by_state(self, state_name: str) -> Dict[str, List[str]]:
        districts = self.master_data[self.master_data['state'] == state_name]['district'].unique().tolist()
        districts = sorted(districts)
        return {'state': state_name, 'districts': districts}
    
    def get_state_overview(self, state_name: str) -> Dict[str, Any]:
        state_data = self.master_data[self.master_data['state'] == state_name]
        
        if state_data.empty:
            return {'error': 'State not found'}
        
        # Use latest date
        latest_date = state_data['date'].max()
        latest_data = state_data[state_data['date'] == latest_date]
        
        total_enrollments = int(latest_data['total_enrollments'].sum())
        total_population = int(latest_data['total_population'].sum())
        
        avg_penetration = total_enrollments / total_population if total_population > 0 else 0
        avg_penetration = min(avg_penetration, 1.0)
        
        num_districts = state_data['district'].nunique()
        
        return {
            'state': state_name,
            'total_enrollments': total_enrollments,
            'total_population': total_population,
            'avg_penetration_rate': round(avg_penetration, 4),
            'num_districts': num_districts
        }
    
    def get_district_analytics(self, state_name: str, district_name: str) -> Dict[str, Any]:
        district_data = self.master_data[
            (self.master_data['state'] == state_name) & 
            (self.master_data['district'] == district_name)
        ]
        
        if district_data.empty:
            return {'error': 'District not found'}
        
        features = self.district_features[
            (self.district_features['state'] == state_name) & 
            (self.district_features['district'] == district_name)
        ]
        
        if features.empty:
            return {'error': 'District features not found'}
        
        feature_row = features.iloc[0]
        
        time_series = district_data.sort_values('date')[['date', 'total_enrollments', 'penetration_rate']].copy()
        time_series['penetration_rate'] = time_series['penetration_rate'].clip(upper=1.0)
        
        trends = []
        for _, row in time_series.iterrows():
            trends.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'enrollments': int(row['total_enrollments']),
                'penetration_rate': round(row['penetration_rate'], 4)
            })
        
        return {
            'state': state_name,
            'district': district_name,
            'total_enrollments': int(feature_row['total_enrollments']),
            'total_population': int(feature_row['total_population']),
            'avg_penetration_rate': round(feature_row['avg_penetration_rate'], 4),
            'latest_penetration_rate': round(feature_row['latest_penetration_rate'], 4),
            'youth_inclusion_rate': round(feature_row['youth_inclusion_rate'], 4),
            'adult_inclusion_rate': round(feature_row['adult_inclusion_rate'], 4),
            'youth_adult_gap': round(feature_row['youth_adult_gap'], 4),
            'growth_slope': round(feature_row['growth_slope'], 2),
            'growth_volatility': round(feature_row['growth_volatility'], 4),
            'stagnation_periods': int(feature_row['stagnation_periods']),
            'trends': trends
        }
    
    def get_district_features_df(self) -> pd.DataFrame:
        return self.district_features
    

    

