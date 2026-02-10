"""
Newsroom Page Entry Point
=========================
Standalone Streamlit page for newsroom with Coresight header/footer.
URL: /newsroom

ADJUSTABLE LAYOUT:
- Body padding: set_page_layout(body_padding="0 20px")  # "top_bottom left_right"
- Max content width: set_page_layout(max_content_width="1350px")
- See components/styles.py for all options
"""
import streamlit as st

# Configure page settings - MUST be first Streamlit command
st.set_page_config(
    page_title="Coresight Newsroom",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import after page config
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# IMMEDIATELY hide sidebar to prevent skeleton flash
from components.styles import hide_sidebar, set_page_layout
hide_sidebar()

from datetime import datetime, timedelta, date
from components.styles import render_styles, COLORS
from components.navigation import render_header, render_coresight_footer
from data.models import NewsCategory, NewsArticle
from data.dummy_data import NewsRepository
from utils.local_storage import init_local_storage


def initialize_app():
    """Initialize application state and dependencies."""
    init_local_storage()


def format_time_ago(published_at: datetime) -> str:
    """Format datetime as relative time."""
    now = datetime.now()
    diff = now - published_at
    
    if diff.days == 0:
        hours = diff.seconds // 3600
        if hours == 0:
            minutes = diff.seconds // 60
            return f"({minutes} minutes ago)"
        return f"({hours} hours, {diff.seconds % 3600 // 60} minutes ago)"
    elif diff.days == 1:
        return "(1 day ago)"
    elif diff.days < 7:
        return f"({diff.days} days ago)"
    elif diff.days < 30:
        weeks = diff.days // 7
        return f"({weeks} weeks ago)"
    else:
        return published_at.strftime("(%B %d, %Y)")


def render_news_article(article: NewsArticle):
    """Render a single news article using Streamlit native components."""
    # Format date
    date_str = article.published_at.strftime("%B %d, %Y")
    time_ago = format_time_ago(article.published_at)
    
    # Container for the article
    with st.container():
        # Source and Date row using columns
        cols = st.columns([1, 1])
        with cols[0]:
            st.markdown(f"<span style='color: #6C757D; font-size: 0.875rem;'>{article.source}</span>", unsafe_allow_html=True)
        with cols[1]:
            st.markdown(f"<span style='color: #6C757D; font-size: 0.875rem; float: right;'>{date_str} {time_ago}</span>", unsafe_allow_html=True)
        
        # Headline
        st.markdown(f"""
        <h2 style="
            font-size: 1.25rem;
            font-weight: 600;
            color: #212529;
            margin: 8px 0 8px 0;
            line-height: 1.4;
        ">
            {article.headline}
        </h2>
        """, unsafe_allow_html=True)
        
        # Summary
        st.markdown(f"""
        <p style="
            font-size: 0.9375rem;
            color: #495057;
            margin: 0 0 8px 0;
            line-height: 1.5;
        ">{article.summary}</p>
        """, unsafe_allow_html=True)
        
        # Tagged Companies
        if article.related_tickers:
            company_map = {
                "MSFT": "Microsoft Corporation",
                "ATVI": "Activision Blizzard",
                "WMT": "Walmart Inc.",
                "AAPL": "Apple Inc.",
                "TSLA": "Tesla Inc.",
                "AMZN": "Amazon.com Inc.",
                "GOOGL": "Alphabet Inc.",
                "META": "Meta Platforms Inc.",
                "NVDA": "NVIDIA Corporation",
                "JPM": "JPMorgan Chase & Co.",
                "JNJ": "Johnson & Johnson",
                "V": "Visa Inc.",
                "MA": "Mastercard Inc.",
                "BAC": "Bank of America",
                "C": "Citigroup Inc.",
                "SPY": "S&P 500 ETF",
                "QQQ": "Nasdaq-100 ETF",
                "ESG": "ESG Index",
            }
            companies = [company_map.get(t, t) for t in article.related_tickers[:3]]
            if companies:
                company_links = " | ".join([f"<a href='#' style='color: #DC3545; text-decoration: none;'>{c}</a>" for c in companies])
                st.markdown(f"""
                <p style="
                    font-size: 0.9375rem;
                    color: #212529;
                    font-weight: 500;
                    margin: 0 0 16px 0;
                ">Tagged Companies: {company_links}</p>
                """, unsafe_allow_html=True)
        
        # Divider
        st.markdown("<hr style='border: none; border-top: 1px solid #DEE2E6; margin: 16px 0;'>", unsafe_allow_html=True)


def main():
    """Newsroom page entry point."""
    # Initialize
    initialize_app()
    
    # Render global styles
    render_styles()
    
    # ADJUSTABLE LAYOUT - Modify these parameters as needed
    # LOCATION: This call is in app/pages/newsroom.py
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
    .stApp {
        background-color: #FFFFFF;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render Header (shared component from components/navigation.py)
    # This renders: Logo, Market Data (link), Newsroom (active), Contact Us button
    render_header(full_width=True)
    
    # Fetch and render articles
    articles = NewsRepository.get_articles(
        search_query=None,
        date_from=date.today() - timedelta(days=30),
        date_to=date.today(),
        sort_by="published_at",
        limit=20
    )
    
    # Render articles
    for article in articles:
        render_news_article(article)
    
    # Render Footer (shared component from components/navigation.py)
    render_coresight_footer(full_width=True, stick_to_bottom=True)


# Entry point
if __name__ == "__main__":
    main()
