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
    Then, edit the `.env` file and add your `GROQ_API_KEY`.

5.  **Run the application:**
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
*   **FAISS Index & Data Files**: These are currently local file system resources. However, their locations are now configurable via environment variables (`FAISS_INDEX_PATH`, `DATA_PATH`). This provides flexibility and is a step towards treating them as abstract resources. In a more distributed or managed environment, the FAISS index could be replaced by a managed vector database service, which would then be a true network-attached backing service.
