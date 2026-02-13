"""
Company Profile Page - Coresight Research
=========================================
Company overview page with profile information.
"""
import streamlit as st
from typing import Optional

# MUST be first Streamlit command
st.set_page_config(
    page_title="Company Profile - Coresight Research",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed",
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Hide sidebar immediately
from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

from components.styles import render_styles, COLORS, TYPOGRAPHY, SPACING
from components.navigation import render_header, render_coresight_footer
from data.models import CompanyOverview
from data.repository import CompanyOverviewRepository, CompanyRepository
from core.database import init_database


def get_company_css() -> str:
    """Get custom CSS for company profile page - matches Figma exactly."""
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&family=Montserrat:wght@400;500;600;700&display=swap');
    
    /* Page Container */
    .company-profile-container {
        max-width: 1238px;
        margin: 0 auto;
        padding: 24px 0;
        font-family: 'Roboto', sans-serif;
    }
    
    /* Company Header Section - matches Figma Frame 1321316478 */
    .company-header-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 24px;
        padding: 24px 0;
    }
    
    /* Left side - Title and Company Name */
    .company-header-left {
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    /* Section Title - "CORESIGHT MARKET DATA" - Montserrat 20px weight 700 #d62e2f */
    .section-title {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 20px;
        color: #d62e2f;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 0;
        padding: 0;
    }
    
    /* Company Name with Dropdown - Montserrat 20px weight 700 #2d2a29 */
    .company-name-dropdown {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 20px;
        color: #2d2a29;
        display: flex;
        align-items: center;
        gap: 4px;
        cursor: pointer;
    }
    
    /* Dropdown arrow icon */
    .dropdown-arrow {
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .dropdown-arrow svg {
        width: 16px;
        height: 16px;
        stroke: #2d2a29;
    }
    
    /* Company Documents Button - matches Figma exactly */
    .company-documents-btn {
        background-color: #d62e2f;
        color: #ffffff;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 14px;
        padding: 12px 16px;
        border-radius: 4px;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: background-color 0.2s ease;
        height: 44px;
    }
    
    .company-documents-btn:hover {
        background-color: #b52627;
    }
    
    /* External link icon */
    .company-documents-btn svg {
        width: 20px;
        height: 20px;
    }
    
    /* Streamlit Selectbox Styling - Make it look like the Figma dropdown */
    div[data-testid="stSelectbox"] {
        margin-top: -85px !important;
        margin-bottom: 20px !important;
        width: 600px !important;
    }
    
    div[data-testid="stSelectbox"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stSelectbox"] label {
        display: none !important;
    }
    
    /* Hide the actual selectbox but keep it clickable */
    div[data-testid="stSelectbox"] > div > div {
        opacity: 0;
        height: 30px;
        cursor: pointer;
    }
    
    /* Tab Navigation */
    .tab-navigation {
        display: flex;
        border-bottom: 1px solid #CBCACA;
        margin-bottom: 24px;
        gap: 80px;
    }
    
    .tab-item {
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 16px;
        padding: 12px 0;
        cursor: pointer;
        color: #323232;
        border-bottom: 3px solid transparent;
        margin-bottom: -2px;
        transition: all 0.2s ease;
    }
    
    .tab-item:hover {
        color: #d62e2f;
    }
    
    .tab-item.active {
        color: #d62e2f;
        border-bottom-color: #d62e2f;
    }
    
    /* Info Table Container */
    .info-table-container {
        border: 1px solid #CBCACA;
        border-radius: 8px;
        overflow: hidden;
        background: #FFFFFF;
        margin-bottom: 32px;
    }
    
    .info-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .info-table-row {
        display: flex;
        border-bottom: 1px solid #CBCACA;
    }
    
    .info-table-row:last-child {
        border-bottom: none;
    }
    
    /* Left column (labels) - Website:, Number of Employees, etc */
    .info-label {
        width: 22%;
        padding: 14px 20px;
        background: #F8F9FA;
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 14px;
        color: #323232;
        border-right: 1px solid #CBCACA;
        display: flex;
        align-items: center;
    }
    
    /* Middle column (values) - macys.com, 1,556,999, etc */
    .info-value {
        width: 28%;
        padding: 14px 20px;
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 14px;
        color: #323232;
        border-right: 1px solid #CBCACA;
        display: flex;
        align-items: center;
    }
    
    /* Right column labels (Coverage Summary:, Coverage List:, etc) */
    .info-label-right {
        width: 22%;
        padding: 14px 20px;
        background: #F8F9FA;
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        font-size: 14px;
        color: #323232;
        border-right: 1px solid #CBCACA;
        display: flex;
        align-items: center;
    }
    
    /* Right column values - No, No, No, etc */
    .info-value-right {
        width: 28%;
        padding: 14px 20px;
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 14px;
        color: #323232;
        display: flex;
        align-items: center;
    }
    
    /* Business Description Section */
    .business-description-section {
        margin-top: 32px;
    }
    
    .section-header {
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        font-size: 18px;
        color: #323232;
        margin-bottom: 16px;
        padding-bottom: 8px;
        border-bottom: 1px solid #CBCACA;
    }
    
    .business-description-text {
        font-family: 'Roboto', sans-serif;
        font-weight: 400;
        font-size: 15px;
        line-height: 1.6;
        color: #4F4F4F;
    }
    
    /* Link styling */
    .website-link {
        color: #0066CC;
        text-decoration: none;
    }
    
    .website-link:hover {
        text-decoration: underline;
    }
    
    /* No data available styling */
    .no-data {
        color: #888888;
        font-style: italic;
    }
    </style>
    """


def render_info_table(company: CompanyOverview) -> str:
    """Render the company info table matching Figma wireframe exactly."""
    
    # Website value with link
    website_html = f'<a href="{company.official_site}" target="_blank" class="website-link">{company.website_display}</a>' if company.official_site else '<span class="no-data">N/A</span>'
    
    # Ticker with exchange
    ticker_display = f"{company.exchange}:{company.ticker}" if company.exchange else company.ticker
    
    # Build table rows - matching wireframe exactly with placeholder values
    # NOTE: These are wireframe mock values. Database doesn't have employees/year_founded/professionals
    rows = [
        ("Website:", website_html, "Coverage Summary:", "No"),
        ("Number of Employees", "1,556,999", "Coverage List:", "No"),
        ("Ticker", ticker_display, "Relationships:", "No"),
        ("Current Professionals Profiled:", "36", "Projects:", "No"),
        ("Year Founded", "1858", "Activity Logs/Tasks:", "No"),
    ]
    
    table_html = '<div class="info-table-container"><div class="info-table">'
    
    for label_left, value_left, label_right, value_right in rows:
        table_html += f'<div class="info-table-row">'
        table_html += f'<div class="info-label">{label_left}</div>'
        table_html += f'<div class="info-value">{value_left}</div>'
        table_html += f'<div class="info-label-right">{label_right}</div>'
        table_html += f'<div class="info-value-right">{value_right}</div>'
        table_html += '</div>'
    
    table_html += '</div></div>'
    
    return table_html


def render_tabs(active_tab: str = "profile") -> str:
    """Render the tab navigation - matches Figma exactly.
    Order: Company Profile | Key Stats | Income Statement | Balance Sheet
    """
    tabs = [
        ("profile", "Company Profile"),
        ("stats", "Key Stats"),
        ("income", "Income Statement"),
        ("balance", "Balance Sheet")
    ]
    
    tabs_html = '<div class="tab-navigation">'
    for tab_id, tab_label in tabs:
        active_class = "active" if tab_id == active_tab else ""
        tabs_html += f'<div class="tab-item {active_class}">{tab_label}</div>'
    tabs_html += '</div>'
    
    return tabs_html


def render_business_description(description: Optional[str]) -> str:
    """Render the business description section."""
    if not description:
        description = "No business description available."
    
    html = f"""
    <div class="business-description-section">
        <div class="section-header">Business Description</div>
        <div class="business-description-text">
            {description}
        </div>
    </div>
    """
    
    return html


def render_company_header(company: CompanyOverview) -> str:
    """Render company header with company name and Company Documents button.
    
    Layout per Figma node 20893:206268:
    [Left Side]                          [Right Side]
    CORESIGHT MARKET DATA (red)          [Company Documents Button]
    Macy's Inc. (NYSE:M) ▼
    """
    html = f"""
    <div class="company-header-section">
        <div class="company-header-left">
            <div class="section-title">CORESIGHT MARKET DATA</div>
            <div class="company-name-dropdown">
                <span>{company.name} ({company.exchange or 'NYSE'}:{company.ticker})</span>
                <span class="dropdown-arrow">
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </span>
            </div>
        </div>
        <button class="company-documents-btn">
            <span>Company Documents</span>
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 17L17 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 7H17V17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
    </div>
    """
    return html


def main():
    """Company profile page entry point."""
    # Initialize
    init_database()
    
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
    
    # Render Header
    render_header(full_width=True)
    
    # Get ticker from URL query params or default to M (Macy's)
    query_params = st.query_params
    ticker = query_params.get("ticker", "M")
    
    # Fetch company data
    company = CompanyOverviewRepository.get_company_overview(ticker)
    
    if not company:
        st.error(f"Company data not found for ticker: {ticker}")
        st.stop()
    
    # Inject custom CSS
    st.markdown(get_company_css(), unsafe_allow_html=True)
    
    # Page content container
    st.markdown('<div class="company-profile-container">', unsafe_allow_html=True)
    
    # Get all companies for the dropdown
    companies = CompanyRepository.get_companies()
    
    # Render the company header (title, name, and Company Documents button)
    st.markdown(render_company_header(company), unsafe_allow_html=True)
    
    # Hidden Streamlit selectbox for company selection (functional)
    # This is positioned to look like it's part of the header dropdown
    company_options = {f"{c['name']} ({c['ticker']})": c['ticker'] for c in companies}
    current_display = f"{company.name} ({company.ticker})"
    
    # Find current index
    option_list = list(company_options.keys())
    current_index = option_list.index(current_display) if current_display in option_list else 0
    
    # Use a callback to handle selection change
    def on_company_change():
        selected = st.session_state.company_selector
        selected_ticker = company_options[selected]
        if selected_ticker != ticker:
            st.query_params["ticker"] = selected_ticker
            st.rerun()
    
    # Hidden label but functional dropdown
    st.selectbox(
        "Select Company",
        options=option_list,
        index=current_index,
        key="company_selector",
        on_change=on_company_change,
        label_visibility="collapsed"
    )
    
    # Tab navigation
    st.markdown(render_tabs(active_tab="profile"), unsafe_allow_html=True)
    
    # Info table
    st.markdown(render_info_table(company), unsafe_allow_html=True)
    
    # Business description
    st.markdown(render_business_description(company.company_description), unsafe_allow_html=True)
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Render Footer
    render_coresight_footer(full_width=True, stick_to_bottom=True)


if __name__ == "__main__":
    main()
