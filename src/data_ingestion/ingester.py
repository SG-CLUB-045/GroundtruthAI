"""
Data Ingestion Module
Handles ingestion from CSV and JSON files
"""

import pandas as pd
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataIngester:
    """
    Handles data ingestion from CSV and JSON files.
    """

    def __init__(self, use_polars: bool = False):
        """
        Initialize DataIngester.
        
        Args:
            use_polars: Not used (kept for compatibility)
        """
        self.data: Optional[pd.DataFrame] = None
        self.metadata: Dict[str, Any] = {}

    def from_csv(
        self,
        file_path: str,
        encoding: str = "utf-8",
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding
            **kwargs: Additional parameters for read_csv
            
        Returns:
            DataFrame
        """
        try:
            logger.info(f"Loading CSV from {file_path}")
            self.data = pd.read_csv(file_path, encoding=encoding, **kwargs)
            
            self.metadata["source"] = file_path
            self.metadata["source_type"] = "csv"
            self.metadata["rows"] = len(self.data)
            self.metadata["columns"] = list(self.data.columns)
            self.metadata["loaded_at"] = datetime.now().isoformat()
            
            logger.info(f"Successfully loaded {len(self.data)} rows from {file_path}")
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise

    def from_json(
        self,
        file_path: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load data from JSON file.
        
        Args:
            file_path: Path to JSON file
            **kwargs: Additional parameters
            
        Returns:
            DataFrame
        """
        try:
            logger.info(f"Loading JSON from {file_path}")
            self.data = pd.read_json(file_path, **kwargs)
            
            self.metadata["source"] = file_path
            self.metadata["source_type"] = "json"
            self.metadata["rows"] = len(self.data)
            self.metadata["columns"] = list(self.data.columns)
            self.metadata["loaded_at"] = datetime.now().isoformat()
            
            logger.info(f"Successfully loaded {len(self.data)} rows from {file_path}")
            return self.data
            
        except Exception as e:
            logger.error(f"Error loading JSON: {str(e)}")
            raise

    def clean_data(
        self,
        data: Optional[pd.DataFrame] = None,
        remove_duplicates: bool = True,
        handle_nulls: str = "drop"
    ) -> pd.DataFrame:
        """
        Clean data by handling duplicates and null values.
        
        Args:
            data: DataFrame to clean (uses self.data if not provided)
            remove_duplicates: Whether to remove duplicate rows
            handle_nulls: Strategy for handling null values ('drop', 'forward_fill', 'backward_fill', 'mean')
            
        Returns:
            Cleaned DataFrame
        """
        if data is None:
            data = self.data
        
        try:
            if remove_duplicates:
                data = data.drop_duplicates()
            
            if handle_nulls == "drop":
                data = data.dropna()
            elif handle_nulls == "forward_fill":
                data = data.ffill()
            elif handle_nulls == "backward_fill":
                data = data.bfill()
            elif handle_nulls == "mean":
                numeric_cols = data.select_dtypes(include=["number"]).columns
                data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())
            
            logger.info(f"Data cleaning applied: duplicates={remove_duplicates}, nulls={handle_nulls}")
            self.data = data
            return data
            
        except Exception as e:
            logger.error(f"Error cleaning data: {str(e)}")
            raise

    def get_data(self) -> pd.DataFrame:
        """Get current data."""
        return self.data

    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata about loaded data."""
        return self.metadata
