"""
Delhi Land Records MVP API
FastAPI application for property search and comparison
"""

from .main import app
from .models import *
from .database import get_database

__version__ = "1.0.0"
