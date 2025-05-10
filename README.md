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
    To run the Streamlit interface:
    ```bash
    streamlit run botInterface.py
    ```

*(More details to be filled in as we progress)*

## 12-Factor App Implementation

This section details how the project adheres to the 12-Factor App methodology.

### 12-Factor Adaptation Notes & Future Refinements

As we adapt the project to the 12-Factor methodology, this section will note key changes, decisions, and areas that could be further refined in a more complex production environment.

*   **Factor III (Config) & Factor IV (Backing Services):** Hardcoded Groq API key was moved to `GROQ_API_KEY` environment variable. Paths for data (`data/`) and FAISS index (`faiss_index/`) were made configurable via `DATA_PATH` and `FAISS_INDEX_PATH` environment variables, treating them as configurable resource locators.
*   **Factor V (Build, Release, Run):** Introduced a separate `build_index.py` script to handle the creation of the FAISS vector index. The main application (`RAG.py`) now loads this pre-built index instead of generating it at runtime, clearly separating the build and run stages.
*   **Factor VI (Processes):** The core request-handling logic of the `ChatBot` is stateless. The main application process (Streamlit) loads the FAISS index into memory as a read-only resource. Streamlit manages user session state (chat history) in memory within each process.

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
