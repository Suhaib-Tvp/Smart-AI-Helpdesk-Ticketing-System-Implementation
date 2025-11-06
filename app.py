"""Smart AI Helpdesk Ticketing System - Main Application."""
import streamlit as st
from utils import GroqClient, TicketManager, KnowledgeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart AI Helpdesk",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #4CAF50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'groq_client' not in st.session_state:
    try:
        st.session_state.groq_client = GroqClient()
    except ValueError as e:
        st.error(f"⚠️ {e}")
        st.stop()

if 'ticket_manager' not in st.session_state:
    st.session_state.ticket_manager = TicketManager()

if 'knowledge_base' not in st.session_state:
    st.session_state.knowledge_base = KnowledgeBase()

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# Header
st.markdown('<div class="main-header">🎫 Smart AI Helpdesk System</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bot.png", width=80)
    st.title("Navigation")
    st.markdown("---")
    
    # Statistics
    stats = st.session_state.ticket_manager.get_statistics()
    st.metric("Total Tickets", stats['total_tickets'])
    st.metric("AI Resolution Rate", f"{stats['resolution_rate']:.1f}%")
    st.metric("Escalated", stats['escalated'])
    
    st.markdown("---")
    st.info("💡 **Tip**: Describe your IT issue clearly for best results!")

# Main content
st.header("🤖 Get AI-Powered Help")
st.write("Describe your IT issue below, and our AI will analyze it instantly!")

# Quick issue buttons
st.subheader("⚡ Quick Issue Selection")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🖥️ Software Issue"):
        st.session_state.quick_issue = "My application keeps crashing"
with col2:
    if st.button("💻 Hardware Problem"):
        st.session_state.quick_issue = "My computer won't turn on"
with col3:
    if st.button("🌐 Network Issue"):
        st.session_state.quick_issue = "I can't connect to the internet"
with col4:
    if st.button("🔐 Login Problem"):
        st.session_state.quick_issue = "I forgot my password"

# User input
user_query = st.text_area(
    "Describe your issue:",
    value=st.session_state.get('quick_issue', ''),
    height=150,
    placeholder="Example: My laptop screen is flickering and showing weird colors..."
)

# Analyze button
if st.button("🔍 Analyze Issue", type="primary"):
    if not user_query.strip():
        st.warning("⚠️ Please describe your issue first!")
    else:
        with st.spinner("🤖 AI is analyzing your issue..."):
            analysis = st.session_state.groq_client.analyze_ticket(user_query)
            
            if analysis:
                st.session_state.current_analysis = {
                    'user_query': user_query,
                    **analysis
                }
                
                # Display results
                st.success("✅ Analysis Complete!")
                
                # Results in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    category_colors = {
                        'Software': '🖥️',
                        'Hardware': '💻',
                        'Network': '🌐',
                        'Login/Access': '🔐',
                        'Other': '📋'
                    }
                    st.metric(
                        "Category",
                        f"{category_colors.get(analysis['category'], '📋')} {analysis['category']}"
                    )
                
                with col2:
                    urgency_colors = {
                        'High': '🔴',
                        'Medium': '🟡',
                        'Low': '🟢'
                    }
                    st.metric(
                        "Urgency",
                        f"{urgency_colors.get(analysis['urgency'], '🟢')} {analysis['urgency']}"
                    )
                
                with col3:
                    st.metric(
                        "Confidence",
                        f"{analysis.get('confidence', 0.95) * 100:.1f}%"
                    )
                
                # Solution
                st.markdown("### 💡 Suggested Solution")
                st.info(analysis['solution'])
                
                # Knowledge base articles
                if analysis.get('knowledge_base_articles'):
                    st.markdown("### 📚 Related Articles")
                    for article in analysis['knowledge_base_articles']:
                        st.markdown(f"- {article}")
                
                # Department routing
                st.markdown("### 🏢 Recommended Department")
                st.write(f"**{analysis['department']}**")
                
            else:
                st.error("❌ Failed to analyze ticket. Please try again.")

# Action buttons
if st.session_state.current_analysis:
    st.markdown("---")
    st.subheader("🎯 Next Steps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Mark as Resolved", use_container_width=True):
            ticket_data = st.session_state.current_analysis.copy()
            ticket_data['status'] = 'Resolved'
            ticket_data['resolved_by'] = 'AI'
            
            ticket_id = st.session_state.ticket_manager.save_ticket(ticket_data)
            
            st.success(f"🎉 Ticket {ticket_id} marked as resolved!")
            st.balloons()
            st.session_state.current_analysis = None
            st.rerun()
    
    with col2:
        if st.button("📤 Escalate to Team", use_container_width=True):
            ticket_data = st.session_state.current_analysis.copy()
            ticket_data['status'] = 'Escalated'
            ticket_data['resolved_by'] = 'Escalated'
            
            ticket_id = st.session_state.ticket_manager.save_ticket(ticket_data)
            
            st.success(f"📨 Ticket {ticket_id} escalated to {ticket_data['department']}!")
            st.session_state.current_analysis = None
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Powered by Groq API (Llama 3.3 70B) | Built with ❤️ using Streamlit"
    "</div>",
    unsafe_allow_html=True
)
