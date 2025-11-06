"""Dashboard Page - Analytics and Ticket Overview."""
import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import TicketManager, AnalyticsDashboard

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Initialize
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsDashboard()

# Header
st.title("📊 Helpdesk Dashboard")
st.markdown("Real-time analytics and ticket management")

# Load data
df = st.session_state.ticket_manager.load_tickets()
stats = st.session_state.ticket_manager.get_statistics()

# KPI Metrics
st.subheader("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", stats['total_tickets'])

with col2:
    st.metric("AI Resolved", stats['ai_resolved'], 
             delta=f"{stats['resolution_rate']:.1f}%")

with col3:
    st.metric("Escalated", stats['escalated'])

with col4:
    st.metric("Avg Confidence", f"{stats['avg_confidence']:.1%}")

if not df.empty:
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏷️ Issue Types")
        fig, ax = st.session_state.analytics.create_category_distribution(df)
        st.pyplot(fig)
    
    with col2:
        st.subheader("⚠️ Urgency Levels")
        fig, ax = st.session_state.analytics.create_urgency_distribution(df)
        st.pyplot(fig)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Department Workload")
        fig, ax = st.session_state.analytics.create_department_workload(df)
        st.pyplot(fig)
    
    with col2:
        st.subheader("📈 Timeline")
        fig, ax = st.session_state.analytics.create_resolution_timeline(df)
        st.pyplot(fig)
    
    # Recent Tickets
    st.markdown("---")
    st.subheader("🎫 Recent Tickets")
    
    recent_df = df.tail(10).sort_values('timestamp', ascending=False)
    
    st.dataframe(
        recent_df[['ticket_id', 'timestamp', 'category', 'urgency', 'status', 'user_query', 'department']],
        use_container_width=True,
        hide_index=True
    )
    
    # Export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download All Tickets (CSV)",
        data=csv,
        file_name="tickets.csv",
        mime="text/csv"
    )

else:
    st.info("📭 No tickets yet! Go to the Get Help page to submit your first ticket.")
