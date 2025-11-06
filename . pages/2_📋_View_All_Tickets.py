"""View All Tickets Page."""
import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import TicketManager

st.set_page_config(page_title="View All Tickets", page_icon="📋", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .ticket-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 10px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

# Header
col1, col2 = st.columns([1, 10])
with col1:
    st.image("https://img.icons8.com/color/96/000000/documents.png", width=80)
with col2:
    st.title("📋 All Tickets")
    st.markdown("View, filter, and manage all support tickets")

st.markdown("---")

# Load tickets
df = st.session_state.ticket_manager.load_tickets()

if not df.empty:
    # Summary statistics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Total", len(df))
    with col2:
        software_count = len(df[df['category'] == 'Software'])
        st.metric("🖥️ Software", software_count)
    with col3:
        hardware_count = len(df[df['category'] == 'Hardware'])
        st.metric("💻 Hardware", hardware_count)
    with col4:
        network_count = len(df[df['category'] == 'Network'])
        st.metric("🌐 Network", network_count)
    with col5:
        high_urgency = len(df[df['urgency'] == 'High'])
        st.metric("🔴 High Priority", high_urgency)
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filter Tickets")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        category_filter = st.multiselect(
            "📁 Category",
            options=df['category'].unique().tolist(),
            default=df['category'].unique().tolist()
        )
    
    with col2:
        urgency_filter = st.multiselect(
            "⚠️ Urgency",
            options=['High', 'Medium', 'Low'],
            default=df['urgency'].unique().tolist()
        )
    
    with col3:
        status_filter = st.multiselect(
            "✅ Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist()
        )
    
    with col4:
        resolved_filter = st.multiselect(
            "👤 Resolved By",
            options=df['resolved_by'].unique().tolist(),
            default=df['resolved_by'].unique().tolist()
        )
    
    # Apply filters
    filtered_df = df[
        (df['category'].isin(category_filter)) &
        (df['urgency'].isin(urgency_filter)) &
        (df['status'].isin(status_filter)) &
        (df['resolved_by'].isin(resolved_filter))
    ]
    
    # Search box
    st.markdown("---")
    search_term = st.text_input("🔎 Search in ticket descriptions:", placeholder="Type to search...")
    
    if search_term:
        filtered_df = filtered_df[filtered_df['user_query'].str.contains(search_term, case=False, na=False)]
    
    # Display count
    st.markdown(f"### 📋 Showing **{len(filtered_df)}** of **{len(df)}** tickets")
    
    # Sort options
    col1, col2 = st.columns([3, 1])
    with col2:
        sort_order = st.selectbox(
            "Sort by:",
            options=["Newest First", "Oldest First", "High Urgency First", "Category"]
        )
    
    # Apply sorting
    if sort_order == "Newest First":
        filtered_df = filtered_df.sort_values('timestamp', ascending=False)
    elif sort_order == "Oldest First":
        filtered_df = filtered_df.sort_values('timestamp', ascending=True)
    elif sort_order == "High Urgency First":
        urgency_order = {'High': 0, 'Medium': 1, 'Low': 2}
        filtered_df['urgency_rank'] = filtered_df['urgency'].map(urgency_order)
        filtered_df = filtered_df.sort_values('urgency_rank')
        filtered_df = filtered_df.drop('urgency_rank', axis=1)
    else:
        filtered_df = filtered_df.sort_values('category')
    
    # Data table with enhanced styling
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ticket_id": st.column_config.TextColumn(
                "Ticket ID",
                width="small",
                help="Unique ticket identifier"
            ),
            "timestamp": st.column_config.DatetimeColumn(
                "Created At",
                width="medium",
                format="DD/MM/YYYY HH:mm",
                help="Ticket creation timestamp"
            ),
            "category": st.column_config.TextColumn(
                "Category",
                width="small",
                help="Issue category"
            ),
            "urgency": st.column_config.TextColumn(
                "Urgency",
                width="small",
                help="Priority level"
            ),
            "status": st.column_config.TextColumn(
                "Status",
                width="small",
                help="Current status"
            ),
            "user_query": st.column_config.TextColumn(
                "Issue Description",
                width="large",
                help="User's problem description"
            ),
            "department": st.column_config.TextColumn(
                "Department",
                width="medium",
                help="Assigned department"
            ),
            "resolved_by": st.column_config.TextColumn(
                "Resolved By",
                width="small",
                help="Resolution method"
            ),
            "confidence": st.column_config.NumberColumn(
                "AI Confidence",
                width="small",
                format="%.2f",
                help="AI confidence score"
            ),
        }
    )
    
    # Detailed ticket viewer
    st.markdown("---")
    st.subheader("🔍 View Ticket Details")
    
    ticket_ids = filtered_df['ticket_id'].tolist()
    if ticket_ids:
        selected_ticket = st.selectbox("Select a ticket to view full details:", ticket_ids)
        
        if selected_ticket:
            ticket_data = st.session_state.ticket_manager.get_ticket_by_id(selected_ticket)
            
            if ticket_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Ticket ID:** {ticket_data['ticket_id']}")
                    st.markdown(f"**Category:** {ticket_data['category']}")
                    st.markdown(f"**Urgency:** {ticket_data['urgency']}")
                    st.markdown(f"**Status:** {ticket_data['status']}")
                
                with col2:
                    st.markdown(f"**Department:** {ticket_data['department']}")
                    st.markdown(f"**Resolved By:** {ticket_data['resolved_by']}")
                    st.markdown(f"**Confidence:** {ticket_data.get('confidence', 0):.2%}")
                    st.markdown(f"**Created:** {ticket_data['timestamp']}")
                
                st.markdown("---")
                st.markdown("**User Query:**")
                st.info(ticket_data['user_query'])
                
                st.markdown("**AI Solution:**")
                st.success(ticket_data['solution'])
    
    # Export and action buttons
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered (CSV)",
            data=csv,
            file_name="filtered_tickets.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        all_csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download All (CSV)",
            data=all_csv,
            file_name="all_tickets.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col4:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("app.py")
    
else:
    st.info("📭 No tickets found. Submit your first issue from the main page!")
    st.markdown("---")
    st.image("https://img.icons8.com/clouds/400/000000/nothing-found.png", width=300)
    
    if st.button("🏠 Go to Home Page", use_container_width=True):
        st.switch_page("app.py")

# Footer
st.markdown("---")
st.caption(f"📋 Total tickets in system: {len(df)} | Database: data/tickets.csv")
