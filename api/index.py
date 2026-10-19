"""
api/index.py
============
Entry point for Vercel Serverless Functions.
Exposes the Flask WSGI application instance `app`.
"""

import os
import sys

# Ensure the project root directory is on sys.path so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
