"""
Data Analysis Module
Performs data aggregation and key insight extraction
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataAnalyzer:
    """
    Analyzes data to extract key metrics and insights.
    """

    def __init__(self):
        """Initialize DataAnalyzer."""
        self.data: Optional[pd.DataFrame] = None
        self.metrics: Dict[str, Any] = {}

    def load_data(self, data: pd.DataFrame) -> None:
        """Load data for analysis."""
        self.data = data
        logger.info(f"Data loaded for analysis: {len(data)} rows")

    def calculate_basic_statistics(
        self,
        data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Calculate basic statistical measures.
        
        Args:
            data: DataFrame to analyze (uses self.data if not provided)
            
        Returns:
            Dictionary of statistics
        """
        if data is None:
            data = self.data
        
        if data is None:
            raise ValueError("No data provided for analysis")
        
        stats = {}
        
        try:
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            
            for col in numeric_cols:
                stats[col] = {
                    "mean": float(data[col].mean()),
                    "median": float(data[col].median()),
                    "std": float(data[col].std()),
                    "min": float(data[col].min()),
                    "max": float(data[col].max()),
                    "count": int(data[col].count()),
                    "null_count": int(data[col].isna().sum())
                }
            
            self.metrics["basic_statistics"] = stats
            logger.info(f"Calculated statistics for {len(numeric_cols)} columns")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            raise

    def calculate_trends(
        self,
        data: Optional[pd.DataFrame] = None,
        date_column: Optional[str] = None,
        value_column: Optional[str] = None,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Calculate trends over time.
        
        Args:
            data: DataFrame to analyze
            date_column: Name of date column
            value_column: Name of value column to trend
            period: Time period for aggregation ('daily', 'weekly', 'monthly')
            
        Returns:
            Trend data and analysis
        """
        if data is None:
            data = self.data
        
        if data is None or date_column is None or value_column is None:
            raise ValueError("Data, date_column, and value_column required")
        
        try:
            # Convert to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(data[date_column]):
                data[date_column] = pd.to_datetime(data[date_column])
            
            # Group by period
            if period == "daily":
                grouped = data.groupby(data[date_column].dt.date)
            elif period == "weekly":
                grouped = data.groupby(data[date_column].dt.to_period('W'))
            elif period == "monthly":
                grouped = data.groupby(data[date_column].dt.to_period('M'))
            else:
                grouped = data.groupby(data[date_column].dt.date)
            
            trend_data = grouped[value_column].agg(['sum', 'mean', 'count'])
            # Convert to simple dict with dates as keys and sum as values
            trend = {}
            for idx, row in trend_data.iterrows():
                trend[str(idx)] = float(row['sum'])
            
            # Calculate trend direction
            if len(trend) >= 2:
                values = list(trend.values())
                if all(isinstance(v, (int, float)) for v in values):
                    trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "insufficient_data"
            
            trend_result = {
                "trend_data": trend,
                "trend_direction": trend_direction,
                "period": period
            }
            
            self.metrics["trends"] = trend_result
            logger.info(f"Calculated {period} trends")
            return trend_result
            
        except Exception as e:
            logger.error(f"Error calculating trends: {str(e)}")
            raise

    def calculate_correlations(
        self,
        data: Optional[pd.DataFrame] = None,
        columns: Optional[list] = None,
        method: str = "pearson"
    ) -> Dict[str, Any]:
        """
        Calculate correlations between numeric columns.
        
        Args:
            data: DataFrame to analyze
            columns: Specific columns to correlate
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Correlation matrix
        """
        if data is None:
            data = self.data
        
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            if columns:
                numeric_data = numeric_data[[col for col in columns if col in numeric_data.columns]]
            
            corr_matrix = numeric_data.corr(method=method)
            correlations = corr_matrix.to_dict()
            
            self.metrics["correlations"] = correlations
            logger.info(f"Calculated {method} correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
            raise

    def get_summary_insights(
        self,
        data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive summary of data insights.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            Summary insights dictionary
        """
        if data is None:
            data = self.data
        
        try:
            summary = {
                "total_rows": len(data),
                "total_columns": len(data.columns),
                "columns": list(data.columns),
                "shape": (len(data), len(data.columns)),
                "dtypes": data.dtypes.to_dict(),
                "memory_usage": data.memory_usage(deep=True).sum()
            }
            
            logger.info("Generated summary insights")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get all calculated metrics."""
        return self.metrics
