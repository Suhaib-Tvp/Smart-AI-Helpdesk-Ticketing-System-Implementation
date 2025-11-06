"""Analytics Dashboard Page."""
import streamlit as st
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import TicketManager, AnalyticsDashboard

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

# Custom CSS for dashboard
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsDashboard()

# Header with icon
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://img.icons8.com/color/96/000000/dashboard.png", width=80)
with col2:
    st.title("📊 Analytics Dashboard")
    st.markdown("Real-time insights into helpdesk performance")

st.markdown("---")

# Load data
df = st.session_state.ticket_manager.load_tickets()
stats = st.session_state.ticket_manager.get_statistics()

# KPI Metrics with enhanced styling
st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🎫 Total Tickets",
        value=stats['total_tickets'],
        delta=None,
        help="Total number of tickets submitted"
    )

with col2:
    st.metric(
        label="🤖 AI Resolved",
        value=stats['ai_resolved'],
        delta=f"+{stats['resolution_rate']:.1f}%",
        delta_color="normal",
        help="Tickets resolved by AI without escalation"
    )

with col3:
    st.metric(
        label="📤 Escalated",
        value=stats['escalated'],
        delta=f"{stats['escalated'] - stats['ai_resolved']}" if stats['ai_resolved'] > 0 else None,
        delta_color="inverse",
        help="Tickets escalated to human support"
    )

with col4:
    st.metric(
        label="🎯 Avg Confidence",
        value=f"{stats['avg_confidence']:.1%}",
        delta=None,
        help="Average AI confidence score"
    )

# Additional insights
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if stats['total_tickets'] > 0:
        efficiency = (stats['ai_resolved'] / stats['total_tickets']) * 100
        st.metric(
            label="⚡ Automation Efficiency",
            value=f"{efficiency:.1f}%",
            help="Percentage of tickets handled by AI"
        )

with col2:
    if df.empty is False:
        avg_per_day = len(df) / max(df['timestamp'].nunique() if 'timestamp' in df.columns else 1, 1)
        st.metric(
            label="📊 Daily Average",
            value=f"{avg_per_day:.1f}",
            help="Average tickets per day"
        )

with col3:
    if not df.empty and 'category' in df.columns:
        most_common = df['category'].mode()[0] if len(df['category'].mode()) > 0 else "N/A"
        st.metric(
            label="🔝 Top Category",
            value=most_common,
            help="Most common issue category"
        )

# Visualizations
if not df.empty:
    st.markdown("---")
    st.subheader("📊 Visual Analytics")
    
    # Row 1: Category and Urgency
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏷️ Category Distribution")
        fig, ax = st.session_state.analytics.create_category_distribution(df)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("#### ⚠️ Urgency Levels")
        fig, ax = st.session_state.analytics.create_urgency_distribution(df)
        st.pyplot(fig)
        plt.close()
    
    # Row 2: Department and Timeline
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏢 Department Workload")
        fig, ax = st.session_state.analytics.create_department_workload(df)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.markdown("#### 📈 Ticket Timeline")
        fig, ax = st.session_state.analytics.create_resolution_timeline(df)
        st.pyplot(fig)
        plt.close()
    
    # Resolution breakdown
    st.markdown("---")
    st.subheader("🎯 Resolution Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Resolution pie chart
        fig, ax = plt.subplots(figsize=(8, 6))
        resolution_counts = df['resolved_by'].value_counts()
        colors = ['#4CAF50', '#FF6B6B', '#FFA726']
        ax.pie(resolution_counts.values, labels=resolution_counts.index, 
               autopct='%1.1f%%', startangle=90, colors=colors)
        ax.set_title('Resolution Method Distribution', fontsize=14, fontweight='bold')
        st.pyplot(fig)
        plt.close()
    
    with col2:
        # Urgency by category
        fig, ax = plt.subplots(figsize=(8, 6))
        urgency_category = df.groupby(['category', 'urgency']).size().unstack(fill_value=0)
        urgency_category.plot(kind='bar', stacked=True, ax=ax, 
                            color=['#4CAF50', '#FFA500', '#FF6B6B'])
        ax.set_xlabel('Category', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Tickets', fontsize=12, fontweight='bold')
        ax.set_title('Urgency Distribution by Category', fontsize=14, fontweight='bold')
        ax.legend(title='Urgency', labels=['Low', 'Medium', 'High'])
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    # Recent tickets table
    st.markdown("---")
    st.subheader("🕒 Recent Tickets")
    
    recent_df = df.tail(10).sort_values('timestamp', ascending=False)
    
    # Style the dataframe
    styled_df = recent_df[['ticket_id', 'timestamp', 'category', 'urgency', 'status', 'resolved_by']].copy()
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ticket_id": st.column_config.TextColumn("Ticket ID", width="small"),
            "timestamp": st.column_config.DatetimeColumn("Time", width="medium", format="DD/MM/YY HH:mm"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "urgency": st.column_config.TextColumn("Urgency", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "resolved_by": st.column_config.TextColumn("Resolved By", width="small"),
        }
    )
    
    # Export options
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All Data (CSV)",
            data=csv,
            file_name=f"helpdesk_analytics_{st.session_state.ticket_manager.load_tickets()['timestamp'].max() if not df.empty else 'empty'}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()
    
else:
    st.info("📭 No tickets yet! Submit your first issue from the main page to see analytics.")
    st.markdown("---")
    st.image("https://img.icons8.com/clouds/400/000000/ticket.png", width=200)
    st.markdown("### Get Started")
    st.write("Navigate to the main page using the sidebar to submit your first ticket!")

# Footer
st.markdown("---")
st.caption("📊 Dashboard updates in real-time as new tickets are submitted | Last updated: " + 
          st.session_state.ticket_manager.load_tickets()['timestamp'].max() if not df.empty else "No data")
