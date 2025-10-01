"""
Data formatters for different column types.
"""

from typing import Any, Optional, Union
from datetime import datetime, date
import re
from decimal import Decimal


class DataFormatter:
    """Format data based on its type and content."""
    
    def __init__(self):
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        self.datetime_patterns = [
            r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',   # YYYY-MM-DDTHH:MM:SS
        ]
    
    def detect_data_type(self, value: Any) -> str:
        """Detect the data type of a value."""
        if value is None:
            return "null"
        
        value_str = str(value)
        
        # Check for datetime
        for pattern in self.datetime_patterns:
            if re.match(pattern, value_str):
                return "datetime"
        
        # Check for date
        for pattern in self.date_patterns:
            if re.match(pattern, value_str):
                return "date"
        
        # Check for numeric types
        try:
            float(value_str)
            if '.' in value_str:
                return "decimal"
            else:
                return "integer"
        except (ValueError, TypeError):
            pass
        
        # Check for boolean
        if value_str.lower() in ['true', 'false', '1', '0', 'yes', 'no']:
            return "boolean"
        
        # Default to text
        return "text"
    
    def format_value(self, value: Any, data_type: Optional[str] = None, 
                    max_length: int = 50) -> str:
        """Format a value based on its detected or specified type."""
        if value is None:
            return "[dim]NULL[/dim]"
        
        if data_type is None:
            data_type = self.detect_data_type(value)
        
        value_str = str(value)
        
        # Truncate long text
        if len(value_str) > max_length:
            value_str = value_str[:max_length-3] + "..."
        
        # Apply type-specific formatting
        if data_type == "datetime":
            return f"[blue]{value_str}[/blue]"
        elif data_type == "date":
            return f"[cyan]{value_str}[/cyan]"
        elif data_type == "integer":
            return f"[green]{value_str}[/green]"
        elif data_type == "decimal":
            return f"[yellow]{value_str}[/yellow]"
        elif data_type == "boolean":
            if value_str.lower() in ['true', '1', 'yes']:
                return "[green]✓[/green]"
            else:
                return "[red]✗[/red]"
        else:  # text
            return value_str
    
    def format_number(self, value: Any, decimals: int = 2, 
                     thousands_separator: bool = True) -> str:
        """Format a number with specified decimal places and separators."""
        try:
            num = float(value)
            
            # Format with decimals
            if decimals == 0:
                formatted = f"{int(num):,}" if thousands_separator else str(int(num))
            else:
                formatted = f"{num:,.{decimals}f}" if thousands_separator else f"{num:.{decimals}f}"
            
            return f"[green]{formatted}[/green]"
        except (ValueError, TypeError):
            return str(value)
    
    def format_percentage(self, value: Any, decimals: int = 1) -> str:
        """Format a value as percentage."""
        try:
            num = float(value)
            formatted = f"{num:.{decimals}f}%"
            return f"[yellow]{formatted}[/yellow]"
        except (ValueError, TypeError):
            return str(value)


class ColumnAnalyzer:
    """Analyze columns to determine their characteristics."""
    
    def __init__(self):
        self.formatter = DataFormatter()
    
    def analyze_column(self, column_name: str, values: list) -> dict:
        """Analyze a column and return its characteristics."""
        if not values:
            return {
                "name": column_name,
                "type": "unknown",
                "null_count": 0,
                "unique_count": 0,
                "sample_values": []
            }
        
        # Remove None values for analysis
        non_null_values = [v for v in values if v is not None]
        
        # Detect most common data type
        type_counts = {}
        for value in non_null_values[:100]:  # Sample first 100 values
            data_type = self.formatter.detect_data_type(value)
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
        
        most_common_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else "text"
        
        # Calculate statistics
        null_count = len(values) - len(non_null_values)
        unique_count = len(set(str(v) for v in non_null_values))
        
        # Get sample values
        sample_values = non_null_values[:5]
        
        return {
            "name": column_name,
            "type": most_common_type,
            "null_count": null_count,
            "unique_count": unique_count,
            "total_count": len(values),
            "sample_values": sample_values,
            "type_distribution": type_counts
        }
    
    def suggest_column_width(self, column_name: str, values: list, 
                           min_width: int = 10, max_width: int = 50) -> int:
        """Suggest optimal column width based on content."""
        if not values:
            return min_width
        
        # Calculate width based on column name and content
        name_width = len(column_name)
        
        # Sample some values to calculate content width
        sample_values = [str(v) for v in values[:20] if v is not None]
        if sample_values:
            content_width = max(len(v) for v in sample_values)
        else:
            content_width = 0
        
        # Use the larger of name width and content width
        suggested_width = max(name_width, content_width)
        
        # Apply constraints
        return max(min_width, min(suggested_width, max_width))
