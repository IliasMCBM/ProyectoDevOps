# DeNexus_ChatBot-AI

This project is a chatbot built using Retrieval Augmented Generation (RAG).

## Project Structure

*(To be filled in)*

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd DeNexus_ChatBot-AI
    ```

2.  **Create and activate a virtual environment:** (Recommended)
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the project root by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Then, edit the `.env` file and add your `GROQ_API_KEY`, and optionally customize `DATA_PATH` and `FAISS_INDEX_PATH` if you don't want to use the defaults (`data/` and `faiss_index/` respectively).

5.  **Build the FAISS Index:** (Factor V: Build, release, run)
    Run the build script to generate the vector index from your data:
    ```bash
    python build_index.py
    ```
    This step reads from `DATA_PATH` and writes the index to `FAISS_INDEX_PATH`.

6.  **Run the application:**
    To run the Streamlit interface (it will use the port specified in `APP_PORT` from your `.env` file, or 8501 by default if not set in `.env` but only in `.env.example` or if `dotenv` loading fails for this specific CLI usage):
    ```bash
    # Make sure APP_PORT is set in your environment (e.g., from .env or exported)
    # Streamlit directly picks up some config like server.port via its own mechanisms
    # but to be explicit with 12-Factor, we will guide users to set it and use it.
    # One way to ensure it for the command if not globally exported:
    APP_PORT=$(grep APP_PORT .env | cut -d '=' -f2) streamlit run botInterface.py --server.port=${APP_PORT:-8501}
    # Or, if you load .env contents into your shell environment before running:
    # streamlit run botInterface.py --server.port=$APP_PORT
    ```
    A simpler way if `python-dotenv` CLI is available or if you manage env vars externally:
    ```bash
    # Assuming APP_PORT is loaded into the environment, e.g. by your shell sourcing .env,
    # or using a tool like direnv, or if streamlit automatically picks it up.
    # The most straightforward for Streamlit is to pass it as an argument:
    streamlit run botInterface.py --server.port ${APP_PORT:-8501} 
    # (The ${APP_PORT:-8501} syntax uses environment variable APP_PORT if set, otherwise defaults to 8501)
    ```
    The application will typically be available at `http://localhost:${APP_PORT}`.

### Running with Docker (Recommended for Deployment)

This project includes a `Dockerfile` to build and run the application in a containerized environment. This is the recommended way to run the application for consistency and to align with 12-Factor principles.

1.  **Build the Docker image:**
    From the project root directory (where the `Dockerfile` is located):
    ```bash
    docker build -t denexus-chatbot-ai .
    ```

2.  **Run the Docker container:**
    You'll need to pass your `GROQ_API_KEY` as an environment variable to the container. You can also override `APP_PORT` if needed.
    ```bash
    docker run -p 8501:8501 --env GROQ_API_KEY="your_actual_groq_api_key" denexus-chatbot-ai
    # To use a different host port or specify the container port (if you changed APP_PORT in .env or want to override Dockerfile default):
    # docker run -p <host_port>:<container_port> --env GROQ_API_KEY="your_actual_groq_api_key" --env APP_PORT=<container_port> denexus-chatbot-ai
    ```
    For example, if your `GROQ_API_KEY` is `sk-123...` and you want to run on host port `8000` mapping to container port `8501` (the default in the image):
    ```bash
    docker run -p 8000:8501 --env GROQ_API_KEY="sk-123..." denexus-chatbot-ai
    ```
    The application will be available at `http://localhost:<host_port>` (e.g., `http://localhost:8000`).

### Health Check

The application provides a health check endpoint that reports on the status of key components:
- FAISS index availability
- Groq API connectivity 
- Application uptime

To access the health check:
```
http://localhost:8501/?health-check
```

The health check returns a JSON response with status information for all critical components.

### Testing

Unit tests are included in the `tests/` directory to verify the core functionality without relying on external services:

1. **Run the tests:**
   ```bash
   python -m unittest discover -s tests
   ```

2. **Test coverage includes:**
   - ChatBot initialization and configuration
   - FAISS index loading
   - Context retrieval functionality
   - LLM response generation (mocked)
   - Error handling for missing API keys

If you're using Docker, you can run the tests inside the container:
```bash
docker run --rm denexus-chatbot-ai python -m unittest discover -s tests
```

### Log Monitoring with ELK Stack

The project includes an ELK (Elasticsearch, Logstash, Kibana) stack for advanced log monitoring and visualization. Logs are collected automatically from all Docker containers, with special parsing rules for the chatbot application.

#### Setup and Usage

1. **Run the ELK stack with the application:**
   ```bash
   # Make sure your .env file contains GROQ_API_KEY
   docker-compose up -d
   ```

2. **Access the monitoring dashboard:**
   - Kibana: http://localhost:5601
   - Elasticsearch API: http://localhost:9200

3. **Setting up Kibana (first-time setup):**
   - Go to http://localhost:5601
   - Navigate to "Stack Management" → "Index Patterns"
   - Create an index pattern with `chatbot-logs-*`
   - Select `@timestamp` as the time filter field
   - Click "Create index pattern"
   - Go to "Discover" to see incoming logs

4. **Log visualization features:**
   - Filter logs by level (INFO, WARNING, ERROR)
   - View logs by component (faiss_index, groq_api)
   - Create dashboards for error monitoring
   - Set up alerts for critical errors

5. **Structured logging:**
   The application now uses structured JSON logging for better ELK integration. Key fields include:
   - `timestamp`: When the log entry was created
   - `level`: Log level (INFO, WARNING, ERROR)
   - `message`: The log message
   - `logger`: The logger name (chatbot)
   - `function`: For errors, indicates which function failed
   - `error_type`: The type of exception for errors
   - `component`: Which component the log relates to

#### Customizing Log Retention

By default, logs are retained based on Elasticsearch's default retention policy. For production use, consider setting up index lifecycle management in Elasticsearch.

*(More details to be filled in as we progress)*

## 12-Factor App Implementation

This section details how the project adheres to the 12-Factor App methodology.

### 12-Factor Adaptation Notes & Future Refinements

As we adapt the project to the 12-Factor methodology, this section will note key changes, decisions, and areas that could be further refined in a more complex production environment.

*   **Factor III (Config) & Factor IV (Backing Services):** Hardcoded Groq API key was moved to `GROQ_API_KEY` environment variable. Paths for data (`data/`) and FAISS index (`faiss_index/`) were made configurable via `DATA_PATH` and `FAISS_INDEX_PATH` environment variables, treating them as configurable resource locators.
*   **Factor V (Build, Release, Run):** Introduced a separate `build_index.py` script to handle the creation of the FAISS vector index. The main application (`RAG.py`) now loads this pre-built index instead of generating it at runtime, clearly separating the build and run stages. With Docker, `docker build` executes `build_index.py` incorporating the index into the image (build & release), and `docker run` executes the application (run).
*   **Factor VI (Processes):** The core request-handling logic of the `ChatBot` is stateless. The main application process (Streamlit running in a Docker container) loads the FAISS index into memory as a read-only resource. Streamlit manages user session state (chat history) in memory within each container.
*   **Factor VII (Port Binding):** The application uses Streamlit, which handles port binding. The `Dockerfile` `EXPOSE`s the `APP_PORT`, and `docker run` maps a host port to the container's exposed port.
*   **Factor VIII (Concurrency):** The application is designed to scale out by running multiple stateless Docker containers, typically behind a load balancer. Each container operates independently.
*   **Factor IX (Disposability):** Docker containers are inherently disposable. The FAISS index is built into the image for fast startup. Containers can be quickly started and stopped.
*   **Factor X (Dev/Prod Parity):** Using Docker for both development and production ensures environments are as similar as possible, reducing environment-specific bugs.
*   **Factor XI (Logs):** The application writes logs to `stdout`/`stderr`. Docker captures these streams, making them available via `docker logs` and enabling integration with centralized logging systems.
*   **Factor XII (Admin Processes):** The primary admin task, building the FAISS index (`build_index.py`), is run in the same environment as the application (during Docker image build) and ships with the app code.

### I. Codebase

One codebase tracked in Git, supporting multiple deploys (development, production).

*   All code, configuration templates, and infrastructure definitions are stored in the Git repository.
*   The `faiss_index/` directory, which contains the generated FAISS index, is listed in `.gitignore` as it's a build artifact and should be generated during the build/deployment process.

### II. Dependencies

Dependencies are explicitly declared and isolated.

*   All Python dependencies are listed in `requirements.txt`.
*   It is strongly recommended to use a Python virtual environment (e.g., `venv`) to isolate project dependencies.

### III. Config

Configuration that varies between deploys (e.g., API keys, resource handles) is stored in the environment.

*   The application (specifically `RAG.py`) reads sensitive configurations like the `GROQ_API_KEY` from environment variables.
*   Paths for local data (`data/`) and the FAISS index (`faiss_index/`) are also configurable via `DATA_PATH` and `FAISS_INDEX_PATH` environment variables respectively, with sensible defaults.
*   A `.env.example` file is provided in the repository to show what environment variables are needed.
*   Actual secret files (like a `.env` file) should not be committed to the repository and are included in `.gitignore`.

### IV. Backing Services

Backing services are treated as attached resources, typically consumed over a network.

*   **Groq API**: This is an external API and is treated as an attached resource. Its API key (configuration) is supplied via the `GROQ_API_KEY` environment variable (Factor III).
*   **FAISS Index & Data Files**: These are currently local file system resources. The data files in `DATA_PATH` are inputs to the build process (`build_index.py`). The FAISS index at `FAISS_INDEX_PATH` is an artifact of the build stage and is consumed by the run stage. Their locations are configurable via environment variables.

### V. Build, release, run

Strictly separate build and run stages.

*   **Build Stage:** Executed by running `python build_index.py`. This script takes the codebase, dependencies (installed via `requirements.txt`), and data (from `DATA_PATH`) to produce the FAISS vector index (saved to `FAISS_INDEX_PATH`). This index is a build artifact.
*   **Release Stage:** A release is the combination of the build (code + build artifacts like the FAISS index) and the configuration (environment variables). For this project, a release isn't a single packaged binary but the state of the repository files plus the generated index, ready to be run with appropriate environment configuration.
*   **Run Stage:** Executed by running `streamlit run botInterface.py`. This stage runs the application. The application expects the FAISS index to be pre-built and available at `FAISS_INDEX_PATH`. It does not perform any build steps itself.

### VI. Processes

Execute the app as one or more stateless processes.

*   **ChatBot Logic:** The `ChatBot` class in `RAG.py`, once initialized with the FAISS index, processes each incoming query statelessly. It does not retain information from one query to affect the processing of subsequent, independent queries.
*   **In-Memory Index:** The FAISS index is loaded into the memory of each application process (Streamlit worker) at startup. This is treated as a read-only, pre-built dependency for the lifetime of the process. This is acceptable as it doesn't represent mutable state that changes with requests.
*   **Streamlit Session State:** The `botInterface.py` (Streamlit app) uses `st.session_state` to maintain chat history for each user. This session state is currently held in the memory of the specific Streamlit process handling that user. For simple deployments, this is standard. For robust, scalable deployments that need to survive process restarts or load balancing across many instances without losing session data, this session state would ideally be externalized to a backing service (e.g., a database or cache like Redis). This is a more advanced consideration beyond the current scope.
*   **Scalability:** Because the core request processing is stateless, the application can be scaled horizontally by running multiple instances of the Streamlit application. Each instance would operate independently with its own copy of the read-only FAISS index.

### VII. Port Binding

Export services via port binding.

*   The application is served using Streamlit, which acts as the web server.
*   When executed with `streamlit run botInterface.py`, Streamlit binds to a network port and serves the application over HTTP, making it a self-contained web service.
*   The port is configurable. It is recommended to set the `APP_PORT` environment variable (e.g., in a `.env` file, with a default like `8501`) and use it when running the application:
    ```bash
    streamlit run botInterface.py --server.port ${APP_PORT:-8501}
    ```
*   This approach ensures the application does not rely on runtime injection of a webserver and explicitly declares its HTTP interface via port binding.

### VIII. Concurrency

Scale out via the process model.

*   The application is designed to achieve concurrency by running multiple instances of the Streamlit application process. This horizontal scaling is possible due to the stateless nature of the request handling (Factor VI).
*   Each process (typically a Docker container instance) would run independently, loading its own copy of the FAISS index (built into the image) and managing its own user sessions (given Streamlit's default session handling).
*   In a typical deployment, these multiple processes/containers would operate behind a load balancer, which distributes incoming requests among them.
*   The application does not rely on complex in-process threading for concurrency but rather on adding more identical processes/containers. This aligns with the 12-Factor model of scaling out.

### IX. Disposability

Maximize robustness with fast startup and graceful shutdown.

*   **Fast Startup:** Docker containers, by nature, start quickly. By building the FAISS index directly into the Docker image (during `docker build` via `RUN python build_index.py`), the application container starts with the index ready for use, minimizing startup time for the application logic itself.
*   **Graceful Shutdown:** When a Docker container is stopped (e.g., via `docker stop`), it sends a `SIGTERM` signal to the main process inside the container (Streamlit in this case), followed by a `SIGKILL` if the process doesn't terminate within a timeout. Python applications and Streamlit generally handle `SIGTERM` by default to shut down. No special signal handling is currently implemented in the application code, as the default behavior is expected to be sufficient for clean termination without data loss (given stateless operations and read-only index).
*   **Robustness & Scaling:** The disposability of containers allows for easy replacement of unhealthy instances and rapid scaling up or down by adding or removing containers.

### X. Dev/prod parity

Keep development, staging, and production as similar as possible.

*   **Docker for Consistency:** The use of Docker is central to achieving dev/prod parity. The `Dockerfile` defines a consistent Linux-based environment with specific Python and dependency versions.
*   **Development Workflow:** For optimal dev/prod parity, developers should run the application within the Docker container during development, similar to how it would run in staging or production. This can be achieved using `docker run` with volume mounts for the source code to allow live reloading of code changes without rebuilding the image for every minor edit.
    ```bash
    # Example for development with live code reloading (assuming current directory is project root):
    docker run -p 8501:8501 \
      --env GROQ_API_KEY="your_dev_groq_api_key" \
      -v "$(pwd)/RAG.py:/app/RAG.py" \
      -v "$(pwd)/botInterface.py:/app/botInterface.py" \
      denexus-chatbot-ai
    ```
    *Note: For Streamlit, live reloading of Python module changes might require restarting the `streamlit run` command or more advanced Docker setups if changes are deep within imported modules. For simple UI or script changes in `botInterface.py`, Streamlit often reloads automatically.*
*   **Production Deployment:** The same Docker image built and tested in development/staging environments is deployed to production. The only differences should be environment-specific configurations (Factor III) passed via environment variables.
*   **Reduced Risk:** This approach significantly reduces the risk of bugs that occur only in production due to environment differences.
*   **Backing Services:** While the application environment is consistent via Docker, dev/prod parity also extends to backing services (Factor IV). Ideally, development environments should connect to local or dev-tier instances of backing services (like a dev Groq API key or a local vector DB if used instead of FAISS files) that are as similar as possible to production services.

### XI. Logs

Treat logs as event streams.

*   **Output to `stdout`/`stderr`:** The application (including `RAG.py`, `build_index.py`, and Streamlit itself) writes log output to standard output (`stdout`) and standard error (`stderr`). This is achieved through the Python logging module configured to output structured JSON logs.
*   **Unbuffered Output:** The `Dockerfile` sets `ENV PYTHONUNBUFFERED=1`, ensuring that Python's log output is sent directly to the console streams without buffering, making logs timely.
*   **Structured Logging:** The application uses JSON structured logging, which makes the logs more machine-parsable and enables better indexing in Elasticsearch.
*   **ELK Stack Integration:** Logs are collected by Filebeat, processed by Logstash, stored in Elasticsearch, and visualized through Kibana.
*   **Docker Log Collection:** When running in a Docker container, Docker automatically captures these `stdout` and `stderr` streams. These are then collected by Filebeat and forwarded to the ELK stack.
*   **Log Management:** The ELK stack provides comprehensive log management features:
    ```bash
    docker logs <container_id_or_name>
    ```

### XII. Admin processes

Run admin/management tasks as one-off processes.

*   **FAISS Index Building (`build_index.py`):** The primary administrative task for this application is building the FAISS vector index. This is handled by the `build_index.py` script.
    *   **Ships with Code:** The script is part of the application codebase.
    *   **Identical Environment:** When using Docker, this script is executed via a `RUN` command in the `Dockerfile`. This means it runs in the exact same environment (OS, Python version, dependencies, environment variables like `DATA_PATH`, `FAISS_INDEX_PATH`) as the main application will eventually run in. This is a key aspect of Factor XII.
    *   **One-off Execution:** It's a one-off task that prepares an asset (the index) for the application. By running it during `docker build`, the resulting image contains the pre-built index.
*   **Other Admin Tasks:** If other one-off administrative tasks were needed (e.g., data migration, running a specific utility script), they should be implemented as scripts within the codebase and run using the application's Docker image to ensure environment consistency:
    ```bash
    docker run --rm --env-file .env denexus-chatbot-ai python path/to/your_admin_script.py [args]
    ```
    Using `--env-file .env` (if your `.env` file contains all necessary non-secret configs or if you manage secrets via the execution environment) or individual `--env` flags ensures the script has access to the same configuration as the main app.
*   **No SSH / Shell Access to Running Instances:** Factor XII discourages SSHing into running production instances to perform admin tasks. Instead, such tasks should be scripted and run as described above.

*(End of 12-Factor App Implementation section)*
