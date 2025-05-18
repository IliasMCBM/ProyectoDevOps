#!/bin/bash

echo "DeNexus Chatbot - Cybersecurity Assistant"
echo "========================================="

# First activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✅ Activating existing virtual environment..."
    source venv/bin/activate
else
    echo "🔧 Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists, if not create it with prompt
if [ ! -f .env ]; then
    echo "🔑 No .env file found. Creating one..."
    echo "Please enter your GROQ API key:"
    read -s groq_key
    echo "GROQ_API_KEY=$groq_key" > .env
    echo "✅ .env file created."
else
    echo "✅ .env file found."
fi

# Check if FAISS index exists
if [ ! -d "faiss_index" ] || [ -z "$(ls -A faiss_index)" ]; then
    echo "🔎 FAISS index not found or empty. Building index..."
    mkdir -p faiss_index
    python build_index.py
    echo "✅ FAISS index built successfully."
else
    # Check if we need to rebuild the index
    if [ "$1" == "--rebuild-index" ]; then
        echo "🔄 Rebuilding FAISS index..."
        mkdir -p faiss_index
        python build_index.py
        echo "✅ FAISS index rebuilt successfully."
    else
        echo "✅ Using existing FAISS index."
    fi
fi

# Start the Streamlit app in the foreground
echo "🚀 Starting Streamlit app..."
echo "========================================="
echo "Press Ctrl+C to stop the application"
echo "========================================="
streamlit run botInterface.py 