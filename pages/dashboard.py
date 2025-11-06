"""Dashboard Page - Analytics and Ticket Overview."""
import streamlit as st
import sys
import os
import matplotlib.pyplot as plt

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import TicketManager, AnalyticsDashboard

st.set_page_config(
    page_title="Dashboard", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsDashboard()

# Header
st.title("📊 Helpdesk Dashboard")
st.markdown("Real-time analytics and ticket management")

# Sidebar with stats
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/dashboard.png", width=80)
    st.title("Quick Stats")
    st.markdown("---")
    
    stats = st.session_state.ticket_manager.get_statistics()
    st.metric("Total Tickets", stats['total_tickets'])
    st.metric("AI Resolved", stats['ai_resolved'])
    st.metric("Escalated", stats['escalated'])
    st.metric("Resolution Rate", f"{stats['resolution_rate']:.1f}%")

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
        help="Tickets escalated to human support"
    )

with col4:
    st.metric(
        "Avg Confidence",
        f"{stats['avg_confidence']:.1%}",
        help="Average AI confidence score"
    )

if not df.empty:
    st.markdown("---")
    
    # Charts Row 1
    st.subheader("📊 Visual Analytics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🏷️ Category Distribution")
        fig, ax = st.session_state.analytics.create_category_distribution(df)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("##### ⚠️ Urgency Levels")
        fig, ax = st.session_state.analytics.create_urgency_distribution(df)
        st.pyplot(fig)
        plt.close()
    
    st.markdown("---")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🏢 Department Workload")
        fig, ax = st.session_state.analytics.create_department_workload(df)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("##### 📈 Ticket Timeline")
        fig, ax = st.session_state.analytics.create_resolution_timeline(df)
        st.pyplot(fig)
        plt.close()
    
    # Recent Tickets
    st.markdown("---")
    st.subheader("🎫 Recent Tickets")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.multiselect(
            "Filter by Category",
            options=df['category'].unique().tolist(),
            default=df['category'].unique().tolist()
        )
    
    with col2:
        urgency_filter = st.multiselect(
            "Filter by Urgency",
            options=['High', 'Medium', 'Low'],
            default=df['urgency'].unique().tolist()
        )
    
    with col3:
        status_filter = st.multiselect(
            "Filter by Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist()
        )
    
    # Apply filters
    filtered_df = df[
        (df['category'].isin(category_filter)) &
        (df['urgency'].isin(urgency_filter)) &
        (df['status'].isin(status_filter))
    ]
    
    recent_df = filtered_df.tail(10).sort_values('timestamp', ascending=False)
    
    st.dataframe(
        recent_df[['ticket_id', 'timestamp', 'category', 'urgency', 'status', 'user_query', 'department']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "ticket_id": st.column_config.TextColumn("Ticket ID", width="small"),
            "timestamp": st.column_config.DatetimeColumn("Time", width="medium", format="DD/MM/YYYY HH:mm"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "urgency": st.column_config.TextColumn("Urgency", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "user_query": st.column_config.TextColumn("Issue", width="large"),
            "department": st.column_config.TextColumn("Department", width="medium"),
        }
    )
    
    # Export options
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name="filtered_tickets.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        all_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All Tickets",
            data=all_csv,
            file_name="all_tickets.csv",
            mime="text/csv",
            use_container_width=True
        )

else:
    st.info("📭 No tickets yet! Go to the main page to submit your first ticket.")
    st.markdown("---")
    st.image("https://img.icons8.com/clouds/400/000000/ticket.png", width=200)

# Footer
st.markdown("---")
st.caption(f"📊 Dashboard last updated: {df['timestamp'].max() if not df.empty else 'No data'}")
