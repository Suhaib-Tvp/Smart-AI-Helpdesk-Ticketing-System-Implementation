def __init__(self):
    """Initialize Groq client with API key from environment or secrets."""
    api_key = None
    
    # Try Streamlit secrets first (for deployment)
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variable (for local development)
        api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Please add it to:\n"
            "- Streamlit Cloud: Settings → Secrets\n"
            "- Local: .env file"
        )
    
    try:
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
    except Exception as e:
        raise ValueError(f"Failed to initialize Groq client: {str(e)}")
