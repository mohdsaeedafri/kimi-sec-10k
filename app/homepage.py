"""
Homepage Entry Point - Coresight Research
EXACT match to Figma design
"""
import streamlit as st

st.set_page_config(
    page_title="Coresight Market Data - Research Portal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from components.styles import hide_sidebar, render_styles
from components.navigation import render_header, render_coresight_footer
from pages.home import main as home_main

hide_sidebar()

if __name__ == "__main__":
    home_main()
