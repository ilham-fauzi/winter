"""
Header formatting utilities for Winter table display.
"""

from rich.text import Text
from rich.console import Console
from typing import List, Tuple


class HeaderFormatter:
    """Format table headers with dynamic font scaling for long column names."""
    
    def __init__(self):
        self.console = Console()
        self.max_header_width = 20  # Maximum width for header before scaling
        self.min_font_size = 0.7   # Minimum font size (70% of normal)
        self.max_font_size = 1.0   # Maximum font size (100% of normal)
    
    def format_header(self, header_text: str, max_width: int = 20) -> str:
        """
        Format header text with dynamic font scaling to fit full text.
        
        Args:
            header_text: The original header text
            max_width: Maximum width for the header
            
        Returns:
            Formatted header text with appropriate font scaling
        """
        if len(header_text) <= max_width:
            # Header fits, use normal font
            return f"[bold blue]{header_text}[/bold blue]"
        
        # Calculate font scale based on length to fit full text
        scale_factor = self._calculate_font_scale(header_text, max_width)
        
        # Use smaller font to fit full text
        if scale_factor < 1.0:
            # Calculate how much we need to scale down
            if scale_factor >= 0.8:
                # Slightly smaller font
                return f"[bold blue]{header_text}[/bold blue]"
            elif scale_factor >= 0.6:
                # Medium smaller font
                return f"[blue]{header_text}[/blue]"
            else:
                # Very small font
                return f"[dim blue]{header_text}[/dim blue]"
        else:
            # Use normal font
            return f"[bold blue]{header_text}[/bold blue]"
    
    def _calculate_font_scale(self, text: str, max_width: int) -> float:
        """
        Calculate appropriate font scale factor.
        
        Args:
            text: The text to scale
            max_width: Maximum allowed width
            
        Returns:
            Scale factor between min_font_size and max_font_size
        """
        if len(text) <= max_width:
            return self.max_font_size
        
        # Calculate scale based on how much we need to compress
        compression_ratio = max_width / len(text)
        
        # Ensure scale is within bounds
        scale = max(self.min_font_size, min(self.max_font_size, compression_ratio))
        
        return scale
    
    def format_headers_with_scaling(self, headers: List[str], max_width: int = 20) -> List[str]:
        """
        Format multiple headers with consistent scaling.
        
        Args:
            headers: List of header texts
            max_width: Maximum width for each header
            
        Returns:
            List of formatted header texts
        """
        formatted_headers = []
        
        for header in headers:
            formatted_header = self.format_header(header, max_width)
            formatted_headers.append(formatted_header)
        
        return formatted_headers
    
    def get_header_display_info(self, header_text: str, max_width: int = 20) -> dict:
        """
        Get information about how a header will be displayed.
        
        Args:
            header_text: The header text
            max_width: Maximum width for the header
            
        Returns:
            Dictionary with display information
        """
        scale_factor = self._calculate_font_scale(header_text, max_width)
        
        return {
            'original_text': header_text,
            'display_text': header_text if len(header_text) <= max_width else header_text[:max_width-3] + "...",
            'scale_factor': scale_factor,
            'is_scaled': scale_factor < 1.0,
            'is_truncated': len(header_text) > max_width,
            'original_length': len(header_text),
            'display_length': min(len(header_text), max_width)
        }


class SmartHeaderFormatter(HeaderFormatter):
    """Advanced header formatter with smart scaling and tooltips."""
    
    def __init__(self):
        super().__init__()
        self.tooltip_enabled = True
    
    def format_header_with_tooltip(self, header_text: str, max_width: int = 20) -> str:
        """
        Format header with full text display using font scaling.
        
        Args:
            header_text: The original header text
            max_width: Maximum width for the header
            
        Returns:
            Formatted header text with full text display
        """
        if len(header_text) <= max_width:
            return f"[bold blue]{header_text}[/bold blue]"
        
        # Calculate font scale based on length to fit full text
        scale_factor = self._calculate_font_scale(header_text, max_width)
        
        # Use font scaling to fit full text
        if scale_factor >= 0.8:
            # Slightly smaller font
            return f"[bold blue]{header_text}[/bold blue]"
        elif scale_factor >= 0.6:
            # Medium smaller font
            return f"[blue]{header_text}[/blue]"
        else:
            # Very small font
            return f"[dim blue]{header_text}[/dim blue]"
    
    def format_headers_smart(self, headers: List[str], max_width: int = 20) -> List[Tuple[str, str]]:
        """
        Format headers with smart scaling to display full text.
        
        Args:
            headers: List of header texts
            max_width: Maximum width for each header
            
        Returns:
            List of tuples (display_text, full_text) - both are the same now
        """
        formatted_headers = []
        
        for header in headers:
            if len(header) <= max_width:
                display_text = f"[bold blue]{header}[/bold blue]"
                full_text = header
            else:
                # Calculate font scale to fit full text
                scale_factor = self._calculate_font_scale(header, max_width)
                
                # Use font scaling to fit full text
                if scale_factor >= 0.8:
                    # Slightly smaller font
                    display_text = f"[bold blue]{header}[/bold blue]"
                elif scale_factor >= 0.6:
                    # Medium smaller font
                    display_text = f"[blue]{header}[/blue]"
                else:
                    # Very small font
                    display_text = f"[dim blue]{header}[/dim blue]"
                
                full_text = header
            
            formatted_headers.append((display_text, full_text))
        
        return formatted_headers


def create_header_formatter() -> HeaderFormatter:
    """Create a header formatter instance."""
    return HeaderFormatter()


def create_smart_header_formatter() -> SmartHeaderFormatter:
    """Create a smart header formatter instance."""
    return SmartHeaderFormatter()
