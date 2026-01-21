import pandas as pd
import numpy as np
from typing import Dict, List, Any

class RecommendationEngine:
    def __init__(self):
        self.recommendation_rules = self._initialize_recommendation_rules()
    
    def _initialize_recommendation_rules(self) -> Dict[str, Dict[str, Any]]:
        return {
            'low_youth_enrollment': {
                'condition': lambda data: data.get('youth_inclusion_rate', 1) < 0.5,
                'priority': 'high',
                'intervention': 'School-Based Enrollment Drives',
                'description': 'Youth inclusion rate is below 50%. Deploy mobile enrollment units to schools and educational institutions.',
                'expected_impact': 'Increase youth enrollment by 15-25% within 6 months'
            },
            'stagnation_detected': {
                'condition': lambda data: data.get('stagnation_periods', 0) > 3,
                'priority': 'high',
                'intervention': 'Community Outreach Campaign',
                'description': 'Enrollment growth has stagnated over multiple periods. Launch targeted awareness campaigns.',
                'expected_impact': 'Revitalize enrollment growth momentum'
            },
            'low_penetration': {
                'condition': lambda data: data.get('latest_penetration_rate', 1) < 0.4,
                'priority': 'critical',
                'intervention': 'Intensive Enrollment Push',
                'description': 'Overall penetration is below 40%. Immediate large-scale intervention required.',
                'expected_impact': 'Achieve 60% penetration within 12 months'
            },
            'high_volatility': {
                'condition': lambda data: data.get('growth_volatility', 0) > 0.3,
                'priority': 'medium',
                'intervention': 'Infrastructure Review',
                'description': 'High enrollment volatility detected. Review and stabilize enrollment infrastructure.',
                'expected_impact': 'Stabilize enrollment patterns and improve predictability'
            },
            'low_adult_enrollment': {
                'condition': lambda data: data.get('adult_inclusion_rate', 1) < 0.6,
                'priority': 'medium',
                'intervention': 'Mobile Enrollment Camps',
                'description': 'Adult inclusion rate is low. Deploy mobile camps to workplaces and community centers.',
                'expected_impact': 'Increase adult enrollment by 10-20% within 6 months'
            },
            'youth_adult_gap': {
                'condition': lambda data: data.get('youth_adult_gap', 0) > 0.25,
                'priority': 'medium',
                'intervention': 'Targeted Age-Group Campaigns',
                'description': 'Significant gap between youth and adult enrollment rates. Design age-specific interventions.',
                'expected_impact': 'Reduce enrollment disparity between age groups'
            },
            'negative_growth': {
                'condition': lambda data: data.get('growth_slope', 0) < 0,
                'priority': 'critical',
                'intervention': 'Emergency Enrollment Recovery',
                'description': 'Enrollment is declining. Immediate investigation and corrective action required.',
                'expected_impact': 'Reverse negative growth trend within 3 months'
            }
        }
    
    def generate_recommendations(self, district_data: Dict[str, Any], risk_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'error' in district_data or 'error' in risk_data:
            return {'recommendations': [], 'priority_count': {}}
        
        combined_data = {**district_data, **risk_data}
        
        recommendations = []
        priority_count = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for rule_name, rule in self.recommendation_rules.items():
            if rule['condition'](combined_data):
                recommendations.append({
                    'intervention': rule['intervention'],
                    'priority': rule['priority'],
                    'description': rule['description'],
                    'expected_impact': rule['expected_impact']
                })
                priority_count[rule['priority']] += 1
        
        recommendations.sort(key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['priority']])
        
        return {
            'recommendations': recommendations,
            'total_recommendations': len(recommendations),
            'priority_breakdown': priority_count
        }
    
    def generate_policy_insights(self, analytics_engine, risk_engine) -> Dict[str, Any]:
        national_overview = analytics_engine.get_national_overview()
        risk_distribution = risk_engine.get_risk_distribution()
        top_risk = risk_engine.get_top_risk_districts(20)
        
        insights = []
        
        coverage_gap = national_overview.get('coverage_gap', 0)
        if coverage_gap > 0.3:
            insights.append({
                'category': 'National Coverage',
                'severity': 'high',
                'insight': f"National coverage gap is {coverage_gap*100:.1f}%. Approximately {int(national_overview['total_population'] * coverage_gap)} individuals remain unenrolled.",
                'recommendation': 'Launch nationwide enrollment acceleration program targeting uncovered populations.'
            })
        
        youth_penetration = national_overview.get('youth_penetration_rate', 0)
        adult_penetration = national_overview.get('adult_penetration_rate', 0)
        
        if abs(youth_penetration - adult_penetration) > 0.2:
            if youth_penetration < adult_penetration:
                insights.append({
                    'category': 'Youth Inclusion',
                    'severity': 'high',
                    'insight': f"Youth penetration ({youth_penetration*100:.1f}%) lags behind adult penetration ({adult_penetration*100:.1f}%) by {abs(youth_penetration - adult_penetration)*100:.1f} percentage points.",
                    'recommendation': 'Prioritize school-based enrollment drives and partnerships with educational institutions.'
                })
            else:
                insights.append({
                    'category': 'Adult Inclusion',
                    'severity': 'medium',
                    'insight': f"Adult penetration ({adult_penetration*100:.1f}%) lags behind youth penetration ({youth_penetration*100:.1f}%) by {abs(youth_penetration - adult_penetration)*100:.1f} percentage points.",
                    'recommendation': 'Deploy workplace and community-based enrollment campaigns for adults.'
                })
        
        high_risk_count = risk_distribution['overall_distribution'].get('High Risk', 0)
        total_districts = risk_distribution['total_districts']
        
        if high_risk_count > total_districts * 0.2:
            insights.append({
                'category': 'Risk Concentration',
                'severity': 'critical',
                'insight': f"{high_risk_count} districts ({high_risk_count/total_districts*100:.1f}%) are classified as high-risk, indicating systemic challenges.",
                'recommendation': 'Establish dedicated task force for high-risk districts with enhanced resources and monitoring.'
            })
        
        state_risk_summary = risk_distribution['state_risk_summary']
        high_risk_states = [s for s in state_risk_summary if s['avg_risk_score'] > 0.6]
        
        if high_risk_states:
            state_names = [s['state'] for s in high_risk_states[:5]]
            insights.append({
                'category': 'State-Level Challenges',
                'severity': 'high',
                'insight': f"{len(high_risk_states)} states show elevated average risk scores. Top concerns: {', '.join(state_names)}.",
                'recommendation': 'Provide state-specific technical assistance and additional funding allocation.'
            })
        
        return {
            'insights': insights,
            'total_insights': len(insights),
            'critical_issues': sum(1 for i in insights if i['severity'] == 'critical'),
            'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def generate_state_insights(self, state_name: str, analytics_engine, risk_engine) -> Dict[str, Any]:
        state_overview = analytics_engine.get_state_overview(state_name)
        
        if 'error' in state_overview:
            return {'error': 'State not found'}
        
        state_risk_data = risk_engine.risk_scores[risk_engine.risk_scores['state'] == state_name]
        
        insights = []
        
        avg_penetration = state_overview.get('avg_penetration_rate', 0)
        if avg_penetration < 0.5:
            insights.append({
                'category': 'State Penetration',
                'severity': 'high',
                'insight': f"{state_name} has an average penetration rate of {avg_penetration*100:.1f}%, below the recommended threshold.",
                'recommendation': 'Implement state-wide enrollment acceleration program.'
            })
        
        high_risk_districts = state_risk_data[state_risk_data['composite_risk_score'] > 0.6]
        if len(high_risk_districts) > 0:
            top_districts = high_risk_districts.nlargest(5, 'composite_risk_score')['district'].tolist()
            insights.append({
                'category': 'High-Risk Districts',
                'severity': 'critical',
                'insight': f"{len(high_risk_districts)} districts in {state_name} are high-risk. Priority districts: {', '.join(top_districts[:3])}.",
                'recommendation': 'Deploy rapid response teams to high-risk districts for immediate intervention.'
            })
        
        avg_state_risk = state_risk_data['composite_risk_score'].mean()
        insights.append({
            'category': 'Overall State Risk',
            'severity': 'medium' if avg_state_risk < 0.5 else 'high',
            'insight': f"{state_name} has an average risk score of {avg_state_risk:.2f}.",
            'recommendation': 'Continue monitoring and adjust intervention strategies based on district-level performance.'
        })
        
        return {
            'state': state_name,
            'insights': insights,
            'total_insights': len(insights),
            'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        }