"""
Earnings Calls Entry Point
==========================
Standalone Streamlit page for viewing earnings call transcripts.
URL: /earningscalls

Figma Reference: https://www.figma.com/design/CiMfOW2lULkY8p613AuNkX/Marketing---Research-Website?node-id=20663-225723

Usage:
    cd app && streamlit run earningscalls.py

Or with specific port:
    cd app && streamlit run earningscalls.py --server.port 8504
"""
import streamlit as st

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="Earnings Calls - Coresight Research",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import after page config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Run the main page - all logic is in pages/earnings_calls.py
from pages.earnings_calls import main

if __name__ == "__main__":
    main()
