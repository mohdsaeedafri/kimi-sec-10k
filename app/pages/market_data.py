"""
Market Data Page - PIXEL PERFECT FIGMA MATCH
============================================
Based on detailed wireframe analysis
"""
import streamlit as st
from datetime import date
from typing import Optional, List

from components.styles import render_styles, COLORS
from data.repository import CompanyRepository, IncomeStatementRepository
from data.models import IncomeStatementData, Company
from utils.local_storage import (
    get_marketdata_company, set_marketdata_company,
    get_marketdata_tab, set_marketdata_tab,
    get_marketdata_date_range, set_marketdata_date_range
)


def format_value(value: Optional[float], conversion_rate: float = 1.0) -> str:
    """Format value in millions with comma separator and currency conversion."""
    if value is None:
        return "-"
    converted = value * conversion_rate
    return f"{converted:,.1f}"


def get_indent_level(label: str) -> int:
    """Get indentation level based on row type."""
    level_0 = {"Revenue", "Total Revenue", "Gross Profit", "Operating Income"}
    level_1 = {"Other Revenue", "Cost Of Goods Sold", "Selling General & Admin Exp.",
               "R&D Exp.", "Depreciation & Amort.", "Other Operating Expense/(Income)",
               "Other Operating Exp., Total", "Interest Expense", "Interest and Invest. Income",
               "Net Interest Exp."}
    
    if label in level_0:
        return 0
    elif label in level_1:
        return 1
    return 1


def is_gray_text(label: str) -> bool:
    """Check if row should have gray text - ONLY specific rows per Figma."""
    gray_labels = {"R&D Exp.", "Depreciation & Amort.", "Other Operating Expense/(Income)",
                   "Interest and Invest. Income"}
    return label in gray_labels


def get_underline_style(label: str) -> str:
    """
    Get underline style based on row type per Figma:
    - 'grey': Light grey underline (85% width, starts after indent)
    - 'black': Darker underline (90% width, for subtotals)
    - 'none': No underline
    """
    grey_underline_rows = {"Other Revenue", "Cost Of Goods Sold", 
                           "Other Operating Expense/(Income)", "Interest and Invest. Income"}
    black_underline_rows = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
                           "Operating Income", "Net Interest Exp."}
    
    if label in grey_underline_rows:
        return "grey"
    elif label in black_underline_rows:
        return "black"
    return "none"


def get_conversion_rate(from_currency: str, to_currency: str) -> float:
    """Get conversion rate between currencies."""
    if from_currency == to_currency:
        return 1.0
    
    rates = {
        ('USD', 'EUR'): 0.85,
        ('USD', 'GBP'): 0.73,
        ('USD', 'JPY'): 110.0,
        ('USD', 'CAD'): 1.25,
        ('USD', 'AUD'): 1.35,
        ('USD', 'CHF'): 0.92,
        ('USD', 'CNY'): 6.45,
        ('USD', 'INR'): 74.5,
        ('EUR', 'USD'): 1.18,
        ('GBP', 'USD'): 1.37,
        ('JPY', 'USD'): 0.0091,
        ('CAD', 'USD'): 0.80,
        ('AUD', 'USD'): 0.74,
        ('CHF', 'USD'): 1.09,
        ('CNY', 'USD'): 0.155,
        ('INR', 'USD'): 0.0134,
    }
    return rates.get((from_currency, to_currency), 1.0)


def render_page():
    """Main render function - PIXEL PERFECT FIGMA MATCH."""
    
    # Get data first
    companies = CompanyRepository.get_companies_by_source()
    if not companies:
        st.error("No companies found")
        return
    
    stored_ticker = get_marketdata_company()
    selected_ticker = stored_ticker if stored_ticker and any(
        c.ticker == stored_ticker for c in companies
    ) else companies[0].ticker
    
    selected_company = next(
        (c for c in companies if c.ticker == selected_ticker),
        companies[0]
    )
    
    stored_tab = get_marketdata_tab()
    selected_tab = stored_tab if stored_tab in [
        "income_statement", "key_stats", "company_profile"
    ] else "income_statement"
    
    # Get dates
    min_date, max_date = IncomeStatementRepository.get_date_range(selected_ticker)
    available_dates = IncomeStatementRepository.get_available_dates(selected_ticker)
    
    stored_start, stored_end = get_marketdata_date_range()
    start_date = date.fromisoformat(stored_start) if stored_start else min_date
    end_date = date.fromisoformat(stored_end) if stored_end else max_date
    
    # Get currency from database
    reported_currency = IncomeStatementRepository.get_reported_currency(
        selected_ticker, end_date
    ) or "USD"
    
    # Initialize session state for target currency if not exists
    if 'target_currency' not in st.session_state:
        st.session_state.target_currency = "USD"
    
    # Get conversion rate
    conversion_rate = get_conversion_rate(reported_currency, st.session_state.target_currency)
    
    # ==================== GLOBAL CSS - PIXEL PERFECT ====================
    st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary-red: #D62E2F;
        --dark-text: #111827;
        --body-text: #374151;
        --secondary-text: #6B7280;
        --light-gray-text: #9CA3AF;
        --border-light: #E5E7EB;
        --border-medium: #D1D5DB;
        --bg-light: #F9FAFB;
        --bg-gray: #F3F4F6;
        --white: #FFFFFF;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    .block-container {padding: 0 40px !important; max-width: 100% !important;}
    
    /* Page title */
    .page-title {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        color: var(--primary-red);
        margin: 30px 0 4px 0;
    }
    
    /* Company selector */
    .company-selector {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 25px;
    }
    
    .company-name {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 22px;
        color: var(--dark-text);
    }
    
    .dropdown-chevron {
        font-size: 12px;
        color: var(--secondary-text);
    }
    
    /* Tabs */
    .tabs-container {
        display: flex;
        gap: 60px;
        border-bottom: 1px solid var(--border-light);
        margin-bottom: 30px;
    }
    
    .tab {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        padding: 12px 0;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        margin-bottom: -1px;
    }
    
    .tab-active {
        color: var(--primary-red);
        font-weight: 500;
        border-bottom-color: var(--primary-red);
    }
    
    .tab-inactive {
        color: var(--secondary-text);
        font-weight: 400;
    }
    
    /* Filter row */
    .date-label {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 400;
        color: var(--secondary-text);
        margin-bottom: 6px;
    }
    
    /* Streamlit selectbox styling */
    div[data-testid="stSelectbox"] > div > div {
        background-color: var(--white) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stSelectbox"] > div > div > div {
        padding: 10px 14px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        color: var(--body-text) !important;
    }
    
    /* TABLE STYLING - PIXEL PERFECT FROM FIGMA */
    .table-container {
        border: 1px solid var(--border-light);
        border-radius: 8px;
        overflow: hidden;
        background: var(--white);
    }
    
    .table-scroll {
        overflow-x: auto;
    }
    
    .data-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
    }
    
    /* Header - light grey background */
    .data-table thead {
        background-color: var(--bg-light);
    }
    
    .data-table th {
        padding: 16px;
        text-align: left;
        font-weight: 600;
        border-bottom: 1px solid var(--border-light);
        white-space: nowrap;
        color: var(--dark-text);
    }
    
    .data-table th:first-child {
        min-width: 280px;
        background-color: var(--bg-light);
    }
    
    .data-table th.data-col {
        text-align: center;
        min-width: 140px;
    }
    
    .header-subtext {
        display: block;
        font-size: 11px;
        font-weight: 400;
        color: var(--secondary-text);
        margin-top: 4px;
    }
    
    .period-label {
        display: block;
        font-size: 12px;
        font-weight: 500;
        color: var(--secondary-text);
        margin-bottom: 2px;
    }
    
    .period-date {
        font-size: 14px;
        font-weight: 600;
        color: var(--dark-text);
    }
    
    /* Table body */
    .data-table td {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-light);
        vertical-align: middle;
    }
    
    /* FIRST COLUMN - LIGHT GREY BACKGROUND, BLACK TEXT */
    .data-table td:first-child {
        text-align: left;
        background-color: var(--bg-light);
        color: var(--dark-text);
        font-weight: 500;
    }
    
    .data-table td.data-cell {
        text-align: right;
        font-variant-numeric: tabular-nums;
        background-color: var(--white);
    }
    
    /* Row text colors for data columns */
    .row-text-dark {
        color: var(--body-text);
    }
    
    .row-text-gray {
        color: var(--secondary-text) !important;
    }
    
    /* Indentation */
    .indent-0 { padding-left: 16px !important; }
    .indent-1 { padding-left: 36px !important; }
    .indent-2 { padding-left: 56px !important; }
    
    /* Font weights */
    .font-regular { font-weight: 400; }
    .font-semibold { font-weight: 600; }
    
    /* PARTIAL UNDERLINE - GREY (85% width) */
    .underline-grey td.data-cell {
        border-top: 1px solid var(--border-medium);
        background: linear-gradient(to right, transparent 15%, var(--border-medium) 15%, var(--border-medium) 100%, transparent 100%);
        background-size: 100% 1px;
        background-position: bottom;
        background-repeat: no-repeat;
    }
    
    /* PARTIAL UNDERLINE - BLACK (90% width, thicker) */
    .underline-black td.data-cell {
        border-top: 1px solid var(--dark-text);
        font-weight: 600;
    }
    
    /* Alternative underline approach using pseudo-element simulation */
    .row-underline-grey td.data-cell {
        position: relative;
    }
    
    .row-underline-grey td.data-cell::before {
        content: '';
        position: absolute;
        top: 0;
        left: 10%;
        right: 5%;
        height: 1px;
        background-color: var(--border-medium);
    }
    
    .row-underline-black td.data-cell {
        position: relative;
    }
    
    .row-underline-black td.data-cell::before {
        content: '';
        position: absolute;
        top: 0;
        left: 5%;
        right: 5%;
        height: 1px;
        background-color: var(--dark-text);
    }
    
    /* CURRENCY CONVERSION - LEFT SIDE ONLY */
    .currency-section {
        margin-top: 30px;
        max-width: 500px;
    }
    
    .currency-label {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 400;
        color: var(--secondary-text);
        margin-bottom: 12px;
    }
    
    .currency-row {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .currency-box {
        background: var(--white);
        border: 1px solid var(--border-medium);
        border-radius: 6px;
        padding: 12px 16px;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        color: var(--body-text);
        min-width: 160px;
    }
    
    .currency-arrow {
        color: var(--light-gray-text);
        font-size: 18px;
        font-weight: 300;
    }
    </style>
    """)
    
    # ==================== TITLE SECTION ====================
    st.html(f'<div class="page-title">CORESIGHT MARKET DATA</div>')
    
    col_title, col_select = st.columns([4, 1])
    with col_title:
        st.html(f"""
            <div class="company-selector">
                <span class="company-name">{selected_company.display_name}</span>
                <span class="dropdown-chevron">▼</span>
            </div>
        """)
    
    with col_select:
        company_options = {c.display_name: c.ticker for c in companies}
        current_display = selected_company.display_name
        
        new_display = st.selectbox(
            "Company",
            options=list(company_options.keys()),
            index=list(company_options.keys()).index(current_display),
            label_visibility="collapsed",
            key="company_sel"
        )
        new_ticker = company_options[new_display]
        
        if new_ticker != selected_ticker:
            set_marketdata_company(new_ticker)
            new_min, new_max = IncomeStatementRepository.get_date_range(new_ticker)
            if new_min and new_max:
                set_marketdata_date_range(new_min.isoformat(), new_max.isoformat())
            st.rerun()
    
    # ==================== TABS ====================
    st.html("""
        <div class="tabs-container">
            <div class="tab tab-active">Income Statement</div>
            <div class="tab tab-inactive">Key Stats</div>
            <div class="tab tab-inactive">Company Profile</div>
        </div>
    """)
    
    # Hidden tab buttons
    tab_cols = st.columns([1, 1, 1, 6])
    for i, (tab_key, label) in enumerate([
        ("income_statement", "Income Statement"),
        ("key_stats", "Key Stats"),
        ("company_profile", "Company Profile")
    ]):
        with tab_cols[i]:
            if st.button(label, key=f"tabbtn_{tab_key}", type="tertiary", use_container_width=True):
                set_marketdata_tab(tab_key)
                st.rerun()
    
    # ==================== FILTER ROW - DATES ONLY ====================
    date_options = [d.strftime("%B %Y") for d in available_dates]
    date_values = {d.strftime("%B %Y"): d for d in available_dates}
    
    curr_start = start_date.strftime("%B %Y")
    start_idx = date_options.index(curr_start) if curr_start in date_options else 0
    
    curr_end = end_date.strftime("%B %Y")
    end_idx = date_options.index(curr_end) if curr_end in date_options else len(date_options) - 1
    
    f1, f2, f3 = st.columns([6, 1.2, 1.2])
    
    with f2:
        st.html('<div class="date-label">Start Date</div>')
        new_start_label = st.selectbox(
            "Start",
            options=date_options,
            index=start_idx,
            label_visibility="collapsed",
            key="start_dt"
        )
        new_start_date = date_values.get(new_start_label, start_date)
    
    with f3:
        st.html('<div class="date-label">End Date</div>')
        new_end_label = st.selectbox(
            "End",
            options=date_options,
            index=end_idx,
            label_visibility="collapsed",
            key="end_dt"
        )
        new_end_date = date_values.get(new_end_label, end_date)
    
    # Update dates if changed
    if new_start_date != start_date or new_end_date != end_date:
        if new_start_date > new_end_date:
            st.error("Start date must be before end date")
        else:
            set_marketdata_date_range(new_start_date.isoformat(), new_end_date.isoformat())
            st.rerun()
    
    # ==================== TABLE WITH CURRENCY CONVERSION ====================
    if selected_tab in ["income_statement", "key_stats"]:
        try:
            data = IncomeStatementRepository.get_income_statement_data(
                selected_ticker, start_date, end_date
            )
            
            if data.periods and data.line_items:
                # Build table HTML
                html = '<div class="table-container"><div class="table-scroll"><table class="data-table"><thead>'
                
                # Header row
                html += '<tr><th>For Fiscal Period Ending<span class="header-subtext">Millions of trading currency, except per share items.</span></th>'
                for period in data.periods:
                    lines = period.label.split('\n')
                    if len(lines) >= 2:
                        period_text = lines[0]
                        date_text = lines[1]
                    else:
                        period_text = ""
                        date_text = period.label
                    
                    html += f'<th class="data-col"><span class="period-label">{period_text}</span><span class="period-date">{date_text}</span></th>'
                html += '</tr></thead><tbody>'
                
                # Data rows with currency conversion applied
                for item in data.line_items:
                    indent = get_indent_level(item.label)
                    is_gray = is_gray_text(item.label)
                    underline_style = get_underline_style(item.label)
                    
                    # Determine text color class for data columns
                    if is_gray:
                        text_class = "row-text-gray"
                    else:
                        text_class = "row-text-dark"
                    
                    # Determine underline class
                    if underline_style == "grey":
                        underline_class = "row-underline-grey"
                    elif underline_style == "black":
                        underline_class = "row-underline-black"
                    else:
                        underline_class = ""
                    
                    html += f'<tr class="{underline_class}">'
                    
                    # First column - LIGHT GREY BACKGROUND, BLACK TEXT (per Figma)
                    html += f'<td class="indent-{indent}">{item.label}</td>'
                    
                    # Data columns with converted values
                    for val in item.values:
                        formatted = format_value(val, conversion_rate)
                        html += f'<td class="data-cell {text_class}">{formatted}</td>'
                    
                    html += '</tr>'
                
                html += '</tbody></table></div></div>'
                st.html(html)
                
                # ==================== CURRENCY CONVERSION - LEFT SIDE ONLY ====================
                st.html('<div class="currency-section"><div class="currency-label">Currency Conversion</div>')
                
                c1, c2, c3, c4 = st.columns([1.5, 0.3, 1.5, 6])
                
                with c1:
                    st.html(f'<div class="currency-box">{reported_currency}</div>')
                
                with c2:
                    st.html('<div class="currency-arrow">→</div>')
                
                with c3:
                    currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "CNY", "INR"]
                    default_index = currencies.index("USD")
                    
                    target = st.selectbox(
                        "To",
                        options=currencies,
                        index=default_index,
                        label_visibility="collapsed",
                        key="currency_to"
                    )
                    
                    if target != st.session_state.target_currency:
                        st.session_state.target_currency = target
                        st.rerun()
                
                st.html('</div>')
                
                if st.session_state.target_currency != reported_currency:
                    rate = get_conversion_rate(reported_currency, st.session_state.target_currency)
                    st.caption(f"Converted at 1 {reported_currency} = {rate:.4f} {st.session_state.target_currency}")
                
            else:
                st.info("No data available")
                
        except Exception as e:
            st.error(f"Error: {e}")
    
    elif selected_tab == "company_profile":
        st.info("Company Profile")
        st.markdown(f'<a href="http://localhost:8504/company_profile?ticker={selected_ticker}" target="_blank">View Profile</a>', unsafe_allow_html=True)
