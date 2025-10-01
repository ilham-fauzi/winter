"""
UI components for table display and scrolling.
"""

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from typing import List, Any, Tuple
import time
from winter.formatters import DataFormatter, ColumnAnalyzer

# Try to import keyboard for arrow key support
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# Simple single-character input without Enter
def get_single_char():
    """Get a single character without requiring Enter."""
    import sys
    import tty
    import termios
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_user_input():
    """Get user input with fallback to regular input."""
    try:
        return get_single_char()
    except:
        # Fallback to regular input for testing
        return input("Enter command (l/r/u/d/q/i/h): ").strip()

def get_arrow_key():
    """Get arrow key input properly."""
    try:
        # Try to get single character input
        key = get_single_char()
        
        if key == '\x1b':  # ESC character (arrow keys)
            # Read the next two characters to determine arrow key
            key2 = get_single_char()
            if key2 == '[':
                key3 = get_single_char()
                if key3 == 'A':  # Up arrow
                    return 'u'
                elif key3 == 'B':  # Down arrow
                    return 'd'
                elif key3 == 'C':  # Right arrow
                    return 'r'
                elif key3 == 'D':  # Left arrow
                    return 'l'
        
        # Handle regular characters
        if key.lower() in ['w', 'a', 's', 'd', 'q', 'i', 'h']:
            return key.lower()
        
        return key
    except:
        # Fallback to regular input
        return input("Enter command (l/r/u/d/q/i/h): ").strip()


class TableViewer:
    """Display query results in a scrollable table."""
    
    def __init__(self):
        self.console = Console()
    
    def display_table(self, results: List[tuple], columns: List[str] = None):
        """Display results in a table format."""
        table = Table(show_header=True, header_style="bold magenta")
        
        # Add columns
        if columns:
            for col in columns:
                table.add_column(col)
        else:
            # Use generic column names if not provided
            for i in range(len(results[0]) if results else 0):
                table.add_column(f"Column {i+1}")
        
        # Add rows
        for row in results:
            table.add_row(*[str(cell) for cell in row])
        
        self.console.print(table)
    
    def display_message(self, message: str, style: str = "default"):
        """Display a message to the user."""
        self.console.print(message, style=style)


class InteractiveTableViewer:
    """Interactive table viewer with horizontal and vertical scrolling."""
    
    def __init__(self):
        self.console = Console()
        self.scroll_x = 0  # Horizontal scroll position
        self.scroll_y = 0  # Vertical scroll position
        self.page_size = 10  # Number of rows per page
        self.cols_per_page = 5  # Number of columns per page
        self.formatter = DataFormatter()
        self.analyzer = ColumnAnalyzer()
        self.column_info = {}  # Store column analysis results
    
    def display_interactive_table(self, results: List[tuple], columns: List[str], 
                                max_rows: int = 20, max_cols: int = 10):
        """Display interactive table with scrolling controls."""
        
        # Limit data
        display_results = results[:max_rows]
        display_cols = columns[:max_cols]
        
        # Analyze columns for formatting (analyze ALL columns, not just limited ones)
        self.console.print("🔍 Analyzing column data types...")
        self.column_info = {}
        for i, col in enumerate(columns):  # Use full columns list
            column_values = [row[i] for row in results if i < len(row)]
            self.column_info[col] = self.analyzer.analyze_column(col, column_values)
        
        # Calculate total pages (use original counts, not limited counts)
        total_rows = len(results)  # Use original results count
        total_cols = len(columns)  # Use original columns count
        max_row_page = max(0, total_rows - self.page_size)
        max_col_page = max(0, total_cols - self.cols_per_page)
        
        # Show controls
        self.console.print("\n🎮 Interactive Table Controls:")
        self.console.print("  ←/→ : Scroll horizontally OR pagination (smart navigation)")
        self.console.print("  ↑/↓ : Page navigation (previous/next page)")
        self.console.print("  i   : Show column information")
        self.console.print("  q   : Quit")
        self.console.print("  h   : Show help")
        self.console.print("\n💡 Use arrow keys or WASD for navigation (no Enter needed!)")
        self.console.print("🔄 Smart pagination: → at last columns = next page, ← at first columns = previous page")
        self.console.print("📄 Page navigation: ↑/↓ keys move by pages (10 rows at a time)")
        
        # Check if we have more data than can be displayed
        if total_rows <= self.page_size and total_cols <= self.cols_per_page:
            self.console.print("\n💡 All data fits in one view - no scrolling needed!")
            self.console.print("   Use 'i' to see column information or 'q' to quit")
        
        # Interactive loop
        try:
            while True:
                # Create table with current scroll position
                table = self._create_scrolled_table(results, columns)
                
                # Create status panel
                status_text = f"Rows: {self.scroll_y+1}-{min(self.scroll_y+self.page_size, total_rows)}/{total_rows} | "
                status_text += f"Cols: {self.scroll_x+1}-{min(self.scroll_x+self.cols_per_page, total_cols)}/{total_cols}"
                
                status_panel = Panel(
                    status_text,
                    title="Table Position",
                    border_style="green"
                )
                
                # Display everything
                # Clear screen more reliably
                import os
                os.system('clear' if os.name == 'posix' else 'cls')
                
                self.console.print(table)
                self.console.print(status_panel)
                
                # Get user input
                try:
                    self.console.print("\nPress arrow keys or WASD to navigate (or 'q' to quit, 'i' for info, 'h' for help):")
                    key = get_arrow_key()
                    
                    # Handle input
                    if key in ['u', 'd', 'l', 'r']:  # Arrow keys already converted
                        user_input = key
                    elif key.lower() in ['w', 'a', 's', 'd']:  # WASD keys
                        if key.lower() == 'w':  # W = up
                            user_input = 'u'
                        elif key.lower() == 's':  # S = down
                            user_input = 'd'
                        elif key.lower() == 'a':  # A = left
                            user_input = 'l'
                        elif key.lower() == 'd':  # D = right
                            user_input = 'r'
                    elif key.lower() in ['q', 'i', 'h']:
                        user_input = key.lower()
                    else:
                        user_input = ''
                except (EOFError, KeyboardInterrupt):
                    self.console.print("\n⚠️  Interactive mode requires terminal input. Exiting...")
                    break
                
                if user_input == 'q':
                    break
                elif user_input == 'l':
                    # Check if we can scroll to previous columns
                    if self.scroll_x > 0:
                        self.scroll_x -= 1
                        self.console.print("⬅️  Scrolled left")
                    else:
                        # At first columns, try previous page of data
                        if self.scroll_y >= self.page_size:
                            self.scroll_y -= self.page_size
                            # Set to last columns if there are more columns
                            if total_cols > self.cols_per_page:
                                self.scroll_x = max(0, total_cols - self.cols_per_page)
                            self.console.print("📄  Previous page of data")
                        else:
                            self.console.print("ℹ️  Already at the beginning of data")
                elif user_input == 'r':
                    # Check if we can scroll to more columns
                    if self.scroll_x + self.cols_per_page < total_cols:
                        self.scroll_x += 1
                        self.console.print("➡️  Scrolled right")
                    else:
                        # No more columns, try pagination (next page of data)
                        if self.scroll_y + self.page_size < total_rows:
                            self.scroll_y += self.page_size
                            self.scroll_x = 0  # Reset to first columns
                            self.console.print("📄  Next page of data")
                        else:
                            self.console.print("ℹ️  Already at the end of data")
                elif user_input == 'u':
                    # Check if we can scroll to previous rows
                    if self.scroll_y >= self.page_size:
                        self.scroll_y -= self.page_size
                        self.console.print("📄  Previous page of data")
                    elif self.scroll_y > 0:
                        self.scroll_y = 0
                        self.console.print("📄  First page of data")
                    else:
                        self.console.print("ℹ️  Already at the beginning of data")
                elif user_input == 'd':
                    # Check if we can go to next page
                    if self.scroll_y + self.page_size < total_rows:
                        self.scroll_y += self.page_size
                        self.console.print("📄  Next page of data")
                    else:
                        self.console.print("ℹ️  Already at the end of data")
                elif user_input == 'i':
                    self._show_column_info(display_cols)
                elif user_input == 'h':
                    self._show_help()
                else:
                    self.console.print(f"❓ Unknown command: '{user_input}'. Use h for help.")
                
        except KeyboardInterrupt:
            pass
        
        self.console.print("\n✅ Exited interactive table viewer")
    
    def _create_scrolled_table(self, results: List[tuple], columns: List[str]) -> Table:
        """Create table with current scroll position."""
        table = Table(
            show_header=True,
            header_style="bold blue",
            border_style="blue",
            show_lines=True,
            expand=True
        )
        
        # Add visible columns
        start_col = self.scroll_x
        end_col = min(start_col + self.cols_per_page, len(columns))
        
        for i in range(start_col, end_col):
            col_name = columns[i]
            
            # Get column info for formatting
            col_info = self.column_info.get(col_name, {})
            col_type = col_info.get('type', 'text')
            
            # Use clean column name without icons, truncate if too long
            header_text = col_name
            if len(header_text) > 20:
                header_text = header_text[:17] + "..."
            
            # Use consistent column width to prevent "heaping"
            table.add_column(
                header_text,
                overflow="fold",
                min_width=20,  # Consistent minimum width
                max_width=20,  # Consistent maximum width
                no_wrap=True  # Prevent header wrapping
            )
        
        # Add visible rows
        start_row = self.scroll_y
        end_row = min(start_row + self.page_size, len(results))
        
        for i in range(start_row, end_row):
            row = results[i]
            formatted_row = []
            
            for j in range(start_col, end_col):
                if j < len(row):
                    cell = row[j]
                    col_name = columns[j]
                    col_info = self.column_info.get(col_name, {})
                    col_type = col_info.get('type', 'text')
                    
                    # Format the cell value based on its type
                    cell_value = self.formatter.format_value(cell, col_type, max_length=25)
                else:
                    cell_value = "[dim]NULL[/dim]"
                formatted_row.append(cell_value)
            
            table.add_row(*formatted_row)
        
        return table
    
    def _create_table_display(self, results: List[tuple], columns: List[str]):
        """Create initial table display."""
        table = self._create_scrolled_table(results, columns)
        self.console.print(table)
    
    def _show_help(self):
        """Show help information."""
        help_text = """
🎮 Interactive Table Viewer Help

Navigation:
  ←/→     : Scroll horizontally (left/right) OR pagination
  ↑/↓     : Page navigation (previous/next page)
  WASD    : Alternative navigation (W=up, A=left, S=down, D=right)
  
Smart Pagination:
  →       : Next columns OR next page of data (when at last columns)
  ←       : Previous columns OR previous page of data (when at first columns)
  ↑       : Previous page of data
  ↓       : Next page of data
  
Actions:
  i       : Show column information and data types
  q       : Quit interactive mode
  h       : Show this help
  
Tips:
  - Use arrow keys or WASD to navigate large tables (no Enter needed!)
  - Data is color-coded by type for better readability
  - Use 'i' to see detailed column analysis with data types
  - ↑/↓ keys navigate by pages (10 rows at a time) for faster browsing
  - When you reach the end of columns, → will show next page of data
  - When you're at the first columns, ← will show previous page of data
        """
        
        help_panel = Panel(
            help_text,
            title="Help",
            border_style="yellow"
        )
        
        self.console.print(help_panel)
        self.console.input("Press Enter to continue...")
    
    def _show_column_info(self, columns: List[str]):
        """Show detailed information about columns."""
        info_text = "📊 Column Information:\n\n"
        
        for col in columns:
            col_info = self.column_info.get(col, {})
            col_type = col_info.get('type', 'unknown')
            null_count = col_info.get('null_count', 0)
            unique_count = col_info.get('unique_count', 0)
            total_count = col_info.get('total_count', 0)
            sample_values = col_info.get('sample_values', [])
            
            info_text += f"🔹 [bold]{col}[/bold]\n"
            info_text += f"   Type: {col_type}\n"
            info_text += f"   Null values: {null_count}/{total_count}\n"
            info_text += f"   Unique values: {unique_count}\n"
            
            if sample_values:
                sample_str = ", ".join(str(v)[:20] for v in sample_values[:3])
                info_text += f"   Sample: {sample_str}\n"
            
            info_text += "\n"
        
        info_panel = Panel(
            info_text,
            title="Column Analysis",
            border_style="blue"
        )
        
        self.console.print(info_panel)
        self.console.input("Press Enter to continue...")
