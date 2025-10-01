"""
Export functionality for Winter terminal client.
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import pandas as pd

console = Console()


class DataExporter:
    """Export query results to various formats."""
    
    def __init__(self):
        self.console = Console()
    
    def export_csv(self, results: List[tuple], columns: List[str], 
                   filename: str, delimiter: str = ',', 
                   encoding: str = 'utf-8') -> bool:
        """Export data to CSV format."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Exporting to CSV...", total=None)
                
                # Ensure directory exists
                file_path = Path(filename)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', newline='', encoding=encoding) as csvfile:
                    writer = csv.writer(csvfile, delimiter=delimiter)
                    
                    # Write headers
                    writer.writerow(columns)
                    
                    # Write data rows
                    for row in results:
                        # Convert None values to empty strings for CSV
                        csv_row = [str(cell) if cell is not None else '' for cell in row]
                        writer.writerow(csv_row)
                
                progress.update(task, description="✅ CSV export completed")
                return True
                
        except Exception as e:
            self.console.print(f"❌ CSV export failed: {e}")
            return False
    
    def export_json(self, results: List[tuple], columns: List[str], 
                   filename: str, pretty: bool = True) -> bool:
        """Export data to JSON format."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Exporting to JSON...", total=None)
                
                # Ensure directory exists
                file_path = Path(filename)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert results to list of dictionaries
                data = []
                for row in results:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        if i < len(row):
                            # Convert None to null for JSON
                            value = row[i] if row[i] is not None else None
                            row_dict[col] = value
                        else:
                            row_dict[col] = None
                    data.append(row_dict)
                
                # Create export metadata
                export_data = {
                    "metadata": {
                        "exported_at": datetime.now().isoformat(),
                        "total_rows": len(results),
                        "total_columns": len(columns),
                        "columns": columns
                    },
                    "data": data
                }
                
                # Write JSON file
                with open(file_path, 'w', encoding='utf-8') as jsonfile:
                    if pretty:
                        json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
                    else:
                        json.dump(export_data, jsonfile, ensure_ascii=False)
                
                progress.update(task, description="✅ JSON export completed")
                return True
                
        except Exception as e:
            self.console.print(f"❌ JSON export failed: {e}")
            return False
    
    def export_excel(self, results: List[tuple], columns: List[str], 
                    filename: str, sheet_name: str = "Query Results") -> bool:
        """Export data to Excel format."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Exporting to Excel...", total=None)
                
                # Ensure directory exists
                file_path = Path(filename)
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Convert to DataFrame
                df = pd.DataFrame(results, columns=columns)
                
                # Create Excel writer with formatting
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    # Get the workbook and worksheet
                    workbook = writer.book
                    worksheet = writer.sheets[sheet_name]
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                    
                    # Format header row
                    from openpyxl.styles import Font, PatternFill
                    header_font = Font(bold=True)
                    header_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
                    
                    for cell in worksheet[1]:
                        cell.font = header_font
                        cell.fill = header_fill
                
                progress.update(task, description="✅ Excel export completed")
                return True
                
        except Exception as e:
            self.console.print(f"❌ Excel export failed: {e}")
            return False
    
    def export_multiple_formats(self, results: List[tuple], columns: List[str], 
                              base_filename: str, formats: List[str] = None) -> Dict[str, bool]:
        """Export data to multiple formats."""
        if formats is None:
            formats = ['csv', 'json', 'xlsx']
        
        # Remove extension from base filename
        base_name = Path(base_filename).stem
        
        results_status = {}
        
        for format_type in formats:
            if format_type.lower() == 'csv':
                filename = f"{base_name}.csv"
                results_status['csv'] = self.export_csv(results, columns, filename)
            elif format_type.lower() == 'json':
                filename = f"{base_name}.json"
                results_status['json'] = self.export_json(results, columns, filename)
            elif format_type.lower() in ['excel', 'xlsx']:
                filename = f"{base_name}.xlsx"
                results_status['xlsx'] = self.export_excel(results, columns, filename)
        
        return results_status
    
    def generate_filename(self, query: str, format_type: str, 
                         timestamp: bool = True) -> str:
        """Generate a filename based on query and format."""
        # Clean query for filename
        clean_query = query.replace(' ', '_').replace('*', 'all')
        clean_query = ''.join(c for c in clean_query if c.isalnum() or c in '_-')
        clean_query = clean_query[:50]  # Limit length
        
        if timestamp:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"winter_export_{clean_query}_{timestamp_str}.{format_type}"
        else:
            filename = f"winter_export_{clean_query}.{format_type}"
        
        return filename


class ExportManager:
    """Manage export operations and settings."""
    
    def __init__(self):
        self.exporter = DataExporter()
        self.default_output_dir = Path.home() / "Downloads" / "winter_exports"
        self.default_output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_query_results(self, results: List[tuple], columns: List[str], 
                           query: str, format_type: str = 'csv',
                           output_dir: Optional[str] = None,
                           filename: Optional[str] = None) -> bool:
        """Export query results with automatic filename generation."""
        
        # Determine output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.default_output_dir
        
        # Generate filename if not provided
        if not filename:
            filename = self.exporter.generate_filename(query, format_type)
        
        # If filename is provided, ensure it has the correct extension
        if filename and not filename.endswith(f'.{format_type}'):
            filename = f"{filename}.{format_type}"
        
        full_path = output_path / filename
        
        # Export based on format
        if format_type.lower() == 'csv':
            return self.exporter.export_csv(results, columns, str(full_path))
        elif format_type.lower() == 'json':
            return self.exporter.export_json(results, columns, str(full_path))
        elif format_type.lower() in ['excel', 'xlsx']:
            return self.exporter.export_excel(results, columns, str(full_path))
        else:
            console.print(f"❌ Unsupported format: {format_type}")
            return False
    
    def get_export_summary(self, results: List[tuple], columns: List[str]) -> Dict[str, Any]:
        """Get summary information for export."""
        return {
            "total_rows": len(results),
            "total_columns": len(columns),
            "columns": columns,
            "estimated_sizes": {
                "csv": f"{len(results) * len(columns) * 10} bytes (estimated)",
                "json": f"{len(results) * len(columns) * 20} bytes (estimated)",
                "excel": f"{len(results) * len(columns) * 15} bytes (estimated)"
            }
        }
