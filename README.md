# Docker Scanner Project

## Architecture Overview

This project consists of three main services, orchestrated using Docker Compose:

### 1. Backend
- **Location:** `./backend`
- **Description:** The backend is a FastAPI (Python) service that provides the main API for the application. It communicates with Docker on the host (via a mounted Docker socket) and uses Redis for caching or task management.
- **Exposed Port:** `8000`
- **Depends on:** Redis

### 2. Redis
- **Location:** Docker official image
- **Description:** Used as a cache for the backend service.
- **Exposed Port:** `6379`

### 3. Frontend
- **Location:** `./frontend`
- **Description:** A Flutter web application served via Nginx. It communicates with the backend API.
- **Exposed Port:** `58632`
- **Depends on:** Backend

All services are defined in `compose.yml` and can be built and run together.

## Service Interaction
- The **frontend** (Flutter web) makes HTTP requests to the **backend** (FastAPI).
- The **backend** interacts with the host's Docker daemon (via `/var/run/docker.sock`) and uses **Redis** for caching.
- All services are networked together by Docker Compose, allowing them to communicate via service names (e.g., `backend`, `redis`).

## Service URLs
After starting the services, you can access them at:

- **Frontend:** [http://localhost:58632](http://localhost:58632)
- **Backend API:** [http://localhost:8000](http://localhost:8000)

## Running the Project

### 1. Build and Start All Services

You can use the provided script to build and start everything:

```bash
./startup.sh
```

This will:
- Build all Docker images (if needed)
- Start all services in the background
- Open the frontend in your browser
- Stream logs from all services

### 2. Manual Docker Compose Commands

Alternatively, you can use Docker Compose directly:

```bash
docker compose build
# or (older versions)
docker-compose build

docker compose up
# or
docker-compose up
```

To run in detached mode (in the background):

```bash
docker compose up -d
```

To stop all services:

```bash
docker compose down
```

## Development Notes
- The frontend disables CORS for local development. If deploying to production, review CORS settings.
- You can rebuild individual services by running `docker compose build <service>`.
- For more details on each service, see their respective `README.md` files in `backend/` and `frontend/`.

---

For any issues, please check the logs using:

```bash
docker compose logs -f
```
