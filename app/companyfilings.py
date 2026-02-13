"""
Company Filing Documents Entry Point
====================================
Standalone entry point for the Company Filing Documents page.
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pages.company_filings import main
from core.database import init_database

if __name__ == "__main__":
    init_database()
    main()
