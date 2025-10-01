"""
Query History and Favorites management for Winter.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

@dataclass
class QueryHistory:
    """Represents a query history entry."""
    id: int
    query: str
    executed_at: str
    execution_time: float
    rows_returned: int
    columns_count: int
    success: bool
    error_message: Optional[str] = None
    user: str = "default"

@dataclass
class QueryFavorite:
    """Represents a favorite query."""
    id: int
    name: str
    query: str
    description: str
    created_at: str
    last_used: str
    use_count: int
    tags: List[str]
    user: str = "default"

class QueryHistoryManager:
    """Manages query history and favorites."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the history manager."""
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / '.snowflake'
        
        self.config_dir.mkdir(exist_ok=True)
        self.db_path = self.config_dir / 'winter_history.db'
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for history and favorites."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                executed_at TEXT NOT NULL,
                execution_time REAL NOT NULL,
                rows_returned INTEGER NOT NULL,
                columns_count INTEGER NOT NULL,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                user TEXT DEFAULT 'default'
            )
        ''')
        
        # Create favorites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                query TEXT NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                last_used TEXT NOT NULL,
                use_count INTEGER DEFAULT 0,
                tags TEXT,  -- JSON array of tags
                user TEXT DEFAULT 'default'
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_executed_at ON query_history(executed_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON query_history(user)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_name ON query_favorites(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_favorites_user ON query_favorites(user)')
        
        conn.commit()
        conn.close()
    
    def add_query_history(self, query: str, execution_time: float, 
                         rows_returned: int, columns_count: int, 
                         success: bool, error_message: Optional[str] = None,
                         user: str = "default") -> int:
        """Add a query to history."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        executed_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO query_history 
            (query, executed_at, execution_time, rows_returned, columns_count, success, error_message, user)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (query, executed_at, execution_time, rows_returned, columns_count, success, error_message, user))
        
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return history_id
    
    def get_query_history(self, limit: int = 50, user: str = "default") -> List[QueryHistory]:
        """Get query history."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, query, executed_at, execution_time, rows_returned, 
                   columns_count, success, error_message, user
            FROM query_history 
            WHERE user = ?
            ORDER BY executed_at DESC 
            LIMIT ?
        ''', (user, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [QueryHistory(*row) for row in rows]
    
    def search_query_history(self, search_term: str, user: str = "default") -> List[QueryHistory]:
        """Search query history by query content."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, query, executed_at, execution_time, rows_returned, 
                   columns_count, success, error_message, user
            FROM query_history 
            WHERE user = ? AND query LIKE ?
            ORDER BY executed_at DESC 
            LIMIT 100
        ''', (user, f'%{search_term}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [QueryHistory(*row) for row in rows]
    
    def add_favorite(self, name: str, query: str, description: str = "", 
                    tags: List[str] = None, user: str = "default") -> int:
        """Add a query to favorites."""
        if tags is None:
            tags = []
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        created_at = datetime.now().isoformat()
        last_used = created_at
        tags_json = json.dumps(tags)
        
        cursor.execute('''
            INSERT INTO query_favorites 
            (name, query, description, created_at, last_used, use_count, tags, user)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, query, description, created_at, last_used, 0, tags_json, user))
        
        favorite_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return favorite_id
    
    def get_favorites(self, user: str = "default") -> List[QueryFavorite]:
        """Get all favorites."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, query, description, created_at, last_used, use_count, tags, user
            FROM query_favorites 
            WHERE user = ?
            ORDER BY last_used DESC
        ''', (user,))
        
        rows = cursor.fetchall()
        conn.close()
        
        favorites = []
        for row in rows:
            tags = json.loads(row[7]) if row[7] else []
            favorites.append(QueryFavorite(
                id=row[0], name=row[1], query=row[2], description=row[3],
                created_at=row[4], last_used=row[5], use_count=row[6],
                tags=tags, user=row[8]
            ))
        
        return favorites
    
    def update_favorite_usage(self, favorite_id: int):
        """Update favorite usage count and last used time."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        last_used = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE query_favorites 
            SET use_count = use_count + 1, last_used = ?
            WHERE id = ?
        ''', (last_used, favorite_id))
        
        conn.commit()
        conn.close()
    
    def delete_favorite(self, favorite_id: int):
        """Delete a favorite query."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM query_favorites WHERE id = ?', (favorite_id,))
        
        conn.commit()
        conn.close()
    
    def search_favorites(self, search_term: str, user: str = "default") -> List[QueryFavorite]:
        """Search favorites by name, description, or tags."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, query, description, created_at, last_used, use_count, tags, user
            FROM query_favorites 
            WHERE user = ? AND (
                name LIKE ? OR 
                description LIKE ? OR 
                query LIKE ? OR
                tags LIKE ?
            )
            ORDER BY last_used DESC
        ''', (user, f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        rows = cursor.fetchall()
        conn.close()
        
        favorites = []
        for row in rows:
            tags = json.loads(row[7]) if row[7] else []
            favorites.append(QueryFavorite(
                id=row[0], name=row[1], query=row[2], description=row[3],
                created_at=row[4], last_used=row[5], use_count=row[6],
                tags=tags, user=row[8]
            ))
        
        return favorites

class HistoryUI:
    """UI components for history and favorites management."""
    
    def __init__(self, history_manager: QueryHistoryManager):
        self.history_manager = history_manager
    
    def show_query_history(self, limit: int = 20):
        """Display query history in a table."""
        history = self.history_manager.get_query_history(limit)
        
        if not history:
            console.print("📝 No query history found")
            return
        
        table = Table(title="Query History", show_header=True, header_style="bold blue")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Executed At", style="cyan", width=20)
        table.add_column("Query", style="white", width=50)
        table.add_column("Time", style="green", width=8)
        table.add_column("Rows", style="magenta", width=6)
        table.add_column("Status", style="bold", width=8)
        
        for entry in history:
            status = "✅ Success" if entry.success else "❌ Failed"
            query_preview = entry.query[:47] + "..." if len(entry.query) > 50 else entry.query
            
            table.add_row(
                str(entry.id),
                entry.executed_at[:19],  # Remove microseconds
                query_preview,
                f"{entry.execution_time:.2f}s",
                str(entry.rows_returned),
                status
            )
        
        console.print(table)
    
    def show_favorites(self):
        """Display favorites in a table."""
        favorites = self.history_manager.get_favorites()
        
        if not favorites:
            console.print("⭐ No favorite queries found")
            return
        
        table = Table(title="Favorite Queries", show_header=True, header_style="bold yellow")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Name", style="bold", width=20)
        table.add_column("Description", style="white", width=30)
        table.add_column("Query", style="cyan", width=40)
        table.add_column("Uses", style="green", width=6)
        table.add_column("Last Used", style="magenta", width=20)
        
        for favorite in favorites:
            query_preview = favorite.query[:37] + "..." if len(favorite.query) > 40 else favorite.query
            
            table.add_row(
                str(favorite.id),
                favorite.name,
                favorite.description[:27] + "..." if len(favorite.description) > 30 else favorite.description,
                query_preview,
                str(favorite.use_count),
                favorite.last_used[:19]
            )
        
        console.print(table)
    
    def interactive_favorite_manager(self):
        """Interactive favorite query manager."""
        while True:
            console.print("\n⭐ Favorite Query Manager")
            console.print("1. View favorites")
            console.print("2. Add favorite")
            console.print("3. Search favorites")
            console.print("4. Delete favorite")
            console.print("5. Back to main menu")
            
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5"])
            
            if choice == "1":
                self.show_favorites()
            elif choice == "2":
                self._add_favorite_interactive()
            elif choice == "3":
                self._search_favorites_interactive()
            elif choice == "4":
                self._delete_favorite_interactive()
            elif choice == "5":
                break
    
    def _add_favorite_interactive(self):
        """Interactive add favorite."""
        name = Prompt.ask("Enter favorite name")
        query = Prompt.ask("Enter SQL query")
        description = Prompt.ask("Enter description (optional)", default="")
        tags_input = Prompt.ask("Enter tags (comma-separated, optional)", default="")
        
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        try:
            favorite_id = self.history_manager.add_favorite(name, query, description, tags)
            console.print(f"✅ Added favorite '{name}' with ID {favorite_id}")
        except sqlite3.IntegrityError:
            console.print(f"❌ Error: Favorite name '{name}' already exists")
    
    def _search_favorites_interactive(self):
        """Interactive search favorites."""
        search_term = Prompt.ask("Enter search term")
        favorites = self.history_manager.search_favorites(search_term)
        
        if not favorites:
            console.print(f"🔍 No favorites found matching '{search_term}'")
            return
        
        console.print(f"\n🔍 Found {len(favorites)} favorites matching '{search_term}':")
        
        table = Table(show_header=True, header_style="bold green")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Name", style="bold", width=20)
        table.add_column("Description", style="white", width=30)
        table.add_column("Query", style="cyan", width=40)
        
        for favorite in favorites:
            query_preview = favorite.query[:37] + "..." if len(favorite.query) > 40 else favorite.query
            
            table.add_row(
                str(favorite.id),
                favorite.name,
                favorite.description[:27] + "..." if len(favorite.description) > 30 else favorite.description,
                query_preview
            )
        
        console.print(table)
    
    def _delete_favorite_interactive(self):
        """Interactive delete favorite."""
        self.show_favorites()
        
        try:
            favorite_id = int(Prompt.ask("Enter favorite ID to delete"))
            
            if Confirm.ask(f"Are you sure you want to delete favorite ID {favorite_id}?"):
                self.history_manager.delete_favorite(favorite_id)
                console.print(f"✅ Deleted favorite ID {favorite_id}")
            else:
                console.print("❌ Deletion cancelled")
        except ValueError:
            console.print("❌ Invalid favorite ID")
