# Docker Setup Guide for Network Security Project

## Files Included

- **Dockerfile** - Multi-stage Docker configuration for the FastAPI application
- **docker-compose.yml** - Orchestration file for PostgreSQL + FastAPI app
- **.dockerignore** - Excludes unnecessary files from Docker image
- **.env.example** - Template for environment variables

## Prerequisites

- Docker installed and running
- Docker Compose installed (comes with Docker Desktop)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Copy the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Build and start the services:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - FastAPI docs: http://localhost:8000/docs
   - API: http://localhost:8000

4. **Stop the services:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t network-security-app .
   ```

2. **Run the container** (requires existing PostgreSQL):
   ```bash
   docker run -p 8000:8000 \
     -e DB_HOST=localhost \
     -e DB_PORT=5432 \
     -e DB_NAME=network_security \
     -e DB_USER=networksecurity \
     -e DB_PASSWORD=postgres \
     network-security-app
   ```

## Development Mode

For development with auto-reload:

```bash
docker-compose up --build
```

The `docker-compose.yml` includes the `--reload` flag for Uvicorn.

## Production Deployment

For production, modify `docker-compose.yml`:

```yaml
command: uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `DB_HOST` - PostgreSQL host (use `postgres` in docker-compose)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password

## Volumes

The docker-compose setup persists:
- `postgres_data` - PostgreSQL data
- `./Artifacts` - Model artifacts
- `./logs` - Application logs
- `./final_model` - Final trained models

## Troubleshooting

### Database connection issues
```bash
docker-compose logs postgres
docker-compose logs app
```

### Rebuild without cache
```bash
docker-compose build --no-cache
```

### Remove all containers and volumes
```bash
docker-compose down -v
```

## Health Check

The application includes a health check endpoint. To verify:

```bash
curl http://localhost:8000/
```

Should redirect to the API documentation.
