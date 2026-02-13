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


def is_bold_row(label: str) -> bool:
    """Check if row should be bold (subtotal rows) per Figma."""
    bold_labels = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
                   "Operating Income", "Net Interest Exp."}
    return label in bold_labels


def has_underline(label: str) -> bool:
    """Check if row should have 2px dark grey underline per Figma."""
    underline_labels = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
                        "Operating Income", "Net Interest Exp."}
    return label in underline_labels


def has_grey_separator(label: str) -> bool:
    """Check if row should have 4px grey separator line below it per Figma."""
    separator_labels = {"Total Revenue", "Gross Profit", "Operating Income"}
    return label in separator_labels


def get_indent_level(label: str) -> int:
    """Get indentation level based on row type - 0=normal (12px), 1=indented (24px)."""
    # Level 1: SUBTOTAL/SUMMARY rows - INDENTED (24px left padding)
    level_1 = {"Total Revenue", "Gross Profit", "Other Operating Exp., Total",
               "Operating Income", "Net Interest Exp."}
    
    # Level 0: Regular line items - NOT INDENTED (12px left padding)
    # Revenue, Other Revenue, Cost Of Goods Sold, Selling General & Admin Exp.,
    # R&D Exp., Depreciation & Amort., Other Operating Expense/(Income),
    # Interest Expense, Interest and Invest. Income
    
    if label in level_1:
        return 1  # Subtotals are indented
    else:
        return 0  # Everything else is NOT indented


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
    
    # ==================== GLOBAL CSS - PIXEL PERFECT FIGMA SPECS ====================
    st.html("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,600;0,700;1,400&display=swap');
    
    :root {
        /* Figma Colors - Exact Match */
        --white: #FFFFFF;
        --light-grey: #F9F9F9;
        --black: #000000;
        --dark-grey: #4F4F4F;
        --border-light: #CFCFCF;
        --border-medium: #C1CFCF;
        
        /* Accent Colors */
        --primary-red: #D62E2F;
        
        /* Typography - Figma Specs */
        --font-family: 'Roboto', sans-serif;
        --font-size-base: 16px;
        --font-size-small: 12px;
        --line-height-base: 19px;
        --line-height-compact: 100%;
        
        /* Font Weights */
        --font-weight-regular: 400;
        --font-weight-semibold: 600;
        --font-weight-bold: 700;
        
        /* Spacing */
        --padding-normal: 12px;
        --padding-indented: 24px;
        --padding-top: 4px;
        --gap-small: 2px;
        --gap-medium: 6px;
        
        /* Dimensions */
        --header-height: 48px;
        --row-height: 24px;
        --border-width: 1px;
        --underline-width: 2px;
        
        /* Column Widths */
        --first-column-width: 400px;
        --date-column-width: 164px;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header, .stDeployButton {display: none !important;}
    .block-container {padding: 0 40px !important; max-width: 100% !important;}
    
    /* Hide duplicate Streamlit button tabs (we use styled HTML tabs instead) */
    div[data-testid="stElementContainer"].st-key-tabbtn_income_statement,
    div[data-testid="stElementContainer"].st-key-tabbtn_key_stats,
    div[data-testid="stElementContainer"].st-key-tabbtn_company_profile {
        display: none !important;
    }
    
    /* Page title */
    .page-title {
        font-family: var(--font-family);
        font-weight: var(--font-weight-bold);
        font-size: var(--font-size-small);
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
        font-family: var(--font-family);
        font-weight: var(--font-weight-semibold);
        font-size: 22px;
        color: var(--black);
    }
    
    .dropdown-chevron {
        font-size: var(--font-size-small);
        color: var(--dark-grey);
    }
    
    /* ==================== NAVIGATION TABS - FIGMA EXACT SPECS ==================== */
    .tabs-container {
        display: flex;
        gap: 48px;  /* Figma spec: 48px gap between tabs */
        border-bottom: var(--border-width) solid var(--border-light);
        margin-bottom: 30px;
        padding-top: 8px;  /* Align with Figma 80px header height */
    }
    
    .tab {
        font-family: var(--font-family);
        font-size: var(--font-size-base);  /* 16px Body 1 */
        font-weight: 500;  /* Medium weight from Figma */
        line-height: 26px;  /* Figma height spec */
        padding: 12px 0;
        cursor: pointer;
        border-bottom: 3px solid transparent;
        margin-bottom: -1px;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    
    .tab-active {
        color: var(--primary-red);  /* #D62E2F */
        font-weight: 500;  /* Medium */
        border-bottom-color: var(--primary-red);
    }
    
    .tab-inactive {
        color: rgba(0, 0, 0, 0.6);  /* 60% opacity for inactive */
        font-weight: 400;  /* Regular */
    }
    
    .tab-inactive:hover {
        color: rgba(0, 0, 0, 0.8);  /* Slight hover effect */
    }
    
    /* Filter row */
    .date-label {
        font-family: var(--font-family);
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-regular);
        color: var(--dark-grey);
        margin-bottom: 6px;
    }
    
    /* Streamlit selectbox styling */
    div[data-testid="stSelectbox"] > div > div {
        background-color: var(--white) !important;
        border: var(--border-width) solid var(--border-light) !important;
        border-radius: 6px !important;
    }
    
    div[data-testid="stSelectbox"] > div > div > div {
        padding: 10px 14px !important;
        font-family: var(--font-family) !important;
        font-size: 14px !important;
        color: var(--black) !important;
    }
    
    /* ==================== TABLE STYLING - PIXEL PERFECT FROM FIGMA ==================== */
    
    .table-container {
        border: var(--border-width) solid var(--border-light);
        border-radius: 8px;
        overflow: hidden;
        background: var(--white);
        margin-bottom: 30px;
    }
    
    .table-scroll {
        max-height: 600px;
        overflow-x: auto;
        overflow-y: auto;
    }
    
    .data-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-family: var(--font-family);
        font-size: var(--font-size-base);
    }
    
    /* ========== HEADER ROW - 48px height, grey background ========== */
    .data-table thead {
        background-color: var(--light-grey);
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .data-table th {
        height: var(--header-height);
        padding: var(--padding-top) var(--padding-normal);
        text-align: left;
        font-weight: var(--font-weight-bold);
        font-size: var(--font-size-base);
        line-height: var(--line-height-base);
        color: var(--black);
        border-bottom: var(--border-width) solid var(--border-light);
        background-color: var(--light-grey);
        vertical-align: top;
    }
    
    /* STICKY FIRST COLUMN */
    .data-table th:first-child,
    .data-table td:first-child {
        position: sticky;
        left: 0;
        z-index: 5;
        background-color: var(--light-grey);
    }
    
    .data-table th:first-child {
        min-width: var(--first-column-width);
        max-width: var(--first-column-width);
    }
    
    .data-table td:first-child {
        min-width: var(--first-column-width);
        max-width: var(--first-column-width);
    }
    
    /* Date column headers - right aligned */
    .data-table th.data-col {
        text-align: right;
        min-width: var(--date-column-width);
        padding: var(--padding-top) var(--padding-top) var(--padding-top) var(--padding-normal);
    }
    
    /* Header subtext */
    .header-subtext {
        display: block;
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-regular);
        font-style: italic;
        color: var(--dark-grey);
        margin-top: var(--gap-small);
        line-height: var(--line-height-compact);
    }
    
    /* Period labels in header */
    .period-label {
        display: block;
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-bold);
        color: var(--black);
        line-height: var(--line-height-compact);
        text-align: right;
    }
    
    .period-date {
        display: block;
        font-size: var(--font-size-base);
        font-weight: var(--font-weight-bold);
        color: var(--black);
        line-height: var(--line-height-compact);
        text-align: right;
        margin-top: var(--gap-small);
    }
    
    /* ========== DATA ROWS - 24px height ========== */
    .data-table tbody tr {
        height: var(--row-height);
    }
    
    .data-table td {
        height: var(--row-height);
        padding: var(--padding-top) var(--padding-normal);
        border-bottom: var(--border-width) solid var(--border-light);
        vertical-align: bottom;
        font-size: var(--font-size-base);
        line-height: var(--line-height-base);
    }
    
    /* First column - label column */
    .data-table td:first-child {
        text-align: left;
        background-color: var(--light-grey);
        color: var(--black);
        font-weight: var(--font-weight-regular);
        vertical-align: middle;
    }
    
    /* Data cells - numbers */
    .data-table td.data-cell {
        text-align: right;
        font-variant-numeric: tabular-nums;
        background-color: var(--white);
        color: var(--black);
        font-weight: var(--font-weight-regular);
        padding: var(--padding-top) 8px var(--padding-top) var(--padding-normal);
    }
    
    /* ========== ROW INDENTATION ========== */
    .indent-0 { 
        padding-left: var(--padding-normal) !important; 
    }
    
    .indent-1 { 
        padding-left: var(--padding-indented) !important; 
        background-color: var(--light-grey) !important;
    }
    
    /* ========== BOLD ROWS (Subtotals) ========== */
    .row-bold td:first-child {
        font-weight: var(--font-weight-bold) !important;
        color: var(--dark-grey) !important;
    }
    
    .row-bold td.data-cell {
        font-weight: var(--font-weight-semibold) !important;
        color: var(--dark-grey) !important;
    }
    
    /* ========== UNDERLINES - 2px thick, dark grey ========== */
    .row-underline-black td.data-cell {
        position: relative;
    }
    
    .row-underline-black td.data-cell::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 5%;
        right: 5%;
        height: var(--underline-width);
        background-color: var(--dark-grey);
    }
    
    /* ========== INDENTED ROW BACKGROUNDS ========== */
    .row-indent-grey {
        background-color: var(--light-grey) !important;
    }
    
    /* ========== GREY SEPARATOR - 4px thick ========== */
    .row-grey-separator td,
    .row-grey-separator th {
        border-bottom: 4px solid #CFCFCF;
    }
    
    /* ========== CURRENCY CONVERSION - LEFT SIDE ONLY ========== */
    .currency-section {
        margin-top: 30px;
        max-width: 500px;
    }
    
    .currency-label {
        font-family: var(--font-family);
        font-size: var(--font-size-small);
        font-weight: var(--font-weight-regular);
        color: var(--dark-grey);
        margin-bottom: 12px;
    }
    
    .currency-row {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    
    .currency-box {
        background: var(--white);
        border: var(--border-width) solid var(--border-light);
        border-radius: 6px;
        padding: 12px 16px;
        font-family: var(--font-family);
        font-size: 14px;
        color: var(--black);
        min-width: 160px;
    }
    
    .currency-arrow {
        color: var(--dark-grey);
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
    
    # Hidden tab buttons (COMMENTED OUT - using HTML tabs instead)
    # tab_cols = st.columns([1, 1, 1, 6])
    # for i, (tab_key, label) in enumerate([
    #     ("income_statement", "Income Statement"),
    #     ("key_stats", "Key Stats"),
    #     ("company_profile", "Company Profile")
    # ]):
    #     with tab_cols[i]:
    #         if st.button(label, key=f"tabbtn_{tab_key}", type="tertiary", use_container_width=True):
    #             set_marketdata_tab(tab_key)
    #             st.rerun()
    
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
                
                # Header row - with grey separator
                html += '<tr class="row-grey-separator"><th>For Fiscal Period Ending<span class="header-subtext">Millions of trading currency, except per share items.</span></th>'
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
                prev_item_label = None
                for i, item in enumerate(data.line_items):
                    indent = get_indent_level(item.label)
                    is_bold = is_bold_row(item.label)
                    needs_grey_sep = has_grey_separator(item.label)
                    
                    # Check if NEXT row needs underline, if so add it to THIS row
                    next_item = data.line_items[i + 1] if i + 1 < len(data.line_items) else None
                    needs_underline = has_underline(next_item.label) if next_item else False
                    
                    # Build row classes
                    row_classes = []
                    if is_bold:
                        row_classes.append("row-bold")
                    if needs_underline:
                        row_classes.append("row-underline-black")
                    if needs_grey_sep:
                        row_classes.append("row-grey-separator")
                    
                    row_class_str = ' '.join(row_classes) if row_classes else ''
                    
                    html += f'<tr class="{row_class_str}">'
                    
                    # First column - label with proper indentation
                    html += f'<td class="indent-{indent}">{item.label}</td>'
                    
                    # Data columns with converted values
                    for val in item.values:
                        formatted = format_value(val, conversion_rate)
                        html += f'<td class="data-cell">{formatted}</td>'
                    
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
