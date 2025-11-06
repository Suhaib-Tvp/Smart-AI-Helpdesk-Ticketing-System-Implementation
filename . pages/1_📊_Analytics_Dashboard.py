"""Analytics Dashboard Page."""
import streamlit as st
from utils import TicketManager, AnalyticsDashboard

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

# Initialize
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsDashboard()

# Header
st.title("📊 Analytics Dashboard")
st.markdown("Real-time insights into helpdesk performance")

# Load data
df = st.session_state.ticket_manager.load_tickets()
stats = st.session_state.ticket_manager.get_statistics()

# KPI Metrics
st.subheader("📈 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Tickets",
        stats['total_tickets'],
        delta=None,
        help="Total number of tickets submitted"
    )

with col2:
    st.metric(
        "AI Resolved",
        stats['ai_resolved'],
        delta=f"{stats['resolution_rate']:.1f}%",
        help="Tickets resolved by AI without escalation"
    )

with col3:
    st.metric(
        "Escalated",
        stats['escalated'],
        delta=None,
        help="Tickets escalated to human support"
    )

with col4:
    st.metric(
        "Avg Confidence",
        f"{stats['avg_confidence']:.1%}",
        delta=None,
        help="Average AI confidence score"
    )

# Visualizations
if not df.empty:
    st.markdown("---")
    st.subheader("📊 Ticket Distribution")
    
    # Row 1: Category and Urgency
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = st.session_state.analytics.create_category_distribution(df)
        st.pyplot(fig)
    
    with col2:
        fig, ax = st.session_state.analytics.create_urgency_distribution(df)
        st.pyplot(fig)
    
    # Row 2: Department and Timeline
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = st.session_state.analytics.create_department_workload(df)
        st.pyplot(fig)
    
    with col2:
        fig, ax = st.session_state.analytics.create_resolution_timeline(df)
        st.pyplot(fig)
    
    # Recent tickets table
    st.markdown("---")
    st.subheader("🕒 Recent Tickets")
    recent_df = df.tail(10).sort_values('timestamp', ascending=False)
    st.dataframe(
        recent_df[['ticket_id', 'timestamp', 'category', 'urgency', 'status']],
        use_container_width=True,
        hide_index=True
    )
    
else:
    st.info("📭 No tickets yet! Submit your first issue to see analytics.")

# Footer
st.markdown("---")
st.caption("Dashboard updates in real-time as new tickets are submitted")
