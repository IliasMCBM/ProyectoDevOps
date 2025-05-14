import streamlit as st
import random
import time
import json
import os
import sys
import logging
import datetime
from functools import wraps
from RAG import ChatBot
from dotenv import load_dotenv

# Configure logging
def setup_logging():
    """Set up structured logging to stdout for ELK stack integration"""
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                "timestamp": datetime.datetime.now().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "logger": record.name
            }
            
            # Add exception info if available
            if record.exc_info:
                log_record["exception"] = self.formatException(record.exc_info)
                
            # Add extra fields if available
            if hasattr(record, "props"):
                log_record.update(record.props)
                
            return json.dumps(log_record)
    
    logger = logging.getLogger("chatbot")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers if any
    if logger.handlers:
        logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JsonFormatter())
    logger.addHandler(console_handler)
    
    return logger

# Setup logger
logger = setup_logging()

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded")

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
            error_msg = f"An error occurred: {str(e)}"
            st.error(error_msg)
            # Log the error with structured logging
            logger.error(error_msg, extra={
                "props": {
                    "function": func.__name__,
                    "error_type": type(e).__name__,
                    "args": str(args) if args else None
                }
            })
            return f"I apologize, but I've encountered an error. Please try again later."
    return wrapper

# Initialize the ChatBot
try:
    logger.info("Initializing ChatBot")
chat = ChatBot()
    health_status["components"]["faiss_index"] = "healthy" if chat.faiss_index else "unhealthy"
    logger.info("ChatBot initialized successfully", extra={
        "props": {"faiss_index_status": health_status["components"]["faiss_index"]}
    })
except Exception as e:
    error_msg = f"ERROR initializing ChatBot: {str(e)}"
    logger.error(error_msg, extra={
        "props": {
            "error_type": type(e).__name__
        }
    })
    health_status["status"] = "degraded"
    health_status["components"]["faiss_index"] = "unhealthy"
    chat = None

@handle_errors
def response_generator(userInput, botContext):
    # First verify the GROQ API is configured
    if not os.environ.get("GROQ_API_KEY"):
        health_status["components"]["groq_api"] = "unconfigured"
        logger.error("GROQ_API_KEY environment variable not set", extra={
            "props": {"component": "groq_api"}
        })
        raise ValueError("GROQ_API_KEY environment variable not set.")
    
    # Log the query (being careful not to log sensitive information)
    logger.info("Processing query", extra={
        "props": {
            "query_length": len(userInput) if userInput else 0,
            "has_context": bool(botContext)
        }
    })
    
    # Update the health status for Groq API
    try:
        logger.info("Calling Groq API")
    response = chat.llamaResponse(userInput)
        health_status["components"]["groq_api"] = "healthy"
        logger.info("Received response from Groq API", extra={
            "props": {"response_length": len(response) if response else 0}
        })
    for word in response.split():
        yield word + " "
        time.sleep(0.05)
    except Exception as e:
        health_status["components"]["groq_api"] = "unhealthy"
        logger.error(f"Error calling Groq API: {str(e)}", extra={
            "props": {
                "error_type": type(e).__name__,
                "component": "groq_api"
            }
        })
        raise e

# Add health check endpoint using Streamlit's URL parameters
if "health-check" in st.experimental_get_query_params():
    # Update uptime
    update_uptime()
    
    # If any component is unhealthy, set overall status to degraded
    if "unhealthy" in health_status["components"].values() or "unconfigured" in health_status["components"].values():
        health_status["status"] = "degraded"
    
    # Log health check
    logger.info("Health check requested", extra={
        "props": {
            "health_status": health_status,
            "uptime_seconds": health_status["uptime_seconds"]
        }
    })
    
    # Display health status in a pretty format
    st.title("Health Check")
    st.json(health_status)
    st.stop()  # Stop further rendering

# Main chatbot UI
logger.info("Rendering main UI")
st.title("Chat DeNexus")

# Check if the FAISS index was loaded successfully
if health_status["components"]["faiss_index"] == "unhealthy":
    error_msg = "Unable to load the FAISS index. Please check the server logs."
    logger.error(error_msg, extra={
        "props": {"component": "faiss_index"}
    })
    st.error(error_msg)
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    logger.info("Initialized empty message history")

# Display message history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("What do you want to ask?", key=2):
    # Log that we received a new message (without logging the content)
    logger.info("Received new user message", extra={
        "props": {"message_length": len(prompt)}
    })
    
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(prompt, ""))
        logger.info("Response generated and displayed", extra={
            "props": {"response_length": len(response) if response else 0}
        })
    
    # Add assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})
