"""
SQL query processing and prefix application system.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of SQL queries."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CREATE = "CREATE"
    DROP = "DROP"
    ALTER = "ALTER"
    TRUNCATE = "TRUNCATE"
    MERGE = "MERGE"
    CALL = "CALL"
    SHOW = "SHOW"
    DESCRIBE = "DESCRIBE"
    EXPLAIN = "EXPLAIN"
    UNKNOWN = "UNKNOWN"


@dataclass
class TableReference:
    """Represents a table reference in SQL."""
    name: str
    alias: Optional[str] = None
    schema: Optional[str] = None
    database: Optional[str] = None
    is_qualified: bool = False
    should_prefix: bool = True
    uses_as_keyword: bool = False  # Track if "AS" keyword was used


@dataclass
class QueryInfo:
    """Information about a parsed SQL query."""
    query_type: QueryType
    tables: List[TableReference]
    original_query: str
    modified_query: str
    has_prefix_applied: bool = False


class SQLParser:
    """SQL parser for identifying table references and query types."""
    
    def __init__(self):
        # Regex patterns for different SQL constructs
        self.table_patterns = {
            'from': re.compile(r'\bFROM\s+([^\s,()]+(?:\s+(?:AS\s+)?[^\s,()]+)?)', re.IGNORECASE),
            'join': re.compile(r'\bJOIN\s+([^\s,()]+(?:\s+(?:AS\s+)?[^\s,()]+)?)', re.IGNORECASE),
            'update': re.compile(r'\bUPDATE\s+([^\s,()]+)', re.IGNORECASE),
            'insert_into': re.compile(r'\bINSERT\s+INTO\s+([^\s,()]+)', re.IGNORECASE),
            'delete_from': re.compile(r'\bDELETE\s+FROM\s+([^\s,()]+)', re.IGNORECASE),
            'truncate': re.compile(r'\bTRUNCATE\s+TABLE\s+([^\s,()]+)', re.IGNORECASE),
        }
        
        # Query type detection
        self.query_type_patterns = {
            QueryType.SELECT: re.compile(r'^\s*SELECT\b', re.IGNORECASE),
            QueryType.INSERT: re.compile(r'^\s*INSERT\b', re.IGNORECASE),
            QueryType.UPDATE: re.compile(r'^\s*UPDATE\b', re.IGNORECASE),
            QueryType.DELETE: re.compile(r'^\s*DELETE\b', re.IGNORECASE),
            QueryType.CREATE: re.compile(r'^\s*CREATE\b', re.IGNORECASE),
            QueryType.DROP: re.compile(r'^\s*DROP\b', re.IGNORECASE),
            QueryType.ALTER: re.compile(r'^\s*ALTER\b', re.IGNORECASE),
            QueryType.TRUNCATE: re.compile(r'^\s*TRUNCATE\b', re.IGNORECASE),
            QueryType.MERGE: re.compile(r'^\s*MERGE\b', re.IGNORECASE),
            QueryType.CALL: re.compile(r'^\s*CALL\b', re.IGNORECASE),
            QueryType.SHOW: re.compile(r'^\s*SHOW\b', re.IGNORECASE),
            QueryType.DESCRIBE: re.compile(r'^\s*DESCRIBE\b', re.IGNORECASE),
            QueryType.EXPLAIN: re.compile(r'^\s*EXPLAIN\b', re.IGNORECASE),
        }
    
    def parse_query(self, query: str) -> QueryInfo:
        """Parse SQL query and extract table references."""
        query = query.strip()
        
        # Detect query type
        query_type = self._detect_query_type(query)
        
        # Extract table references
        tables = self._extract_table_references(query)
        
        return QueryInfo(
            query_type=query_type,
            tables=tables,
            original_query=query,
            modified_query=query
        )
    
    def _detect_query_type(self, query: str) -> QueryType:
        """Detect the type of SQL query."""
        for query_type, pattern in self.query_type_patterns.items():
            if pattern.match(query):
                return query_type
        return QueryType.UNKNOWN
    
    def _extract_table_references(self, query: str) -> List[TableReference]:
        """Extract all table references from SQL query."""
        tables = []
        
        # Extract tables from different SQL constructs
        for construct, pattern in self.table_patterns.items():
            matches = pattern.findall(query)
            for match in matches:
                table_ref = self._parse_table_reference(match.strip())
                if table_ref and table_ref not in tables:
                    tables.append(table_ref)
        
        return tables
    
    def _parse_table_reference(self, table_str: str) -> Optional[TableReference]:
        """Parse a table reference string into TableReference object."""
        if not table_str or table_str.upper() in ['VALUES', 'DUAL']:
            return None
        
        # Handle aliases (both "AS alias" and "alias" formats)
        alias = None
        uses_as_keyword = False
        
        # Check for "AS alias" format
        if ' AS ' in table_str.upper():
            parts = re.split(r'\s+AS\s+', table_str, flags=re.IGNORECASE)
            if len(parts) == 2:
                table_str = parts[0].strip()
                alias = parts[1].strip()
                uses_as_keyword = True
        else:
            # Check for space-separated alias (e.g., "users u")
            # Split by space and check if last part looks like an alias
            words = table_str.strip().split()
            if len(words) >= 2:
                # Check if the last word is a potential alias (short, no dots, not SQL keywords)
                potential_alias = words[-1]
                sql_keywords = {'BY', 'ON', 'WHERE', 'HAVING', 'ORDER', 'GROUP', 'LIMIT', 'OFFSET'}
                if ('.' not in potential_alias and 
                    len(potential_alias) <= 10 and 
                    potential_alias.upper() not in sql_keywords):
                    # This might be an alias
                    table_str = ' '.join(words[:-1])
                    alias = potential_alias
        
        # Parse qualified names (database.schema.table)
        parts = table_str.split('.')
        
        if len(parts) == 3:
            # database.schema.table
            database, schema, table = parts
            return TableReference(
                name=table,
                schema=schema,
                database=database,
                alias=alias,
                is_qualified=True,
                should_prefix=False,  # Fully qualified names don't get prefixed
                uses_as_keyword=uses_as_keyword
            )
        elif len(parts) == 2:
            # schema.table
            schema, table = parts
            return TableReference(
                name=table,
                schema=schema,
                alias=alias,
                is_qualified=True,
                should_prefix=False,  # Schema-qualified names don't get prefixed
                uses_as_keyword=uses_as_keyword
            )
        else:
            # table
            return TableReference(
                name=table_str,
                alias=alias,
                should_prefix=True,
                uses_as_keyword=uses_as_keyword
            )


class PrefixProcessor:
    """Processes SQL queries to apply table prefixes."""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.parser = SQLParser()
    
    def process_query(self, query: str) -> QueryInfo:
        """Process query to apply table prefixes."""
        query_info = self.parser.parse_query(query)
        
        if not self.prefix or not query_info.tables:
            query_info.has_prefix_applied = False
            return query_info
        
        # Apply prefixes to tables that should be prefixed
        modified_query = query
        prefix_applied = False
        
        for table in query_info.tables:
            if table.should_prefix:
                old_ref = self._build_table_reference(table)
                new_ref = self._build_prefixed_table_reference(table)
                modified_query = self._replace_table_reference(modified_query, old_ref, new_ref)
                prefix_applied = True
        
        query_info.modified_query = modified_query
        query_info.has_prefix_applied = prefix_applied
        
        return query_info
    
    def _build_table_reference(self, table: TableReference) -> str:
        """Build table reference string from TableReference object."""
        if table.alias:
            if table.uses_as_keyword:
                return f"{table.name} AS {table.alias}"
            else:
                return f"{table.name} {table.alias}"
        return table.name
    
    def _build_prefixed_table_reference(self, table: TableReference) -> str:
        """Build prefixed table reference string."""
        prefixed_name = f"{self.prefix}{table.name}"
        if table.alias:
            if table.uses_as_keyword:
                return f"{prefixed_name} AS {table.alias}"
            else:
                return f"{prefixed_name} {table.alias}"
        return prefixed_name
    
    def _replace_table_reference(self, query: str, old_ref: str, new_ref: str) -> str:
        """Replace table reference in query with prefixed version."""
        # Use word boundaries to ensure we only replace complete table references
        pattern = r'\b' + re.escape(old_ref) + r'\b'
        return re.sub(pattern, new_ref, query, flags=re.IGNORECASE)


class QueryValidator:
    """Validates SQL queries based on security settings."""
    
    def __init__(self, allowed_all_query_types: bool = False):
        self.allowed_all_query_types = allowed_all_query_types
        self.parser = SQLParser()
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Validate query based on security settings."""
        query_info = self.parser.parse_query(query)
        
        # Allow SELECT queries always
        if query_info.query_type == QueryType.SELECT:
            return True, "Query allowed"
        
        # Allow other query types if configured
        if self.allowed_all_query_types:
            return True, "Query allowed"
        
        # Reject non-SELECT queries if not allowed
        return False, f"Query type '{query_info.query_type.value}' not allowed. Only SELECT queries are permitted."
    
    def get_allowed_query_types(self) -> List[str]:
        """Get list of allowed query types."""
        if self.allowed_all_query_types:
            return [qt.value for qt in QueryType if qt != QueryType.UNKNOWN]
        else:
            return [QueryType.SELECT.value]


class QueryProcessor:
    """Main query processing class that combines parsing, prefixing, and validation."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prefix_processor = PrefixProcessor(config.get('table_prefix', ''))
        self.validator = QueryValidator(
            config.get('security', {}).get('allowed_all_query_types', False)
        )
    
    def process_query(self, query: str) -> QueryInfo:
        """Process query with prefix application and validation."""
        # Apply prefix
        query_info = self.prefix_processor.process_query(query)
        
        # Validate query
        is_valid, message = self.validator.validate_query(query_info.modified_query)
        
        if not is_valid:
            raise ValueError(f"Query validation failed: {message}")
        
        return query_info
    
    def get_query_summary(self, query_info: QueryInfo) -> Dict[str, Any]:
        """Get summary of processed query."""
        return {
            'query_type': query_info.query_type.value,
            'tables_found': len(query_info.tables),
            'tables': [
                {
                    'name': t.name,
                    'alias': t.alias,
                    'schema': t.schema,
                    'database': t.database,
                    'is_qualified': t.is_qualified,
                    'should_prefix': t.should_prefix
                }
                for t in query_info.tables
            ],
            'has_prefix_applied': query_info.has_prefix_applied,
            'prefix_used': self.config.get('table_prefix', ''),
            'is_valid': True
        }