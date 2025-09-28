import streamlit as st
import requests
import json
import time

# --- Configuration ---
# The URL of your backend API.
# This app assumes your backend has an endpoint at "/chat" that accepts a POST request.
BACKEND_URL = "http://localhost:8000"

# --- Streamlit UI ---
st.set_page_config(page_title="Streamlit Chat with Strands Agent API", layout="centered")
st.title("🔗 Chat with your Local AI Agent")

user = st.text_input("User Name")

# Initialize chat history in Streamlit's session state
# This ensures messages persist across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages ---
# Loop through the messages and display them in the chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
# This block is executed when the user sends a message
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display the user message immediately in the chat bubble
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display a loading message while waiting for the backend response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

    try:
        # Prepare the data to be sent to the backend
        payload = {"question": prompt, "session_id": user}
        
        # Send a POST request to the backend's /chat endpoint
        # You may need to adjust the timeout based on your backend's performance
        response = requests.post(f"{BACKEND_URL}/question", json=payload, timeout=60)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        response_json = response.json()["content"]
    

        # Update the placeholder with the actual backend response
        message_placeholder.markdown(response_json[0]["text"])
        
        for messages in response_json:
            # Add the assistant's response to the chat history
            st.session_state.messages.append({"role": "assistant", "content": messages["text"]})
        
    except requests.exceptions.RequestException as e:
        # Handle connection errors or bad status codes
        error_message = f"Error connecting to backend: {e}"
        st.error(error_message)
        # Update the placeholder to show the error
        message_placeholder.markdown(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Rerun the app to clear the input box and update the display
    st.rerun()