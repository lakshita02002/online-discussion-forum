import sys
import os

# Make the project root importable so `from app import create_app` resolves correctly.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app("production")

