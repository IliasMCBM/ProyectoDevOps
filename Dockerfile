# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables for default paths within the image
# These can still be overridden by --env flags in `docker run` if RAG.py logic allows
ENV PYTHONUNBUFFERED=1 \
    APP_PORT=8501 \
    DATA_PATH=/app/data \
    FAISS_INDEX_PATH=/app/faiss_index

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code and data into the container at /app
COPY . .

# Create the directory for the FAISS index if it doesn't exist (it shouldn't yet)
# and ensure the build script can write to it.
RUN mkdir -p $FAISS_INDEX_PATH && chmod -R 755 $FAISS_INDEX_PATH

# Run the build script to generate the FAISS index
# This is part of the image build process
RUN python build_index.py

# Make port ${APP_PORT} available to the world outside this container
EXPOSE ${APP_PORT}

# Define the command to run your app using streamlit
# The server will bind to 0.0.0.0 to be accessible from outside the container
CMD ["streamlit", "run", "botInterface.py", "--server.port", "${APP_PORT}", "--server.address", "0.0.0.0"] 