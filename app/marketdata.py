"""
Market Data Page Entry Point
============================
Standalone Streamlit page for market data with Coresight header/footer.
URL: /marketdata

ADJUSTABLE LAYOUT:
- Body padding: set_page_layout(body_padding="0 20px")  # "top_bottom left_right"
- Max content width: set_page_layout(max_content_width="1350px")
- See components/styles.py for all options
"""
import streamlit as st

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="Coresight Market Data",
    page_icon="📊",
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
from utils.local_storage import init_local_storage, local_storage
from core.database import init_database

# Import page content
from pages.market_data import render_page as render_market_data_content


def initialize_app():
    """Initialize application state and dependencies."""
    init_local_storage()
    init_database()


def main():
    """Market Data page entry point."""
    # Initialize
    initialize_app()
    
    # Handle query parameters for tab切换 - sync to local_storage but DON'T delete query param
    # This avoids the "Page not found" error from Streamlit's query param handling
    query_params = st.query_params
    if "tab" in query_params:
        tab = query_params["tab"]
        if tab in ["income_statement", "balance_sheet", "cash_flow", "key_stats", "company_profile"]:
            from utils.local_storage import set_marketdata_tab
            set_marketdata_tab(tab)
    
    # Render global styles
    render_styles()
    
    # ADJUSTABLE LAYOUT - Modify these parameters as needed
    # LOCATION: This call is in app/marketdata.py
    set_page_layout(
        header_full_width=True,      # Header takes full width
        footer_full_width=True,      # Footer takes full width
        body_padding="0 20px",       # "top_bottom left_right" - ADJUST THIS FOR BODY PADDING
        max_content_width="1350px",  # Max content width - ADJUST THIS
        remove_top_padding=True,     # Remove top padding
        footer_at_bottom=True        # Footer sticks to bottom
    )
    
    # Hide default Streamlit elements
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Render Header (shared component from components/navigation.py)
    # This renders: Logo, Market Data (active), Newsroom (link), Contact Us button
    render_header(full_width=True)
    
    # Render Market Data page content
    render_market_data_content()
    
    # Render Footer (shared component from components/navigation.py)
    render_coresight_footer(full_width=True, stick_to_bottom=True)


if __name__ == "__main__":
    main()
