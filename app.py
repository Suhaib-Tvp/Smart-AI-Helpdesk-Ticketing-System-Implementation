import streamlit as st
from groq import Groq
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime
from enum import Enum
import os

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

def get_groq_client():
    """Initialize and return Groq client"""
    try:
        # Try Streamlit secrets first
        api_key = st.secrets.get("GROQ_API_KEY", None)
        
        # Fall back to environment variable
        if not api_key:
            api_key = os.environ.get("GROQ_API_KEY")
        
        if not api_key:
            st.error("⚠️ GROQ_API_KEY not found. Please set it in .streamlit/secrets.toml or as environment variable.")
            return None
            
        return Groq(api_key=api_key)
        
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        return None

def build_prompt(issue_text):
    """Build the prompt for Groq API"""
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
    """Analyze user issue using Groq API with Llama 3.3 70B"""
    client = get_groq_client()
    
    if not client:
        return None
        
    try:
        prompt = build_prompt(issue_text)
        
        # Create chat completion with Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert IT helpdesk agent. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=1024,
            top_p=0.9
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Clean the response (remove markdown code blocks if present)
        if response_text.startswith('```
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        analysis = json.loads(response_text)
        return analysis
        
    except json.JSONDecodeError as e:
        st.error(f"Error parsing AI response: {e}")
        st.error(f"Raw response: {response_text}")
        return None
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
            plt.xticks(rotation=45, ha='right')
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
