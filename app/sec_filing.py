"""
SEC Filing Documents Page Entry Point
=====================================
Standalone Streamlit page for company filing documents.
URL: /sec_filing
"""
import streamlit as st

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="Company Filing Documents - Coresight Research",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import after page config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# IMMEDIATELY hide sidebar to prevent skeleton flash
from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

from components.navigation import render_header, render_coresight_footer
from components.styles import render_styles
from utils.local_storage import init_local_storage
from core.database import init_database

# Import page content
from pages.sec_filing import main as render_sec_filing_content


def initialize_app():
    """Initialize application state and dependencies."""
    init_local_storage()
    init_database()


def main():
    """SEC Filing page entry point."""
    # Initialize
    initialize_app()
    
    # Render global styles
    render_styles()
    
    # Set layout
    set_page_layout(
        header_full_width=True,
        footer_full_width=True,
        body_padding="0 20px",
        max_content_width="1350px",
        remove_top_padding=True,
        footer_at_bottom=True
    )
    
    # Hide default Streamlit elements
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Render Header
    render_header(full_width=True)
    
    # Render SEC Filing page content
    render_sec_filing_content()
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


if __name__ == "__main__":
    main()
