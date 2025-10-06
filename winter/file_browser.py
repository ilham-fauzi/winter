"""
File browser utility for Winter setup.
"""

import os
import shutil
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

console = Console()

# Supported RSA key file extensions
RSA_KEY_EXTENSIONS = {
    '.p8',      # PKCS#8 format (Snowflake standard)
    '.pem',     # Privacy Enhanced Mail format
    '.key',     # Generic private key format
    '.rsa',     # RSA specific format
    '.pkcs8',   # PKCS#8 format (alternative extension)
    '.der',     # Distinguished Encoding Rules (binary)
    '.crt',     # Certificate format (bisa berisi private key)
    '.cer',     # Certificate format (alternative)
    '.p12',     # PKCS#12 format (bisa berisi private key)
    '.pfx',     # Personal Information Exchange format
}


class FileBrowser:
    """Simple file browser for selecting private key files."""
    
    def __init__(self, start_path: str = None):
        self.current_path = Path(start_path or os.path.expanduser("~"))
        self.selected_file = None
    
    def browse_for_rsa_key_file(self) -> str:
        """Browse for RSA private key file (all supported extensions)."""
        console.print("\n🔍 File Browser - Select RSA Private Key File")
        console.print("📁 Use arrow keys to navigate, Enter to select, 'q' to quit")
        console.print("🔍 Type 'search' to search for RSA key files in directories")
        console.print(f"📄 Supported extensions: {', '.join(sorted(RSA_KEY_EXTENSIONS))}")
        
        while True:
            self._display_directory()
            
            # Get user input
            choice = console.input("\n[bold blue]Enter choice (number, 'u' for up, 'search' for search, 'q' to quit):[/bold blue] ")
            
            if choice.lower() == 'q':
                return None
            
            if choice.lower() == 'u':
                self._go_up()
                continue
            
            if choice.lower() == 'search':
                search_result = self._search_for_rsa_key_files()
                if search_result:
                    return search_result
                continue
            
            try:
                choice_num = int(choice)
                if self._handle_choice(choice_num):
                    return str(self.selected_file)
            except ValueError:
                console.print("❌ Invalid choice. Please enter a number, 'u', 'search', or 'q'")
    
    def _display_directory(self):
        """Display current directory contents."""
        console.print(f"\n📁 Current Directory: {self.current_path}")
        
        # Get directory contents
        try:
            items = []
            for item in self.current_path.iterdir():
                if item.is_file() and item.suffix.lower() in RSA_KEY_EXTENSIONS:
                    items.append(('file', item))
                elif item.is_dir() and not item.name.startswith('.'):
                    items.append(('dir', item))
            
            if not items:
                console.print(f"📭 No RSA key files ({', '.join(sorted(RSA_KEY_EXTENSIONS))}) or directories found")
                return
            
            # Create table
            table = Table(show_header=True, header_style="bold green")
            table.add_column("#", style="dim", width=4)
            table.add_column("Type", style="cyan", width=6)
            table.add_column("Name", style="white", width=50)
            table.add_column("Size", style="magenta", width=12)
            
            for i, (item_type, item) in enumerate(items, 1):
                if item_type == 'file':
                    size = self._format_size(item.stat().st_size)
                    table.add_row(str(i), "📄", item.name, size)
                else:
                    table.add_row(str(i), "📁", item.name, "-")
            
            console.print(table)
            
        except PermissionError:
            console.print("❌ Permission denied to access this directory")
        except Exception as e:
            console.print(f"❌ Error reading directory: {e}")
    
    def _handle_choice(self, choice_num: int) -> bool:
        """Handle user choice."""
        try:
            items = []
            for item in self.current_path.iterdir():
                if item.is_file() and item.suffix.lower() in RSA_KEY_EXTENSIONS:
                    items.append(('file', item))
                elif item.is_dir() and not item.name.startswith('.'):
                    items.append(('dir', item))
            
            if 1 <= choice_num <= len(items):
                item_type, item = items[choice_num - 1]
                
                if item_type == 'file':
                    # File selected
                    self.selected_file = item
                    console.print(f"✅ Selected file: {item.name}")
                    
                    # Show file info
                    self._show_file_info(item)
                    
                    # Confirm selection
                    if Confirm.ask("Use this file?", default=True):
                        return True
                    else:
                        self.selected_file = None
                        return False
                else:
                    # Directory selected, navigate into it
                    self.current_path = item
                    return False
            else:
                console.print("❌ Invalid choice number")
                return False
                
        except Exception as e:
            console.print(f"❌ Error handling choice: {e}")
            return False
    
    def _go_up(self):
        """Go up one directory level."""
        if self.current_path.parent != self.current_path:
            self.current_path = self.current_path.parent
        else:
            console.print("⚠️  Already at root directory")
    
    def _show_file_info(self, file_path: Path):
        """Show file information."""
        try:
            stat = file_path.stat()
            console.print(Panel.fit(
                f"File: {file_path.name}\n"
                f"Path: {file_path}\n"
                f"Size: {self._format_size(stat.st_size)}\n"
                f"Modified: {stat.st_mtime}",
                title="File Information",
                border_style="blue"
            ))
        except Exception as e:
            console.print(f"⚠️  Could not read file info: {e}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _search_for_rsa_key_files(self) -> str:
        """Search for RSA key files in directories."""
        console.print("\n🔍 Search for RSA Key Files")
        console.print("1. Search in Downloads directory")
        console.print("2. Search in Desktop directory")
        console.print("3. Search in Documents directory")
        console.print("4. Search in home directory")
        console.print("5. Search in custom directory")
        console.print("6. Cancel search")
        
        search_choice = console.input("\n[bold blue]Choose search option (1-6):[/bold blue] ")
        
        search_paths = {
            '1': Path.home() / "Downloads",
            '2': Path.home() / "Desktop", 
            '3': Path.home() / "Documents",
            '4': Path.home(),
            '5': None  # Custom path
        }
        
        if search_choice == '6':
            return None
        
        if search_choice == '5':
            # Custom directory
            custom_path = console.input("Enter directory path: ").strip()
            if not custom_path:
                console.print("❌ No path provided")
                return None
            search_path = Path(custom_path)
        else:
            search_path = search_paths.get(search_choice)
        
        if not search_path or not search_path.exists():
            console.print(f"❌ Directory not found: {search_path}")
            return None
        
        console.print(f"🔍 Searching for RSA key files in: {search_path}")
        console.print(f"📄 Looking for extensions: {', '.join(sorted(RSA_KEY_EXTENSIONS))}")
        console.print("⏳ Please wait...")
        
        # Search for RSA key files recursively
        rsa_key_files = []
        try:
            for ext in RSA_KEY_EXTENSIONS:
                for file_path in search_path.rglob(f"*{ext}"):
                    if file_path.is_file():
                        rsa_key_files.append(file_path)
        except PermissionError:
            console.print("❌ Permission denied to search this directory")
            return None
        except Exception as e:
            console.print(f"❌ Error searching: {e}")
            return None
        
        if not rsa_key_files:
            console.print(f"📭 No RSA key files ({', '.join(sorted(RSA_KEY_EXTENSIONS))}) found in this directory")
            return None
        
        # Display found files
        console.print(f"\n✅ Found {len(rsa_key_files)} RSA key files:")
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("#", style="dim", width=4)
        table.add_column("File Name", style="white", width=30)
        table.add_column("Directory", style="cyan", width=50)
        table.add_column("Size", style="magenta", width=12)
        
        for i, file_path in enumerate(rsa_key_files, 1):
            try:
                size = self._format_size(file_path.stat().st_size)
                table.add_row(
                    str(i),
                    file_path.name,
                    str(file_path.parent),
                    size
                )
            except Exception:
                table.add_row(str(i), file_path.name, str(file_path.parent), "Unknown")
        
        console.print(table)
        
        # Let user select a file
        while True:
            choice = console.input(f"\n[bold blue]Select file (1-{len(rsa_key_files)}, 'c' to cancel):[/bold blue] ")
            
            if choice.lower() == 'c':
                return None
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(rsa_key_files):
                    selected_file = rsa_key_files[choice_num - 1]
                    console.print(f"✅ Selected file: {selected_file.name}")
                    
                    # Show file info
                    self._show_file_info(selected_file)
                    
                    # Confirm selection
                    if Confirm.ask("Use this file?", default=True):
                        return str(selected_file)
                    else:
                        continue
                else:
                    console.print("❌ Invalid choice number")
            except ValueError:
                console.print("❌ Invalid input")


def browse_and_copy_rsa_key_file(config_dir: Path) -> str:
    """Browse for RSA key file and copy it to config directory."""
    browser = FileBrowser()
    
    # Start from Downloads directory if it exists
    downloads_path = Path.home() / "Downloads"
    if downloads_path.exists():
        browser.current_path = downloads_path
    
    selected_file = browser.browse_for_rsa_key_file()
    
    if not selected_file:
        console.print("❌ No file selected")
        return None
    
    source_file = Path(selected_file)
    
    # Copy file to config directory
    try:
        # Use consistent filename with original extension
        target_file = config_dir / f"rsa_key{source_file.suffix}"
        
        # Ensure config directory exists
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_file, target_file)
        
        # Set secure permissions
        os.chmod(target_file, 0o600)
        
        console.print(f"✅ File copied to: {target_file}")
        console.print(f"📄 Original extension preserved: {source_file.suffix}")
        return str(target_file)
        
    except Exception as e:
        console.print(f"❌ Failed to copy file: {e}")
        return None


# Backward compatibility
def browse_and_copy_p8_file(config_dir: Path) -> str:
    """Browse for RSA key file and copy it to config directory (backward compatibility)."""
    return browse_and_copy_rsa_key_file(config_dir)
