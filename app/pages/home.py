"""
Homepage - Coresight Research
"""
import streamlit as st

st.set_page_config(
    page_title="Coresight Market Data - Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from components.styles import hide_sidebar, render_styles
from components.navigation import render_header, render_coresight_footer

hide_sidebar()

COMPANIES = [("M", "Macy's"), ("ANF", "Abercrombie & Fitch"), ("JWN", "Nordstrom"), ("KSS", "Kohl's")]
SECTORS = ["Apparel & Footwear", "Department Stores", "Discount Stores", "Luxury Goods"]

def card_html(title, dropdown_id, current_value, button_link="/marketdata"):
    """Generate HTML for a selection card"""
    return (
        '<div style="background-color: #EBEBEB; border-radius: 8px; padding: 8px 16px; width: 357px; margin: 0 auto; box-sizing: border-box;">'
        '<p style="font-family: Roboto, sans-serif; font-weight: 600; font-size: 18px; color: #2D2A29; text-align: center; margin: 0 0 8px 0;">'
        + title +
        '</p>'
        '<div style="margin-bottom: 11px; position: relative;">'
        '<div id="' + dropdown_id + '" style="background-color: #FFFFFF; border-radius: 8px; height: 40px; padding: 8px 10px; display: flex; align-items: center; justify-content: space-between; font-family: Roboto, sans-serif; font-weight: 400; font-size: 14px; color: #000000; box-sizing: border-box; cursor: pointer; border: 1px solid transparent;" onmouseover="this.style.borderColor=\'#D62E2F\'" onmouseout="this.style.borderColor=\'transparent\'">'
        '<span>' + current_value + '</span>'
        '<svg width="12" height="6" viewBox="0 0 12 6"><path d="M1 1L6 5L11 1" stroke="#666" stroke-width="1.5" fill="none"/></svg>'
        '</div>'
        '</div>'
        '<a href="' + button_link + '" style="background-color: #D62E2F; color: white; font-family: Montserrat, sans-serif; font-weight: 700; font-size: 16px; border-radius: 8px; padding: 8px 16px; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 8px; width: 100%; height: 41px; box-sizing: border-box;">'
        'View '
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M10 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-4"/><path d="M14 4h6v6"/><path d="M21 3 12 12"/></svg>'
        '</a>'
        '</div>'
    )

def main():
    if 'home_company' not in st.session_state:
        st.session_state.home_company = COMPANIES[0][0]
    if 'home_sector' not in st.session_state:
        st.session_state.home_sector = SECTORS[0]
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap');
    .block-container { padding: 0 !important; max-width: 100% !important; }
    .appview-container .main .block-container { padding-top: 0 !important; }
    [data-testid="stSidebar"] { display: none !important; }
    .main-title { font-family: 'Montserrat', sans-serif !important; font-weight: 700 !important; font-size: 39px !important; color: #D62E2F !important; text-align: center !important; letter-spacing: -0.5px !important; margin: 96px 0 32px 0 !important; }
    div[data-testid="stSelectbox"] { display: none !important; }
    .stSelectbox { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    render_styles()
    render_header(full_width=True)
    
    # Main title
    st.markdown('<h1 class="main-title">CORESIGHT MARKET DATA</h1>', unsafe_allow_html=True)
    
    # Two cards side by side
    col_spacer1, col1, col2, col_spacer2 = st.columns([1, 2, 2, 1])
    
    # Card 1: View by Company
    with col1:
        current_company = next((c[1] for c in COMPANIES if c[0] == st.session_state.home_company), COMPANIES[0][1])
        st.markdown(card_html("View by Company", "company-dropdown", current_company), unsafe_allow_html=True)
        
        # Hidden streamlit selectbox
        company = st.selectbox("Company", options=[c[0] for c in COMPANIES],
            format_func=lambda x: next((c[1] for c in COMPANIES if c[0] == x), x),
            index=[c[0] for c in COMPANIES].index(st.session_state.home_company),
            key="company_select", label_visibility="collapsed")
        st.session_state.home_company = company
    
    # Card 2: View by Sector
    with col2:
        current_sector = st.session_state.home_sector
        st.markdown(card_html("View by Sector", "sector-dropdown", current_sector), unsafe_allow_html=True)
        
        # Hidden streamlit selectbox
        sector = st.selectbox("Sector", options=SECTORS,
            index=SECTORS.index(st.session_state.home_sector) if st.session_state.home_sector in SECTORS else 0,
            key="sector_select", label_visibility="collapsed")
        st.session_state.home_sector = sector
    
    # JavaScript to make custom dropdowns trigger Streamlit selectboxes
    st.markdown("""
    <script>
    (function() {
        // Find and click the hidden Streamlit selectbox when custom dropdown is clicked
        var companyDropdown = document.getElementById('company-dropdown');
        var sectorDropdown = document.getElementById('sector-dropdown');
        
        if (companyDropdown) {
            companyDropdown.addEventListener('click', function() {
                var selectbox = document.querySelector('[data-testid="stSelectbox"]');
                if (selectbox) {
                    var input = selectbox.querySelector('input');
                    if (input) input.click();
                }
            });
        }
        
        if (sectorDropdown) {
            sectorDropdown.addEventListener('click', function() {
                var selectboxes = document.querySelectorAll('[data-testid="stSelectbox"]');
                if (selectboxes.length > 1) {
                    var input = selectboxes[1].querySelector('input');
                    if (input) input.click();
                }
            });
        }
    })();
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    render_coresight_footer(full_width=True, stick_to_bottom=True)

if __name__ == "__main__":
    main()
