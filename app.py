import streamlit as st
import google.generativeai as genai
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
from enum import Enum
import io
import base64

# Page configuration
st.set_page_config(
    page_title="Smart AI Helpdesk",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .ticket-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .urgent-high {
        border-left: 5px solid #ff4b4b !important;
    }
    .urgent-medium {
        border-left: 5px solid #ffa64b !important;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class IssueCategory(Enum):
    SOFTWARE = "Software"
    HARDWARE = "Hardware"
    NETWORK = "Network"
    LOGIN_ACCESS = "Login/Access"
    OTHER = "Other"

class UrgencyLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TicketStatus(Enum):
    RESOLVED = "Resolved"
    ROUTED = "Routed"

# Initialize session state
if 'tickets_df' not in st.session_state:
    try:
        tickets_df = pd.read_csv('tickets.csv')
        st.session_state.tickets_df = tickets_df
    except FileNotFoundError:
        st.session_state.tickets_df = pd.DataFrame(columns=[
            'id', 'userQuery', 'category', 'urgency', 'suggestedFix', 
            'relevantArticles', 'status', 'routedTo', 'timestamp'
        ])

if 'current_analysis' not in st.session_state:
    st.session_state.current_analysis = None

# Knowledge Base
KNOWLEDGE_BASE = [
    {
        'id': 'KB001',
        'title': 'Troubleshooting Printer Connection Issues',
        'content': 'Check if printer is powered on and connected to network. Verify printer drivers are installed. Restart print spooler service.'
    },
    {
        'id': 'KB002', 
        'title': 'Resolving WiFi Connectivity Problems',
        'content': 'Restart router and device. Forget and reconnect to WiFi network. Update network drivers. Check for interference from other devices.'
    },
    {
        'id': 'KB003',
        'title': 'Password Reset and Account Recovery',
        'content': 'Use self-service password reset portal. Contact IT helpdesk for manual reset. Ensure account is not locked out.'
    },
    {
        'id': 'KB004',
        'title': 'Software Installation Guide',
        'content': 'Download from official company portal. Run as administrator. Disable antivirus temporarily during installation.'
    },
    {
        'id': 'KB005',
        'title': 'Email Configuration and Troubleshooting',
        'content': 'Verify server settings. Check internet connection. Clear application cache. Update email client software.'
    }
]

# Department mapping
DEPARTMENT_MAPPING = {
    "Software": "Software Support Team",
    "Hardware": "Hardware Support Team", 
    "Network": "Network Operations Team",
    "Login/Access": "Identity Management Team",
    "Other": "General IT Support"
}

def configure_gemini():
    """Configure Gemini API with Streamlit secrets"""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Failed to configure Gemini API: {e}")
        return False

def build_prompt(issue_text):
    """Build the prompt for Gemini API"""
    kb_string = "\n".join([
        f"{{ id: \"{a['id']}\", title: \"{a['title']}\", content: \"{a['content'][:200]}...\" }}" 
        for a in KNOWLEDGE_BASE
    ])
    
    return f"""You are an expert IT helpdesk agent. Your task is to analyze a user-submitted IT issue.

Knowledge Base:
{kb_string}

User Issue:
"{issue_text}"

Please analyze this issue and provide:
1. Category classification (Software, Hardware, Network, Login/Access, Other)
2. Urgency level (High, Medium, Low)
3. A single, concise initial troubleshooting step
4. Up to 3 relevant knowledge base article IDs from the provided list

Respond ONLY with valid JSON in this exact format:
{{
    "category": "Software|Hardware|Network|Login/Access|Other",
    "urgency": "High|Medium|Low", 
    "suggestedFix": "Brief actionable step starting with a verb",
    "relevantArticles": [
        {{"id": "KB001", "title": "Article Title"}},
        {{"id": "KB002", "title": "Article Title"}}
    ]
}}"""

def analyze_issue(issue_text):
    """Analyze user issue using Gemini API"""
    if not configure_gemini():
        return None
        
    try:
        # ------------------- THIS IS THE FIX -------------------
        model = genai.GenerativeModel('gemini-1.5-flash')
        # -------------------------------------------------------
        
        prompt = build_prompt(issue_text)
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean the response (remove markdown code blocks if present)
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        analysis = json.loads(response_text)
        return analysis
        
    except Exception as e:
        st.error(f"Error analyzing issue: {e}")
        return None

def save_ticket(user_query, analysis, status, routed_to=None):
    """Save ticket to CSV"""
    try:
        ticket_id = f"TKT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        new_ticket = {
            'id': ticket_id,
            'userQuery': user_query,
            'category': analysis['category'],
            'urgency': analysis['urgency'],
            'suggestedFix': analysis['suggestedFix'],
            'relevantArticles': json.dumps(analysis.get('relevantArticles', [])),
            'status': status,
            'routedTo': routed_to if routed_to else '',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add to DataFrame
        new_df = pd.DataFrame([new_ticket])
        st.session_state.tickets_df = pd.concat([st.session_state.tickets_df, new_df], ignore_index=True)
        
        # Save to CSV
        st.session_state.tickets_df.to_csv('tickets.csv', index=False)
        
        return ticket_id
        
    except Exception as e:
        st.error(f"Error saving ticket: {e}")
        return None

def display_dashboard():
    """Display analytics dashboard"""
    st.header("📊 Analytics Dashboard")
    
    if st.session_state.tickets_df.empty:
        st.info("No tickets available for analytics.")
        return
    
    df = st.session_state.tickets_df
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tickets = len(df)
        st.metric("Total Tickets", total_tickets)
    
    with col2:
        resolved_count = len(df[df['status'] == 'Resolved'])
        st.metric("AI Resolved", resolved_count)
    
    with col3:
        escalated_count = len(df[df['status'] == 'Routed'])
        st.metric("Escalated", escalated_count)
    
    with col4:
        if total_tickets > 0:
            resolution_rate = (resolved_count / total_tickets) * 100
            st.metric("AI Resolution Rate", f"{resolution_rate:.1f}%")
        else:
            st.metric("AI Resolution Rate", "0%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Issue Distribution")
        if not df.empty:
            category_counts = df['category'].value_counts()
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
    
    with col2:
        st.subheader("Urgency Levels")
        if not df.empty:
            urgency_counts = df['urgency'].value_counts()
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x=urgency_counts.index, y=urgency_counts.values, ax=ax, palette=['#ff4b4b', '#ffa64b', '#4bff4b'])
            ax.set_ylabel('Number of Tickets')
            plt.xticks(rotation=45)
            st.pyplot(fig)
    
    # Team Workload
    st.subheader("Team Workload Distribution")
    if not df.empty and 'routedTo' in df.columns:
        routed_df = df[df['status'] == 'Routed']
        if not routed_df.empty:
            team_counts = routed_df['routedTo'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=team_counts.index, y=team_counts.values, ax=ax)
            ax.set_ylabel('Number of Tickets')
            ax.set_xlabel('Support Team')
            plt.xticks(rotation=45)
            st.pyplot(fig)
        else:
            st.info("No escalated tickets to show team workload.")
    
    # Recent Tickets
    st.subheader("Recent Tickets")
    display_df = df.tail(10).copy()
    if not display_df.empty:
        # Format the display
        display_df = display_df[['id', 'userQuery', 'category', 'urgency', 'status', 'timestamp']]
        st.dataframe(display_df, use_container_width=True)

def main():
    # Main header
    st.markdown('<h1 class="main-header">🛠️ Smart AI Helpdesk Ticketing System</h1>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a page:", 
                               ["Get AI Help", "Analytics Dashboard", "View All Tickets"])
    
    if app_mode == "Get AI Help":
        render_help_interface()
    elif app_mode == "Analytics Dashboard":
        display_dashboard()
    elif app_mode == "View All Tickets":
        render_ticket_list()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("Powered by Google Gemini AI")

def render_help_interface():
    """Render the main help interface"""
    st.header("🤖 Get AI Help")
    
    # Common questions
    st.subheader("Common Issues")
    common_questions = {
        "Printer not working": "My office printer is not printing documents. It shows offline status.",
        "WiFi connection issues": "I cannot connect to the office WiFi network on my laptop.",
        "Password reset needed": "I forgot my password and need to reset it to access my email.",
        "Software installation": "I need help installing the new project management software.",
        "Email not syncing": "My email is not syncing properly on my mobile device."
    }
    
    cols = st.columns(3)
    for i, (title, question) in enumerate(common_questions.items()):
        with cols[i % 3]:
            if st.button(f"📌 {title}", use_container_width=True):
                st.session_state.user_query = question
    
    # User input
    st.subheader("Describe Your Issue")
    user_query = st.text_area(
        "Please describe your IT issue in detail:",
        value=st.session_state.get('user_query', ''),
        height=150,
        placeholder="Example: My computer won't turn on and makes a beeping sound when I press the power button..."
    )
    
    if st.button("🚀 Get AI Help", type="primary", use_container_width=True):
        if not user_query.strip():
            st.error("Please describe your issue before requesting help.")
            return
        
        with st.spinner("🤔 AI is analyzing your issue..."):
            analysis = analyze_issue(user_query)
            
        if analysis:
            st.session_state.current_analysis = analysis
            st.session_state.current_user_query = user_query
            
            # Display analysis results
            st.success("✅ AI Analysis Complete!")
            
            # Create a nice card for the analysis
            urgency_class = ""
            if analysis['urgency'] == 'High':
                urgency_class = "urgent-high"
            elif analysis['urgency'] == 'Medium':
                urgency_class = "urgent-medium"
            
            st.markdown(f'<div class="ticket-card {urgency_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Category", analysis['category'])
                st.metric("Suggested Fix", analysis['suggestedFix'])
            with col2:
                st.metric("Urgency Level", analysis['urgency'])
            
            # Display relevant articles
            if analysis.get('relevantArticles'):
                st.subheader("📚 Relevant Knowledge Base Articles")
                for article in analysis['relevantArticles']:
                    # Find article details
                    kb_article = next((a for a in KNOWLEDGE_BASE if a['id'] == article['id']), None)
                    if kb_article:
                        with st.expander(f"📖 {article['title']}"):
                            st.write(kb_article['content'])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Resolution buttons
            st.subheader("Next Steps")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Yes, it's resolved!", use_container_width=True, type="primary"):
                    ticket_id = save_ticket(
                        user_query, 
                        analysis, 
                        "Resolved"
                    )
                    if ticket_id:
                        st.success(f"✅ Ticket {ticket_id} marked as resolved!")
                        st.balloons()
                        st.session_state.current_analysis = None
                        st.session_state.user_query = ""
            
            with col2:
                if st.button("❌ No, escalate to Helpdesk", use_container_width=True):
                    routed_to = DEPARTMENT_MAPPING.get(analysis['category'], "General IT Support")
                    ticket_id = save_ticket(
                        user_query,
                        analysis,
                        "Routed",
                        routed_to
                    )
                    if ticket_id:
                        st.success(f"📋 Ticket {ticket_id} escalated to {routed_to}!")
                        st.session_state.current_analysis = None
                        st.session_state.user_query = ""

def render_ticket_list():
    """Render all tickets view"""
    st.header("📋 All Tickets")
    
    if st.session_state.tickets_df.empty:
        st.info("No tickets created yet.")
        return
    
    df = st.session_state.tickets_df
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + list(df['status'].unique()))
    with col2:
        category_filter = st.selectbox("Filter by Category", ["All"] + list(df['category'].unique()))
    with col3:
        urgency_filter = st.selectbox("Filter by Urgency", ["All"] + list(df['urgency'].unique()))
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if urgency_filter != "All":
        filtered_df = filtered_df[filtered_df['urgency'] == urgency_filter]
    
    # Display tickets
    st.subheader(f"Tickets ({len(filtered_df)} found)")
    
    for _, ticket in filtered_df.iterrows():
        urgency_class = ""
        if ticket['urgency'] == 'High':
            urgency_class = "urgent-high"
        elif ticket['urgency'] == 'Medium':
            urgency_class = "urgent-medium"
        
        st.markdown(f'<div class="ticket-card {urgency_class}">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**Ticket ID:** {ticket['id']}")
            st.write(f"**Issue:** {ticket['userQuery']}")
            st.write(f"**Suggested Fix:** {ticket['suggestedFix']}")
        with col2:
            st.write(f"**Category:** {ticket['category']}")
            st.write(f"**Urgency:** {ticket['urgency']}")
        with col3:
            st.write(f"**Status:** {ticket['status']}")
            if ticket['status'] == 'Routed':
                st.write(f"**Routed To:** {ticket['routedTo']}")
            st.write(f"**Created:** {ticket['timestamp']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Download option
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Tickets as CSV",
        data=csv,
        file_name="filtered_tickets.csv",
        mime="text/csv",
        use_container_width=True
    )

if __name__ == "__main__":
    main()
