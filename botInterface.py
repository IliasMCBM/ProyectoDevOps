import streamlit as st
import random
import time
import json
import os
import sys
from functools import wraps
from RAG import ChatBot
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Health status tracking
health_status = {
    "status": "healthy",
    "components": {
        "faiss_index": "unknown",
        "groq_api": "unknown"
    },
    "startup_time": time.time(),
    "uptime_seconds": 0
}

def update_uptime():
    """Update the uptime in the health status"""
    health_status["uptime_seconds"] = int(time.time() - health_status["startup_time"])

# Error handling decorator
def handle_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            # Log the error for debugging
            print(f"ERROR in {func.__name__}: {str(e)}", file=sys.stderr)
            return f"I apologize, but I've encountered an error. Please try again later."
    return wrapper

# Initialize the ChatBot
try:
    chat = ChatBot()
    health_status["components"]["faiss_index"] = "healthy" if chat.faiss_index else "unhealthy"
except Exception as e:
    print(f"ERROR initializing ChatBot: {str(e)}", file=sys.stderr)
    health_status["status"] = "degraded"
    health_status["components"]["faiss_index"] = "unhealthy"
    chat = None

@handle_errors
def response_generator(userInput, botContext):
    # First verify the GROQ API is configured
    if not os.environ.get("GROQ_API_KEY"):
        health_status["components"]["groq_api"] = "unconfigured"
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    # Update the health status for Groq API
    try:
        response = chat.llamaResponse(userInput)
        health_status["components"]["groq_api"] = "healthy"
        for word in response.split():
            yield word + " "
            time.sleep(0.05)
    except Exception as e:
        health_status["components"]["groq_api"] = "unhealthy"
        raise e

# Add health check endpoint using Streamlit's URL parameters
if "health-check" in st.experimental_get_query_params():
    # Update uptime
    update_uptime()
    
    # If any component is unhealthy, set overall status to degraded
    if "unhealthy" in health_status["components"].values() or "unconfigured" in health_status["components"].values():
        health_status["status"] = "degraded"
    
    # Display health status in a pretty format
    st.title("Health Check")
    st.json(health_status)
    st.stop()  # Stop further rendering

# Main chatbot UI
st.title("Chat DeNexus")

# Check if the FAISS index was loaded successfully
if health_status["components"]["faiss_index"] == "unhealthy":
    st.error("Unable to load the FAISS index. Please check the server logs.")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("What do you want to ask?", key=2):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt, ""))
    
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
