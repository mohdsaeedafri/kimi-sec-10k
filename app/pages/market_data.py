"""
Market Data Page - Income Statement View
=======================================
Real financial data from coreiq_av_financials_income_statement table.
"""
import streamlit as st
from datetime import date
from typing import Optional, List

from components.styles import render_styles, COLORS
from data.repository import CompanyRepository, IncomeStatementRepository
from data.models import IncomeStatementData, Company
from utils.local_storage import (
    get_marketdata_source, set_marketdata_source,
    get_marketdata_company, set_marketdata_company,
    get_marketdata_tab, set_marketdata_tab,
    get_marketdata_date_range, set_marketdata_date_range
)


def format_value(value: Optional[float]) -> str:
    """Format value in millions with comma separator."""
    if value is None:
        return "-"
    return f"{value:,.1f}"


def render_company_selector(companies: List[Company], selected_ticker: str):
    """Render the company dropdown with logo."""
    selected_company = next((c for c in companies if c.ticker == selected_ticker), companies[0] if companies else None)
    
    if not selected_company:
        st.error("No companies available")
        return None
    
    # Display company name with dropdown arrow
    display_name = selected_company.display_name
    
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="color: #d62e2f; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
            CORESIGHT MARKET DATA
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 20px; font-weight: 600; color: #212529;">{display_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return selected_company

def render_tabs(selected_tab: str) -> str:
    tabs = ["income_statement", "key_stats", "company_profile"]
    tab_labels = ["Income Statement", "Key Stats", "Company Profile"]

    cols = st.columns([1, 1, 1, 3])

    for i, (tab_key, label) in enumerate(zip(tabs, tab_labels)):
        with cols[i]:
            is_active = selected_tab == tab_key

            if is_active:
                st.markdown(f"""
                <div style="
                    color: #d62e2f;
                    font-weight: 600;
                    font-size: 16px;
                    border-bottom: 2px solid #d62e2f;
                    text-align: center;
                    height: 42px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    position: relative;
                    z-index: 1;
                ">
                {label}
                </div>
                """, unsafe_allow_html=True)
            else:
                if st.button(label, key=f"tab_{tab_key}", type="tertiary", use_container_width=True):
                    set_marketdata_tab(tab_key)
                    st.rerun()

    st.markdown("""
        <style>
            .tabs-hr-wrapper {
                margin-top: -1.5rem;
            }
        </style>
        <div class="tabs-hr-wrapper">
            <hr style="border: none; border-top: 2px solid #dee2e6; margin: 0;">
        </div>
    """, unsafe_allow_html=True)

    return selected_tab

# def render_tabs(selected_tab: str) -> str:
#     """Render the three tabs."""
#     tabs = ["income_statement", "key_stats", "company_profile"]
#     tab_labels = ["Income Statement", "Key Stats", "Company Profile"]
    
#     # Create tab buttons
#     cols = st.columns([1, 1, 1, 3])  # 3 tabs + empty space
    
#     for i, (tab_key, label) in enumerate(zip(tabs, tab_labels)):
#         with cols[i]:
#             is_active = selected_tab == tab_key
#             if is_active:
#                 st.markdown(f"""
#                 <div style="
#                     color: #d62e2f;
#                     font-weight: 600;
#                     font-size: 16px;
#                     padding-bottom: 4px;
#                     border-bottom: 2px solid #d62e2f;
#                     text-align: center;
#                 ">{label}</div>
#                 """, unsafe_allow_html=True)
                
#             else:
#                 if st.button(label, key=f"tab_{tab_key}", type="tertiary", use_container_width=True):
#                     set_marketdata_tab(tab_key)
#                     st.rerun()
            
#     st.markdown("<hr style='border: none; border-top: 1px solid #dee2e6; margin: 0;'>", unsafe_allow_html=True)
    
#     return selected_tab


def render_filters_row(
    # sources: List[str],
    # selected_source: str,
    available_dates: List[date],
    start_date: date,
    end_date: date
):
    """Render the filter row with Data Source, PDFs, and Date pickers."""
    col1,col2, col3, col4 = st.columns([4, 1.5, 1, 1])
    
    with col1:
        pass
        # st.markdown("<div style='color: #6c757d; font-size: 14px; margin-bottom: 6px; text-align:center'>Data Source</div>", unsafe_allow_html=True)
        # new_source = st.selectbox(
        #     "Data Source",
        #     options=sources,
        #     index=sources.index(selected_source) if selected_source in sources else 0,
        #     label_visibility="collapsed",
        #     key="data_source_select"
        # )
        # if new_source != selected_source:
        #     set_marketdata_source(new_source)
        #     # Reset company when source changes
        #     st.rerun()
    # with col9:
    #     st.markdown("&nbsp;")
    
    with col2:
        st.markdown("<div style='margin-bottom:4px;'>&nbsp;</div>", unsafe_allow_html=True)

        pdf_col1, pdf_col2 = st.columns([1, 1])

        with pdf_col1:
            if st.button("10-K 📑", key="10k", use_container_width=True):
                print("10-K clicked")

        with pdf_col2:
            if st.button("10-Q 📑", key="10q", use_container_width=True):
                print("10-Q clicked")
    
    with col3:
        st.markdown("<div style='color: #6c757d; font-size: 14px; margin-bottom: 6px; text-align: center;'>Start Date</div>", unsafe_allow_html=True)
        date_options = [d.strftime("%B %Y") for d in available_dates]
        date_values = {d.strftime("%B %Y"): d for d in available_dates}
        
        current_start_label = start_date.strftime("%B %Y")
        if current_start_label in date_options:
            start_index = date_options.index(current_start_label)
        else:
            start_index = len(date_options) - 1 if date_options else 0
        
        new_start_label = st.selectbox(
            "Start Date",
            options=date_options,
            index=start_index,
            label_visibility="collapsed",
            key="start_date_select"
        )
        new_start_date = date_values.get(new_start_label, start_date)
    
    with col4:
        st.markdown("<div style='color: #6c757d; font-size: 14px; margin-bottom: 6px; text-align: center; margin-left: 10px;'>End Date</div>", unsafe_allow_html=True)
        current_end_label = end_date.strftime("%B %Y")
        if current_end_label in date_options:
            end_index = date_options.index(current_end_label)
        else:
            end_index = 0 if date_options else 0
        
        new_end_label = st.selectbox(
            "End Date",
            options=date_options,
            index=end_index,
            label_visibility="collapsed",
            key="end_date_select"
        )
        new_end_date = date_values.get(new_end_label, end_date)
    
    # with col5:
    #     st.markdown("&nbsp;")
    
    # Validate date range
    if new_start_date > new_end_date:
        st.error("Start date must be before end date")
        return start_date, end_date
    
    # Save if changed
    if new_start_date != start_date or new_end_date != end_date:
        set_marketdata_date_range(new_start_date.isoformat(), new_end_date.isoformat())
        st.rerun()
    
    return new_start_date, new_end_date


def render_income_statement_table(data: IncomeStatementData):
    """Render the income statement table matching screenshot design."""
    if not data.periods or not data.line_items:
        st.info("No data available for selected date range")
        return
    
    # Build table header
    header_cols = ["For Fiscal Period Ending"] + [p.label.replace("\n", "<br>") for p in data.periods]
    num_cols = len(header_cols)
    
    # Sub-total / section-summary rows get bold + light bg
    subtotal_labels = {
        "Total Revenue", "Gross Profit", "Operating Income",
        "Other Operating Exp., Total", "Net Interest Exp."
    }
    # Indented child rows (shown with padding-left in the screenshot)
    indented_labels = {
        "Total Revenue", "Gross Profit", "Operating Income",
        "Other Operating Exp., Total", "Net Interest Exp."
    }
    # Section-starting rows: draw a heavier top border to visually group
    section_start_labels = {
        "Cost Of Goods Sold", "Selling General & Admin Exp.",
        "Other Operating Expense/(Income)", "Interest Expense"
    }

    # --- Table CSS ---
    table_html = """
    <style>
    .income-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 13px;
        margin-top: 8px;
    }
    .income-table th {
        padding: 10px 12px;
        text-align: center;
        font-weight: 600;
        font-size: 12px;
        color: #212529;
        border-bottom: 1px solid #dee2e6;
        background: #fff;
    }
    .income-table th:first-child {
        text-align: left;
    }
    .income-table td {
        padding: 7px 12px;
        border-bottom: 1px solid #eee;
        text-align: right;
        font-size: 13px;
        color: #212529;
    }
    .income-table td:first-child {
        text-align: left;
        color: #212529;
    }
    .income-table .subtotal-row td {
        font-weight: 600;
    }
    .income-table .indented-label {
        padding-left: 24px;
    }
    .income-table .section-start td {
        border-top: 1px solid #ccc;
    }
    .income-table .sub-text {
        color: #6c757d;
        font-size: 11px;
        font-style: italic;
    }
    </style>
    <table class="income-table">
    """

    # Header row
    table_html += "<tr>"
    for i, col in enumerate(header_cols):
        align = "left" if i == 0 else "center"
        table_html += f'<th style="text-align:{align};">{col}</th>'
    table_html += "</tr>"

    # Subheader row (italic note)
    table_html += (
        f'<tr><td class="sub-text" colspan="{num_cols}" '
        f'style="border-bottom:none; padding: 2px 12px 6px;">'
        f'Millions of trading current, except per share items.</td></tr>'
    )

    # Data rows
    for item in data.line_items:
        classes = []
        if item.label in subtotal_labels:
            classes.append("subtotal-row")
        if item.label in section_start_labels:
            classes.append("section-start")
        class_attr = f' class="{" ".join(classes)}"' if classes else ""

        table_html += f"<tr{class_attr}>"

        # Label cell — indent sub-items
        if item.label in indented_labels:
            table_html += f'<td class="indented-label">{item.label}</td>'
        else:
            table_html += f'<td>{item.label}</td>'

        # Value cells
        for value in item.values:
            formatted = format_value(value)
            table_html += f'<td>{formatted}</td>'
        table_html += "</tr>"

    table_html += "</table>"
    st.markdown(table_html, unsafe_allow_html=True)

    # --- Currency Conversion section (bottom of screenshot) ---
    st.markdown("""<div style="margin-top:24px; padding-top:16px; border-top:1px solid #eee;">
        <div style="font-size:12px; color:#6c757d; margin-bottom:6px;">Currency Conversion</div>
        <div style="display:flex; align-items:center; gap:10px; font-size:13px; color:#212529;">
            <span style="border:1px solid #dee2e6; border-radius:4px; padding:5px 12px;">Trading Currency</span>
            <span style="color:#6c757d;">→</span>
            <span style="border:1px solid #dee2e6; border-radius:4px; padding:5px 12px;">Conversion ▾</span>
        </div>
    </div>""", unsafe_allow_html=True)


def render_page():
    """Main render function for Market Data page."""
    
    # Get all data sources
    # sources = CompanyRepository.get_all_sources()
    # if not sources:
    #     st.error("No data sources available")
    #     return
    
    # # Get stored values or defaults
    # stored_source = get_marketdata_source()
    # selected_source = stored_source if stored_source in sources else sources[0]
    
    # Get companies for selected source
    companies = CompanyRepository.get_companies_by_source()
    if not companies:
        st.error(f"No companies found")
        return
    
    stored_ticker = get_marketdata_company()
    selected_ticker = stored_ticker if stored_ticker and any(c.ticker == stored_ticker for c in companies) else companies[0].ticker
    
    stored_tab = get_marketdata_tab()
    selected_tab = stored_tab if stored_tab in ["income_statement", "key_stats", "company_profile"] else "income_statement"
    
    # Get date range for selected company
    min_date, max_date = IncomeStatementRepository.get_date_range(selected_ticker)
    available_dates = IncomeStatementRepository.get_available_dates(selected_ticker)
    
    if not min_date or not max_date or not available_dates:
        st.error(f"No financial data available for {selected_ticker}")
        return
    
    # Get stored dates or use defaults
    stored_start, stored_end = get_marketdata_date_range()
    try:
        start_date = date.fromisoformat(stored_start) if stored_start else min_date
    except:
        start_date = min_date
    
    try:
        end_date = date.fromisoformat(stored_end) if stored_end else max_date
    except:
        end_date = max_date
    
    # Ensure dates are within available range
    if start_date not in available_dates:
        start_date = min_date
    if end_date not in available_dates:
        end_date = max_date
    
    # Render company selector dropdown
    col1, col2 = st.columns([4, 1])
    with col1:
        selected_company = render_company_selector(companies, selected_ticker)
    with col2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        new_ticker = st.selectbox(
            "Select Company",
            options=[c.ticker for c in companies],
            format_func=lambda x: next((c.display_name for c in companies if c.ticker == x), x),
            index=[c.ticker for c in companies].index(selected_ticker),
            label_visibility="collapsed",
            key="company_select"
        )
        if new_ticker != selected_ticker:
            set_marketdata_company(new_ticker)
            # Reset dates when company changes
            new_min, new_max = IncomeStatementRepository.get_date_range(new_ticker)
            if new_min and new_max:
                set_marketdata_date_range(new_min.isoformat(), new_max.isoformat())
            st.rerun()
    
    # Render tabs
    selected_tab = render_tabs(selected_tab)
    # st.markdown("<hr style='margin: 0 0 20px 0; border: none; border-top: 100px solid #dee2e6;'>", unsafe_allow_html=True)
    
    # Render filters row
    start_date, end_date = render_filters_row(
        available_dates, start_date, end_date
    )
    
    # Render content based on selected tab
    if selected_tab == "income_statement":
        # Fetch and display income statement data
        with st.spinner("Loading financial data..."):
            try:
                data = IncomeStatementRepository.get_income_statement_data(
                    selected_ticker, start_date, end_date
                )
                render_income_statement_table(data)
            except Exception as e:
                st.error(f"Error loading financial data: {e}")
    
    elif selected_tab == "key_stats":
        # st.info("Key Stats tab - Coming soon")
        try:
                data = IncomeStatementRepository.get_income_statement_data(
                    selected_ticker, start_date, end_date
                )
                render_income_statement_table(data)
        except Exception as e:
                st.error(f"Error loading financial data: {e}")

    
    elif selected_tab == "company_profile":
        st.info("Company Profile tab - Coming soon")
