"""
Advanced Business Intelligence Analysis Module
Provides strategic business insights, KPIs, and performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessAnalyzer:
    """
    Advanced business intelligence analyzer for strategic insights.
    """

    def __init__(self):
        """Initialize BusinessAnalyzer."""
        self.data: Optional[pd.DataFrame] = None
        self.business_metrics: Dict[str, Any] = {}

    def load_data(self, data: pd.DataFrame) -> None:
        """Load data for business analysis."""
        self.data = data
        logger.info(f"Business data loaded: {len(self.data)} rows")

    def calculate_business_kpis(self) -> Dict[str, Any]:
        """
        Calculate key business performance indicators.
        Automatically detects revenue, cost, profit, customer metrics.
        """
        if self.data is None:
            raise ValueError("No data provided")
        
        kpis = {}
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Detect key business columns
        revenue_cols = [col for col in self.data.columns if any(term in col.lower() 
                       for term in ['revenue', 'sales', 'income', 'earning'])]
        cost_cols = [col for col in self.data.columns if any(term in col.lower() 
                    for term in ['cost', 'expense', 'spend', 'investment'])]
        customer_cols = [col for col in self.data.columns if any(term in col.lower() 
                       for term in ['customer', 'user', 'client', 'visitor'])]
        conversion_cols = [col for col in self.data.columns if any(term in col.lower() 
                          for term in ['conversion', 'purchase', 'order', 'transaction'])]
        
        # Calculate Revenue Metrics
        if revenue_cols:
            revenue_col = revenue_cols[0]
            kpis['total_revenue'] = float(self.data[revenue_col].sum())
            kpis['avg_revenue'] = float(self.data[revenue_col].mean())
            kpis['revenue_growth'] = self._calculate_growth_rate(revenue_col)
            kpis['revenue_trend'] = self._analyze_trend(revenue_col)
        
        # Calculate Profit Metrics
        if revenue_cols and cost_cols:
            revenue_col = revenue_cols[0]
            cost_col = cost_cols[0]
            profit = self.data[revenue_col] - self.data[cost_col]
            kpis['total_profit'] = float(profit.sum())
            kpis['profit_margin'] = float((profit.sum() / self.data[revenue_col].sum()) * 100) if self.data[revenue_col].sum() > 0 else 0
            kpis['roi'] = float((profit.sum() / self.data[cost_col].sum()) * 100) if self.data[cost_col].sum() > 0 else 0
            kpis['cost_efficiency'] = float(self.data[revenue_col].sum() / self.data[cost_col].sum()) if self.data[cost_col].sum() > 0 else 0
        
        # Calculate Conversion Metrics
        if conversion_cols and customer_cols:
            conversion_col = conversion_cols[0]
            customer_col = customer_cols[0]
            if customer_col in numeric_cols:
                kpis['conversion_rate'] = float((self.data[conversion_col].sum() / self.data[customer_col].sum()) * 100) if self.data[customer_col].sum() > 0 else 0
                kpis['revenue_per_customer'] = float(kpis.get('total_revenue', 0) / self.data[customer_col].sum()) if self.data[customer_col].sum() > 0 else 0
        
        # Calculate Performance Metrics
        if len(numeric_cols) >= 2:
            # Find best and worst performing segments
            for col in numeric_cols[:3]:  # Top 3 numeric columns
                if col in self.data.columns:
                    kpis[f'{col}_best_performer'] = self._find_best_performer(col)
                    kpis[f'{col}_worst_performer'] = self._find_worst_performer(col)
        
        # Market Share Analysis
        if revenue_cols:
            revenue_col = revenue_cols[0]
            categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
            if categorical_cols:
                segment_col = categorical_cols[0]
                market_share = self.data.groupby(segment_col)[revenue_col].sum()
                total = market_share.sum()
                kpis['market_share'] = {segment: float((share / total) * 100) 
                                       for segment, share in market_share.items()}
        
        self.business_metrics['kpis'] = kpis
        logger.info(f"Calculated {len(kpis)} business KPIs")
        return kpis

    def generate_swot_analysis(self, context: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Generate SWOT (Strengths, Weaknesses, Opportunities, Threats) analysis.
        """
        swot = {
            'strengths': [],
            'weaknesses': [],
            'opportunities': [],
            'threats': []
        }
        
        if self.data is None:
            return swot
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        
        # Analyze strengths (high performing metrics)
        for col in numeric_cols[:5]:
            if col in self.data.columns:
                mean_val = self.data[col].mean()
                std_val = self.data[col].std()
                if mean_val > 0 and std_val > 0:
                    # High performers (above mean + 0.5*std)
                    threshold = mean_val + 0.5 * std_val
                    high_performers = self.data[self.data[col] > threshold]
                    if len(high_performers) > 0:
                        swot['strengths'].append(f"Strong performance in {col} with {len(high_performers)} high-performing segments")
        
        # Analyze weaknesses (low performing metrics)
        for col in numeric_cols[:5]:
            if col in self.data.columns:
                mean_val = self.data[col].mean()
                std_val = self.data[col].std()
                if mean_val > 0 and std_val > 0:
                    # Low performers (below mean - 0.5*std)
                    threshold = mean_val - 0.5 * std_val
                    low_performers = self.data[self.data[col] < threshold]
                    if len(low_performers) > 0:
                        swot['weaknesses'].append(f"Underperformance in {col} with {len(low_performers)} segments below average")
        
        # Opportunities (growth potential)
        for col in numeric_cols[:3]:
            if col in self.data.columns:
                growth = self._calculate_growth_rate(col)
                if growth and growth > 0:
                    swot['opportunities'].append(f"Growing trend in {col} indicates expansion opportunity")
        
        # Threats (declining trends)
        for col in numeric_cols[:3]:
            if col in self.data.columns:
                growth = self._calculate_growth_rate(col)
                if growth and growth < 0:
                    swot['threats'].append(f"Declining trend in {col} requires immediate attention")
        
        self.business_metrics['swot'] = swot
        return swot

    def identify_growth_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify specific growth opportunities with potential impact.
        """
        opportunities = []
        
        if self.data is None:
            return opportunities
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
        
        # Find high-value segments with growth potential
        if categorical_cols and numeric_cols:
            segment_col = categorical_cols[0]
            metric_col = numeric_cols[0]
            
            segment_performance = self.data.groupby(segment_col)[metric_col].agg(['mean', 'count', 'std'])
            avg_performance = segment_performance['mean'].mean()
            
            for segment, row in segment_performance.iterrows():
                if row['mean'] > avg_performance * 1.2:  # 20% above average
                    opportunities.append({
                        'segment': str(segment),
                        'metric': metric_col,
                        'current_value': float(row['mean']),
                        'potential': 'High - Already performing well, scale this segment',
                        'impact': 'High',
                        'effort': 'Low'
                    })
                elif row['mean'] < avg_performance * 0.8:  # 20% below average
                    opportunities.append({
                        'segment': str(segment),
                        'metric': metric_col,
                        'current_value': float(row['mean']),
                        'potential': f'Medium - Improve to reach average of {avg_performance:.2f}',
                        'impact': 'Medium',
                        'effort': 'Medium'
                    })
        
        self.business_metrics['growth_opportunities'] = opportunities
        return opportunities

    def calculate_risk_factors(self) -> Dict[str, Any]:
        """
        Calculate business risk factors and vulnerabilities.
        """
        risks = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': []
        }
        
        if self.data is None:
            return risks
        
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
        
        # High variance indicates instability
        for col in numeric_cols[:5]:
            if col in self.data.columns:
                cv = self.data[col].std() / self.data[col].mean() if self.data[col].mean() != 0 else 0
                if cv > 0.5:  # Coefficient of variation > 50%
                    risks['high_risk'].append({
                        'metric': col,
                        'issue': 'High volatility',
                        'coefficient_of_variation': float(cv),
                        'recommendation': 'Implement stability measures and risk mitigation'
                    })
                elif cv > 0.3:
                    risks['medium_risk'].append({
                        'metric': col,
                        'issue': 'Moderate volatility',
                        'coefficient_of_variation': float(cv)
                    })
        
        # Declining trends
        for col in numeric_cols[:3]:
            growth = self._calculate_growth_rate(col)
            if growth and growth < -10:  # More than 10% decline
                risks['high_risk'].append({
                    'metric': col,
                    'issue': 'Significant decline',
                    'growth_rate': float(growth),
                    'recommendation': 'Immediate intervention required'
                })
        
        self.business_metrics['risks'] = risks
        return risks

    def generate_strategic_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate prioritized strategic recommendations.
        """
        recommendations = []
        
        kpis = self.business_metrics.get('kpis', {})
        opportunities = self.business_metrics.get('growth_opportunities', [])
        risks = self.business_metrics.get('risks', {})
        
        # High-impact, low-effort opportunities
        for opp in opportunities:
            if opp.get('impact') == 'High' and opp.get('effort') == 'Low':
                recommendations.append({
                    'priority': 'P0 - Immediate',
                    'action': f"Scale {opp.get('segment')} segment",
                    'rationale': opp.get('potential'),
                    'expected_impact': 'High revenue growth',
                    'timeline': '1-2 months',
                    'effort': 'Low'
                })
        
        # Risk mitigation
        for risk in risks.get('high_risk', []):
            recommendations.append({
                'priority': 'P0 - Critical',
                'action': f"Address volatility in {risk.get('metric')}",
                'rationale': risk.get('issue'),
                'expected_impact': 'Stability improvement',
                'timeline': 'Immediate',
                'effort': 'High'
            })
        
        # Profit optimization
        if kpis.get('profit_margin', 0) < 20:
            recommendations.append({
                'priority': 'P1 - High',
                'action': 'Improve profit margins',
                'rationale': f"Current margin: {kpis.get('profit_margin', 0):.1f}% is below optimal",
                'expected_impact': 'Increase profitability by 5-10%',
                'timeline': '3-6 months',
                'effort': 'Medium'
            })
        
        # Growth acceleration
        if kpis.get('revenue_growth', 0) < 10:
            recommendations.append({
                'priority': 'P1 - High',
                'action': 'Accelerate revenue growth',
                'rationale': f"Current growth: {kpis.get('revenue_growth', 0):.1f}% needs improvement",
                'expected_impact': 'Double-digit growth',
                'timeline': '6-12 months',
                'effort': 'High'
            })
        
        self.business_metrics['strategic_recommendations'] = recommendations
        return recommendations

    def _calculate_growth_rate(self, column: str) -> Optional[float]:
        """Calculate growth rate for a column."""
        if column not in self.data.columns:
            return None
        
        try:
            values = self.data[column].dropna().values
            if len(values) < 2:
                return None
            
            # Simple growth rate: (last - first) / first * 100
            first_val = values[0]
            last_val = values[-1]
            
            if first_val != 0:
                return float(((last_val - first_val) / abs(first_val)) * 100)
            return None
        except:
            return None

    def _analyze_trend(self, column: str) -> str:
        """Analyze trend direction."""
        growth = self._calculate_growth_rate(column)
        if growth is None:
            return "stable"
        elif growth > 5:
            return "strongly_increasing"
        elif growth > 0:
            return "increasing"
        elif growth > -5:
            return "stable"
        else:
            return "decreasing"

    def _find_best_performer(self, column: str) -> Dict[str, Any]:
        """Find best performing segment."""
        if self.data is None:
            return {}
        
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
        if not categorical_cols:
            return {'value': float(self.data[column].max())}
        
        segment_col = categorical_cols[0]
        segment_perf = self.data.groupby(segment_col)[column].mean()
        best_segment = segment_perf.idxmax()
        
        return {
            'segment': str(best_segment),
            'value': float(segment_perf.max()),
            'metric': column
        }

    def _find_worst_performer(self, column: str) -> Dict[str, Any]:
        """Find worst performing segment."""
        if self.data is None:
            return {}
        
        categorical_cols = self.data.select_dtypes(include=['object']).columns.tolist()
        if not categorical_cols:
            return {'value': float(self.data[column].min())}
        
        segment_col = categorical_cols[0]
        segment_perf = self.data.groupby(segment_col)[column].mean()
        worst_segment = segment_perf.idxmin()
        
        return {
            'segment': str(worst_segment),
            'value': float(segment_perf.min()),
            'metric': column
        }

    def get_all_business_metrics(self) -> Dict[str, Any]:
        """Get all calculated business metrics."""
        return self.business_metrics

