"""
Utility functions untuk menangani versi Winter.
"""

import pkg_resources
import os
from pathlib import Path


def get_current_version():
    """
    Dapatkan versi saat ini dari package yang terinstall.
    Fallback ke pyproject.toml jika package belum terinstall.
    """
    try:
        # Coba dapatkan dari package yang terinstall
        return pkg_resources.get_distribution("winter").version
    except pkg_resources.DistributionNotFound:
        # Fallback ke pyproject.toml
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # Python < 3.11
            except ImportError:
                # Jika tidak ada tomli, gunakan versi hardcoded
                return "0.1.0"
        
        # Cari pyproject.toml dari direktori saat ini
        current_dir = Path(__file__).parent.parent.parent
        pyproject_path = current_dir / "pyproject.toml"
        
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                return data.get("project", {}).get("version", "0.1.0")
        
        # Fallback terakhir
        return "0.1.0"


def get_package_info():
    """
    Dapatkan informasi package Winter.
    """
    try:
        dist = pkg_resources.get_distribution("winter")
        return {
            "name": dist.project_name,
            "version": dist.version,
            "location": dist.location,
            "requires": [str(req) for req in dist.requires()],
            "installed": True
        }
    except pkg_resources.DistributionNotFound:
        return {
            "name": "winter",
            "version": get_current_version(),
            "location": None,
            "requires": [],
            "installed": False
        }
