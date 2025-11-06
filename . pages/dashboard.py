"""Smart AI Helpdesk - Dashboard Page."""
import streamlit as st
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import TicketManager, AnalyticsDashboard

st.set_page_config(
    page_title="Smart AI Helpdesk - Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS
st.markdown("""
    <style>
    /* Dark theme background */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Card styling */
    .metric-card {
        background-color: #1E2530;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #30363D;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
    }
    
    .metric-label {
        color: #8B949E;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    
    .green-value { color: #10B981; }
    .yellow-value { color: #F59E0B; }
    .white-value { color: white; }
    
    /* Chart containers */
    .chart-container {
        background-color: #1E2530;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #30363D;
        margin: 10px 0;
    }
    
    .chart-title {
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #6366F1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #4F46E5 !important;
    }
    
    /* Ticket card */
    .ticket-card {
        background-color: #1E2530;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #30363D;
        margin: 10px 0;
        color: white;
    }
    
    .ticket-id {
        color: #8B949E;
        font-size: 0.9rem;
    }
    
    .ticket-query {
        font-style: italic;
        color: #C9D1D9;
        margin: 10px 0;
    }
    
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        margin-right: 8px;
    }
    
    .badge-low { background-color: #1E40AF; color: white; }
    .badge-medium { background-color: #D97706; color: white; }
    .badge-high { background-color: #DC2626; color: white; }
    .badge-routed { background-color: #7C3AED; color: white; }
    .badge-category { background-color: #374151; color: white; }
    
    .routed-to {
        color: #A78BFA;
        font-size: 0.9rem;
        margin-top: 10px;
    }
    
    /* Search and filter */
    .stTextInput input {
        background-color: #262D3A !important;
        color: white !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div {
        background-color: #262D3A !important;
        color: white !important;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #8B949E !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsDashboard()

# Top Navigation
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px;'>
            <span style='font-size: 2rem;'>🤖</span>
            <span style='color: white; font-size: 1.5rem; font-weight: bold;'>Smart AI Helpdesk</span>
        </div>
    """, unsafe_allow_html=True)
with col2:
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Get Help", key="nav_help", use_container_width=True):
            st.switch_page("app.py")
    with col_b:
        if st.button("Dashboard", key="nav_dash", use_container_width=True, type="primary"):
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Load data
df = st.session_state.ticket_manager.load_tickets()
stats = st.session_state.ticket_manager.get_statistics()

# KPI Metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Total Tickets</div>
            <div class='metric-value white-value'>{stats['total_tickets']}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>AI Resolved</div>
            <div class='metric-value green-value'>{stats['ai_resolved']}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-label'>Escalated to Human</div>
            <div class='metric-value yellow-value'>{stats['escalated']}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if not df.empty:
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='chart-title'>Issue Type Distribution</div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 6), facecolor='#1E2530')
        ax.set_facecolor('#1E2530')
        
        category_counts = df['category'].value_counts()
        colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444']
        
        wedges, texts, autotexts = ax.pie(
            category_counts.values,
            labels=None,
            autopct='%1.0f%%',
            startangle=90,
            colors=colors
        )
        
        # Style percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_weight('bold')
        
        # Add legend
        legend_labels = [f'{cat} {val/sum(category_counts.values)*100:.0f}%' 
                        for cat, val in category_counts.items()]
        ax.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0.5),
                 frameon=False, fontsize=10, labelcolor='white')
        
        ax.set_title('', color='white')
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("<div class='chart-title'>Urgency Levels</div>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(8, 6), facecolor='#1E2530')
        ax.set_facecolor('#1E2530')
        
        urgency_counts = df['urgency'].value_counts().reindex(['High', 'Medium', 'Low'], fill_value=0)
        colors_urg = ['#A78BFA', '#A78BFA', '#A78BFA']
        
        bars = ax.bar(urgency_counts.index, urgency_counts.values, color=colors_urg, width=0.6)
        
        ax.set_xlabel('', fontsize=12, color='#8B949E')
        ax.set_ylabel('', fontsize=12, color='#8B949E')
        ax.tick_params(colors='#8B949E')
        ax.spines['bottom'].set_color('#30363D')
        ax.spines['left'].set_color('#30363D')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(False)
        
        st.pyplot(fig)
        plt.close()
    
    # Chart Row 2 - Department Workload
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='chart-title'>Routed Tickets Per Team</div>", unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(14, 4), facecolor='#1E2530')
    ax.set_facecolor('#1E2530')
    
    dept_counts = df['department'].value_counts()
    colors_dept = ['#10B981'] * len(dept_counts)
    
    bars = ax.barh(dept_counts.index, dept_counts.values, color=colors_dept)
    
    ax.set_xlabel('', fontsize=12, color='#8B949E')
    ax.set_ylabel('', fontsize=12, color='#8B949E')
    ax.tick_params(colors='#8B949E')
    ax.spines['bottom'].set_color('#30363D')
    ax.spines['left'].set_color('#30363D')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(False)
    
    st.pyplot(fig)
    plt.close()
    
    # Recent Tickets Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Search and filters
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        search_term = st.text_input("", placeholder="Search tickets...", label_visibility="collapsed")
    with col2:
        status_filter = st.selectbox("All Statuses", ["All Statuses", "Resolved", "Escalated"])
    with col3:
        urgency_filter = st.selectbox("All Urgencies", ["All Urgencies", "High", "Medium", "Low"])
    
    st.markdown("<div class='chart-title'>Recent Tickets</div>", unsafe_allow_html=True)
    
    # Filter tickets
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['user_query'].str.contains(search_term, case=False, na=False)]
    if status_filter != "All Statuses":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if urgency_filter != "All Urgencies":
        filtered_df = filtered_df[filtered_df['urgency'] == urgency_filter]
    
    recent_tickets = filtered_df.tail(5).sort_values('timestamp', ascending=False)
    
    for idx, ticket in recent_tickets.iterrows():
        # Urgency badge color
        urg_class = f"badge-{ticket['urgency'].lower()}"
        
        # Format timestamp
        timestamp = pd.to_datetime(ticket['timestamp']).strftime('%m/%d/%Y, %I:%M:%S %p')
        
        st.markdown(f"""
            <div class='ticket-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div class='ticket-id'>ID: {ticket['ticket_id']}</div>
                    <div style='color: #8B949E; font-size: 0.9rem;'>{timestamp}</div>
                </div>
                <div class='ticket-query'>"{ticket['user_query']}"</div>
                <div style='margin: 10px 0;'>
                    <span class='badge {urg_class}'>{ticket['urgency']} Urgency</span>
                    <span class='badge badge-routed'>{ticket['status']}</span>
                    <span class='badge badge-category'>{ticket['category']}</span>
                </div>
                <div style='margin-top: 15px;'>
                    <div style='color: white; font-weight: 600; margin-bottom: 5px;'>AI Suggested Fix:</div>
                    <div style='color: #C9D1D9;'>{ticket['solution'][:150]}...</div>
                </div>
                <div class='routed-to'>Routed To: {ticket['department']}</div>
            </div>
        """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div style='text-align: center; padding: 50px; color: #8B949E;'>
            <h2>📭 No tickets yet!</h2>
            <p>Submit your first issue from the Get Help page.</p>
        </div>
    """, unsafe_allow_html=True)
