import streamlit as st
from phi.agent import Agent
from phi.tools.hackernews import HackerNews
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.llm import LLM
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="HackerNews Insights",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'article' not in st.session_state:
    st.session_state.article = None

# Main app interface
st.title("📰 HackerNews Insights Generator")
st.markdown("""
This app uses AI agents to analyze top stories from HackerNews and generate comprehensive summaries.
The agents search, read, and synthesize information from multiple sources.
""")

# API Key input
api_key = st.text_input("Enter your Gemini API Key:", type="password", value="AIzaSyCOMRugTZFUHkKrg3vxSMZlAQ_eugZz6so")

def initialize_agents(api_key):
    if not api_key:
        st.error("Please enter your Gemini API key")
        return None
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize custom LLM for Gemini
        llm = LLM(
            model="gemini-pro",  # Specify the model
            api_key=api_key,
            template_format="f-string",
            template="{instruction}\n{input}",
            stream=True,
            provider="google",  # Specify the provider
            base_url="https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        )
        
        # Initialize agents
        hn_researcher = Agent(
            name="HackerNews Researcher",
            role="Gets top stories from hackernews.",
            tools=[HackerNews()],
            llm=llm,
        )

        web_searcher = Agent(
            name="Web Searcher",
            role="Searches the web for information on a topic",
            tools=[DuckDuckGo()],
            add_datetime_to_instructions=True,
            llm=llm,
        )

        article_reader = Agent(
            name="Article Reader",
            role="Reads articles from URLs.",
            tools=[Newspaper4k()],
            llm=llm,
        )

        hn_team = Agent(
            name="Hackernews Team",
            team=[hn_researcher, web_searcher, article_reader],
            instructions=[
                "First, search hackernews for what the user is asking about.",
                "Then, ask the article reader to read the links for the stories to get more information.",
                "Important: you must provide the article reader with the links to read.",
                "Then, ask the web searcher to search for each story to get more information.",
                "Finally, provide a thoughtful and engaging summary.",
            ],
            show_tool_calls=True,
            markdown=True,
            llm=llm,
        )
        
        return hn_team
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None

def generate_article(num_stories, topic=None):
    """Generate article with progress tracking"""
    hn_team = initialize_agents(api_key)
    if not hn_team:
        return None
    
    try:
        query = f"Write an article about the top {num_stories} stories"
        if topic:
            query += f" related to {topic}"
        query += " on hackernews"
        
        with st.spinner("🤖 AI agents are analyzing HackerNews..."):
            response = hn_team.print_response(query, stream=True)
            return response
    except Exception as e:
        st.error(f"Error generating article: {str(e)}")
        return None

# User inputs
col1, col2 = st.columns(2)
with col1:
    num_stories = st.slider("Number of stories to analyze", 1, 5, 2)
with col2:
    topic = st.text_input("Optional: Focus on a specific topic", "")

# Generate button
if st.button("Generate Insights", type="primary"):
    st.session_state.processing = True
    st.session_state.article = generate_article(num_stories, topic)

# Display results
if st.session_state.article:
    st.success("✅ Analysis completed successfully!")
    with st.expander("📝 Generated Article", expanded=True):
        st.markdown(st.session_state.article)
    
    # Export options
    if st.download_button(
        label="Download Article",
        data=st.session_state.article,
        file_name="hackernews_insights.md",
        mime="text/markdown"
    ):
        st.toast("Article downloaded successfully!")

# Footer
st.markdown("---")
st.markdown("*Powered by Phi, Google Gemini, and Streamlit*")
