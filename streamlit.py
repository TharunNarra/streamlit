import streamlit as st
import requests

# Set up the Gemini API Key (replace 'your_gemini_api_key' with the actual key)
GEMINI_API_KEY = "AIzaSyCOMRugTZFUHkKrg3vxSMZlAQ_eugZz6so"
GEMINI_API_URL = "https://api.gemini.example/v1/chat"

# Streamlit UI
st.title("Streamlit Chat Application")
st.subheader("Powered by Gemini API")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    role, text = msg
    if role == "user":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**AI:** {text}")

# User input
user_input = st.text_input("Enter your message:", "", key="user_input")

if st.button("Send"):
    if user_input.strip():
        # Add user message to the chat history
        st.session_state.messages.append(("user", user_input))

        # Send the user message to the Gemini API
        try:
            response = requests.post(
                GEMINI_API_URL,
                headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
                json={"message": user_input}
            )
            response_data = response.json()

            if response.status_code == 200:
                ai_response = response_data.get("reply", "Sorry, I couldn't process that.")
            else:
                ai_response = f"Error: {response_data.get('error', 'Unknown error')}"
        except Exception as e:
            ai_response = f"Error: {str(e)}"

        # Add AI response to the chat history
        st.session_state.messages.append(("ai", ai_response))

        # Clear the input field
        st.session_state.user_input = ""

# Note for the user
st.markdown("---")
st.info("Messages are processed using the Gemini API. Ensure your API key is valid.")

