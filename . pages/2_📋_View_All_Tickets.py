"""View All Tickets Page."""
import streamlit as st
import pandas as pd
from utils import TicketManager

st.set_page_config(page_title="View All Tickets", page_icon="📋", layout="wide")

# Initialize
if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

# Header
st.title("📋 All Tickets")
st.markdown("View and manage all support tickets")

# Load tickets
df = st.session_state.ticket_manager.load_tickets()

if not df.empty:
    # Filters
    st.subheader("🔍 Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        category_filter = st.multiselect(
            "Category",
            options=df['category'].unique().tolist(),
            default=df['category'].unique().tolist()
        )
    
    with col2:
        urgency_filter = st.multiselect(
            "Urgency",
            options=df['urgency'].unique().tolist(),
            default=df['urgency'].unique().tolist()
        )
    
    with col3:
        status_filter = st.multiselect(
            "Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist()
        )
    
    with col4:
        resolved_filter = st.multiselect(
            "Resolved By",
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
    
    # Display count
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} tickets**")
    
    # Data table
    st.dataframe(
        filtered_df.sort_values('timestamp', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "ticket_id": st.column_config.TextColumn("Ticket ID", width="small"),
            "timestamp": st.column_config.DatetimeColumn("Time", width="medium"),
            "category": st.column_config.TextColumn("Category", width="small"),
            "urgency": st.column_config.TextColumn("Urgency", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
            "user_query": st.column_config.TextColumn("Issue", width="large"),
        }
    )
    
    # Export button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="helpdesk_tickets.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
else:
    st.info("📭 No tickets found. Submit your first issue from the main page!")

# Footer
st.markdown("---")
st.caption(f"Total tickets in system: {len(df)}")
