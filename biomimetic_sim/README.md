# Biomimetic Industrial Simulation Platform
**Continuous Multiphase Biomineralization & Solidification Grid (CMBSG)**

Full-stack technical implementation for simulating industrial post-combustion capture and mineralization.

## Getting Started

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- PostgreSQL (if running locally without Docker)
- Redis (if running locally without Docker)

### Running with Docker Compose
To launch the complete infrastructure (FastAPI API server, PostgreSQL database, Redis broker, and Celery background workers):
```bash
docker-compose up --build
```
The API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- Redocly: `http://localhost:8000/redoc`

### Local Development Setup
1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the migrations/startup:
   The FastAPI app automatically runs the migrations and tables creation on startup.
4. Start the API Server:
   ```bash
   uvicorn api.main:app --reload
   ```
5. Start the Celery Worker:
   ```bash
   celery -A workers.celery_app worker --loglevel=info
   ```
