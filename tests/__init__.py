"""
Tests for Winter package.
"""

import pytest
from winter.main import main
from winter.query import QueryProcessor
from winter.security import SecurityManager


def test_main_import():
    """Test that main module can be imported."""
    assert main is not None


def test_query_processor():
    """Test QueryProcessor basic functionality."""
    config = {'table_prefix': 'test_'}
    processor = QueryProcessor(config)
    
    assert processor.table_prefix == 'test_'
    assert processor.detect_query_type('SELECT * FROM users') == 'SELECT'
    assert processor.detect_query_type('INSERT INTO users VALUES (1)') == 'INSERT'


def test_security_manager():
    """Test SecurityManager basic functionality."""
    config = {
        'security': {
            'allowed_all_query_types': False
        }
    }
    security = SecurityManager(config)
    
    assert security.allowed_all_types == False
    assert security.get_security_status() == "SELECT-only (allowed_all_query_types: false)"
