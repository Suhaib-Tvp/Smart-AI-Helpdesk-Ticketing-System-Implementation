"""Smart AI Helpdesk - Get Help Page."""
import streamlit as st
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import utilities
try:
    from utils import GroqClient, TicketManager, KnowledgeBase
except ImportError as e:
    st.error(f"❌ Failed to import required modules: {e}")
    st.stop()

from dotenv import load_dotenv
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart AI Helpdesk - Get Help",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark theme CSS matching your screenshots
st.markdown("""
    <style>
    /* Dark theme */
    .stApp {
        background-color: #0E1117;
    }
    
    /* Top navigation bar */
    .top-nav {
        background-color: #1E2530;
        padding: 15px 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    .logo-text {
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Main header */
    .main-header {
        text-align: center;
        color: white;
        margin: 40px 0;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .main-header p {
        color: #8B949E;
        font-size: 1.1rem;
    }
    
    /* Textarea styling */
    .stTextArea textarea {
        background-color: #262D3A !important;
        color: white !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        font-size: 1rem !important;
        padding: 15px !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #6366F1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 30px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100%;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #4F46E5 !important;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.4) !important;
    }
    
    /* Quick issue buttons */
    .quick-btn {
        background-color: #262D3A !important;
        color: #8B949E !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
    }
    
    .quick-btn:hover {
        background-color: #30363D !important;
        color: white !important;
        border-color: #6366F1 !important;
    }
    
    /* Or text */
    .or-text {
        text-align: center;
        color: #8B949E;
        margin: 20px 0;
        font-size: 1rem;
    }
    
    /* Common issues section */
    .common-issues {
        text-align: center;
        margin-top: 30px;
    }
    
    .common-issues p {
        color: #8B949E;
        margin-bottom: 15px;
    }
    
    /* Results card */
    .result-card {
        background-color: #1E2530;
        border-radius: 10px;
        padding: 25px;
        margin: 20px 0;
        border: 1px solid #30363D;
    }
    
    /* Metric styling */
    div[data-testid="stMetricValue"] {
        color: white !important;
        font-size: 1.5rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #8B949E !important;
    }
    
    /* Success/Info boxes */
    .stSuccess, .stInfo {
        background-color: #1E2530 !important;
        border-left: 4px solid #6366F1 !important;
        color: white !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# Top Navigation Bar
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
            st.rerun()
    with col_b:
        if st.button("Dashboard", key="nav_dash", use_container_width=True, type="primary"):
            st.switch_page("pages/dashboard.py")

st.markdown("<br>", unsafe_allow_html=True)

# Main Content
st.markdown("""
    <div class='main-header'>
        <h1>🤖 AI-Powered Help Center</h1>
        <p>Describe your issue to get an instant solution.</p>
    </div>
""", unsafe_allow_html=True)

# Text input area
user_query = st.text_area(
    "",
    height=150,
    placeholder="e.g., 'My laptop won't connect to WiFi and I've already tried restarting it.'",
    key="user_input",
    label_visibility="collapsed"
)

# Analyze button
if st.button("🔍 Get AI Help", type="primary", use_container_width=True):
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
                st.rerun()

# Or text
st.markdown("<div class='or-text'>Or, select a common issue:</div>", unsafe_allow_html=True)

# Common issue buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("📧 I can't log in to my email account.", key="issue1", use_container_width=True):
        st.session_state.current_analysis = None
        user_query = "I can't log in to my email account."
        analysis = st.session_state.groq_client.analyze_ticket(user_query)
        if analysis:
            st.session_state.current_analysis = {'user_query': user_query, **analysis}
            st.rerun()
    
    if st.button("🌐 The Wi-Fi is slow or disconnecting frequently.", key="issue3", use_container_width=True):
        user_query = "The Wi-Fi is slow or disconnecting frequently."
        analysis = st.session_state.groq_client.analyze_ticket(user_query)
        if analysis:
            st.session_state.current_analysis = {'user_query': user_query, **analysis}
            st.rerun()

with col2:
    if st.button("🖨️ My printer is not working.", key="issue2", use_container_width=True):
        user_query = "My printer is not working."
        analysis = st.session_state.groq_client.analyze_ticket(user_query)
        if analysis:
            st.session_state.current_analysis = {'user_query': user_query, **analysis}
            st.rerun()
    
    if st.button("🐌 My computer is running very slowly.", key="issue4", use_container_width=True):
        user_query = "My computer is running very slowly."
        analysis = st.session_state.groq_client.analyze_ticket(user_query)
        if analysis:
            st.session_state.current_analysis = {'user_query': user_query, **analysis}
            st.rerun()

if st.button("📁 I need to request access to a shared folder.", key="issue5", use_container_width=True):
    user_query = "I need to request access to a shared folder."
    analysis = st.session_state.groq_client.analyze_ticket(user_query)
    if analysis:
        st.session_state.current_analysis = {'user_query': user_query, **analysis}
        st.rerun()

# Display results if analysis exists
if st.session_state.current_analysis:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    analysis = st.session_state.current_analysis
    
    # Results header
    st.markdown("### ✅ Analysis Complete!")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_icons = {
            'Software': '🖥️',
            'Hardware': '💻',
            'Network': '🌐',
            'Login/Access': '🔐',
            'Other': '📋'
        }
        st.metric("Category", f"{category_icons.get(analysis['category'], '📋')} {analysis['category']}")
    
    with col2:
        urgency_colors = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
        st.metric("Urgency", f"{urgency_colors.get(analysis['urgency'], '🟢')} {analysis['urgency']}")
    
    with col3:
        st.metric("AI Confidence", f"{analysis.get('confidence', 0.95) * 100:.0f}%")
    
    # Solution
    st.markdown("### 💡 AI Suggested Fix:")
    st.info(analysis['solution'])
    
    # Department routing
    st.markdown(f"**🏢 Routed To:** {analysis['department']}")
    
    # Action buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Mark as Resolved", use_container_width=True):
            ticket_data = st.session_state.current_analysis.copy()
            ticket_data['status'] = 'Resolved'
            ticket_data['resolved_by'] = 'AI'
            ticket_id = st.session_state.ticket_manager.save_ticket(ticket_data)
            st.success(f"🎉 Ticket {ticket_id} saved!")
            st.session_state.current_analysis = None
            st.rerun()
    
    with col2:
        if st.button("📤 Escalate to Support", use_container_width=True):
            ticket_data = st.session_state.current_analysis.copy()
            ticket_data['status'] = 'Escalated'
            ticket_data['resolved_by'] = 'Escalated'
            ticket_id = st.session_state.ticket_manager.save_ticket(ticket_data)
            st.success(f"📨 Ticket {ticket_id} escalated to {ticket_data['department']}!")
            st.session_state.current_analysis = None
            st.rerun()
