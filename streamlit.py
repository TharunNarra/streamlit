import streamlit as st
import requests

# Set up the Gemini API Key (replace 'your_gemini_api_key' with the actual key)
GEMINI_API_KEY = "AIzaSyCOMRugTZFUHkKrg3vxSMZlAQ_eugZz6so"
GEMINI_API_URL = "https://api.gemini.example/v1/chat"

import streamlit as st
from phi.agent import Agent
from phi.tools.hackernews import HackerNews
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.model import Gemini

# Initialize the tools and agents
hn_researcher = Agent(
    name="HackerNews Researcher",
    role="Gets top stories from hackernews.",
    tools=[HackerNews()],
    model=Gemini(id="gemini-1.5-flash"),
)

web_searcher = Agent(
    name="Web Searcher",
    role="Searches the web for information on a topic",
    tools=[DuckDuckGo()],
    add_datetime_to_instructions=True,
    model=Gemini(id="gemini-1.5-flash"),
)

article_reader = Agent(
    name="Article Reader",
    role="Reads articles from URLs.",
    tools=[Newspaper4k()],
    model=Gemini(id="gemini-1.5-flash"),
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
    model=Gemini(id="gemini-1.5-flash"),
)

# Streamlit App
st.title("HackerNews Top Stories")

st.write("This app uses the `phi` library to retrieve and summarize the top stories on HackerNews.")

if st.button("Get Top Stories and Write an Article"):
    with st.spinner("Processing..."):
        response = hn_team.print_response("Write an article about the top 2 stories on hackernews", stream=True)
        st.success("Article generated successfully!")
        st.markdown(response)


