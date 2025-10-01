"""
CLI commands for Winter.
"""

import click
from rich.console import Console

console = Console()


@click.group()
def cli():
    """Winter CLI commands."""
    pass


@cli.command()
def version():
    """Show Winter version."""
    console.print("Winter v0.1.0")


@cli.command()
def info():
    """Show Winter information."""
    console.print("❄️  Winter - Snowflake Terminal Client")
    console.print("Version: 0.1.0")
    console.print("Description: Advanced terminal client for Snowflake")
