# RAG Cybersecurity Chatbot

A Retrieval Augmented Generation (RAG) chatbot system focused on cybersecurity incidents and threats. The system uses vector embeddings and LLM technology to provide accurate, context-aware responses about cybersecurity events.

## Features

- Real-time chat interface using Streamlit
- RAG implementation with FAISS vector database
- Integration with Groq API for LLM processing
- Multi-source cybersecurity data processing
- Docker-based deployment with strict build, release, run stages

## Prerequisites

- Docker and Docker Compose
- Python 3.10 or higher
- Groq API key
- Git

## Project Structure

```
.
├── Data/                   # Data directory for CSV files
├── faiss_index/           # Vector database storage
├── scripts/               # Build, release, and run scripts
│   ├── build.sh
│   ├── release.sh
│   └── run.sh
├── .env                   # Environment variables
├── botInterface.py        # Streamlit interface
├── RAG.py                 # Core RAG implementation
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
└── docker-compose.yml    # Service orchestration
```

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a `.env` file with the following variables:
```env
GROQ_API_KEY=your_api_key_here
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
VECTOR_DB_PATH=faiss_index
```

3. Place your CSV files in the `Data/` directory with the following naming convention:
   - CISSM_cleaned.csv
   - HACKMAGEDDON_cleaned.csv
   - ICSSTRIVE_cleaned.csv
   - KONBRIEFING_cleaned.csv
   - TISAFE_cleaned.csv
   - WATERFALL_cleaned.csv

## Build, Release, Run Process

The project follows the 12-Factor App principle of strict separation between build, release, and run stages.

### Build Stage

Builds the application container:
```bash
chmod +x scripts/build.sh
./scripts/build.sh
```

### Release Stage

Creates a versioned release:
```bash
chmod +x scripts/release.sh
./scripts/release.sh [version]
```

### Run Stage

Deploys the application:
```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

## Development

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application locally:
```bash
streamlit run botInterface.py
```

### Docker Development

1. Build the container:
```bash
docker-compose build
```

2. Run the container:
```bash
docker-compose up
```

## Data Sources

The system processes data from multiple cybersecurity sources:

- CISSM: Event descriptions
- HACKMAGEDDON: Attack descriptions
- ICSSTRIVE: Incident descriptions
- KONBRIEFING: Threat descriptions
- TISAFE: Attack details and IDs
- WATERFALL: Incident summaries and IDs

## Environment Variables

- `GROQ_API_KEY`: Your Groq API key
- `EMBEDDING_MODEL`: HuggingFace model for embeddings (default: sentence-transformers/all-mpnet-base-v2)
- `VECTOR_DB_PATH`: Path to store the FAISS index (default: faiss_index)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your License Here]

## Contact

[Your Contact Information]
