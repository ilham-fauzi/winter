"""
Background counting utilities for Winter.
"""

import threading
import time
from typing import Optional, Callable, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()

class BackgroundCounter:
    """Handles background counting of query results."""
    
    def __init__(self, client, query: str):
        self.client = client
        self.query = query
        self.total_count = None
        self.is_running = False
        self.error = None
        self.thread = None
        self.start_time = None
        
    def _create_count_query(self, original_query: str) -> str:
        """Create a COUNT query from the original query."""
        # Simple approach: wrap the original query in a subquery
        # This works for most SELECT queries
        return f"SELECT COUNT(*) as total_count FROM ({original_query}) as count_query"
    
    def _run_count_query(self):
        """Run the count query in background."""
        try:
            self.is_running = True
            self.start_time = time.time()
            
            # Create count query
            count_query = self._create_count_query(self.query)
            
            # Execute count query
            columns, results = self.client.execute_query_with_columns(count_query)
            
            if results and len(results) > 0:
                self.total_count = results[0][0]  # First row, first column
            else:
                self.total_count = 0
                
        except Exception as e:
            self.error = str(e)
            self.total_count = None
        finally:
            self.is_running = False
    
    def start_counting(self):
        """Start background counting."""
        if self.is_running:
            return
            
        self.thread = threading.Thread(target=self._run_count_query, daemon=True)
        self.thread.start()
    
    def get_status(self) -> dict:
        """Get current counting status."""
        return {
            'is_running': self.is_running,
            'total_count': self.total_count,
            'error': self.error,
            'elapsed_time': time.time() - self.start_time if self.start_time else 0
        }
    
    def wait_for_completion(self, timeout: float = 10.0) -> bool:
        """Wait for counting to complete with timeout."""
        if not self.thread:
            return False
            
        self.thread.join(timeout=timeout)
        return not self.is_running

def show_live_counting_progress(counter: BackgroundCounter, display_callback: Callable[[str], None]):
    """Show live counting progress with real-time updates."""
    
    import time
    
    # Show initial progress
    display_callback("🔍 Counting total records in background...")
    
    # Monitor progress with live updates
    start_time = time.time()
    last_update = 0
    
    while counter.is_running and (time.time() - start_time) < 15:  # 15 second timeout
        current_time = time.time()
        
        # Update every 0.5 seconds
        if current_time - last_update >= 0.5:
            elapsed = current_time - start_time
            
            if elapsed < 2:
                message = "🔍 Counting total records..."
            elif elapsed < 5:
                message = f"🔍 Counting total records... ({elapsed:.1f}s)"
            else:
                message = f"🔍 Counting total records... ({elapsed:.1f}s) - Large dataset detected"
            
            display_callback(message)
            last_update = current_time
        
        time.sleep(0.1)  # Check every 100ms
    
    # Final status check
    status = counter.get_status()
    if not status['is_running'] and status['total_count'] is not None:
        display_callback(f"📈 Total records: {status['total_count']:,}")
    elif status['error']:
        display_callback(f"⚠️  Count failed: {status['error']}")
    else:
        display_callback("⏱️  Counting timed out - dataset may be very large")

def get_query_total_count(client, query: str, timeout: float = 5.0) -> Optional[int]:
    """Get total count for a query with timeout."""
    counter = BackgroundCounter(client, query)
    counter.start_counting()
    
    # Wait for completion
    if counter.wait_for_completion(timeout):
        return counter.total_count
    else:
        console.print(f"⏱️  Count query timed out after {timeout}s")
        return None

def display_query_summary(query: str, displayed_rows: int, total_rows: Optional[int], 
                         columns: int, execution_time: float):
    """Display comprehensive query summary."""
    
    # Base summary
    summary_parts = [
        f"📊 Query Results: {displayed_rows:,} rows displayed",
        f"📋 Columns: {columns}",
        f"⏱️  Execution time: {execution_time:.2f}s"
    ]
    
    # Add total count if available
    if total_rows is not None:
        if total_rows > displayed_rows:
            summary_parts.append(f"📈 Total records: {total_rows:,}")
            summary_parts.append(f"📄 Showing {displayed_rows:,} of {total_rows:,} records")
        else:
            summary_parts.append(f"📈 Total records: {total_rows:,}")
    else:
        summary_parts.append("📈 Total count: Not available")
    
    # Create summary panel
    summary_text = " | ".join(summary_parts)
    
    summary_panel = Panel(
        summary_text,
        title="Query Summary",
        border_style="green"
    )
    
    console.print(summary_panel)
