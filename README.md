# Docker Scanner Project

This application provides a web interface and REST API for evaluating Dockerfiles by building, scanning, and running Docker images, then extracting a performance metric from the container output. The workflow is as follows:

### 1. Uploading a Dockerfile
- The user uploads a Dockerfile through the frontend interface.
- The backend receives the Dockerfile and validates its syntax.
- If the Dockerfile is valid, a new job is created and a job ID is returned to the user.

### 2. Building the Docker Image
- The backend builds a Docker image from the submitted Dockerfile.
- If the build fails, the job is marked as failed and the user is notified.

### 3. Vulnerability Scanning with Trivy
- The built image is scanned for vulnerabilities using [Trivy](https://github.com/aquasecurity/trivy), an open-source container security scanner.
- The backend calls Trivy as a subprocess and parses its output.
- If Trivy finds any **critical** or **high** vulnerabilities, the job is marked as failed and the user is notified.
- If no critical or high vulnerabilities are found, the workflow continues.

### 4. Running the Container & Extracting Performance
- The backend runs the built Docker image as a container.
- The container is started with a volume mounted from the host to the container's `/data` directory. This allows the backend to access files written by the container.
    - **Implementation:** The backend creates a temporary directory on the host, mounts it to `/data` in the container using Docker's `-v` or `--mount` option, and after the container finishes, reads files from this directory.
- The container is expected to write a file `/data/perf.json` containing a JSON object with a `perf` value (e.g., `{ "perf": 0.99 }`).
- After the container exits, the backend checks if `perf.json` exists in the mounted directory:
    - If it exists, the backend reads the file, extracts the performance value, and marks the job as successful, returning the performance to the user.
    - If it does not exist, the job is marked as failed.

### 5. Job Status & Results
- The user can query the status and result of their job using the job ID.
- The backend returns the current status (pending, failed, success) and the performance value if available.

## Example Dockerfile
Here is an example Dockerfile that writes a performance value to `/data/perf.json`:

```Dockerfile
FROM ubuntu:latest
# train machine learning model
# save performances
CMD echo '{"perf":0.99}' > /data/perf.json
```

## Volume Mounting Details
- The backend creates a temporary directory on the host for each job.
- This directory is mounted into the container at `/data`.
- Any files written by the container to `/data` (such as `perf.json`) are accessible to the backend after the container exits.
- This approach ensures safe and isolated data exchange between the container and the backend service.

## Architecture Overview

This project consists of three main services, orchestrated using Docker Compose:

### 1. Backend
- **Location:** `./backend`
- **Description:** The backend is a FastAPI (Python) service that provides the main API for the application. It communicates with Docker on the host (via a mounted Docker socket) and uses Redis for caching or task management.
- **Exposed Port:** `8000`
- **Depends on:** Redis

### 2. Redis
- **Location:** Docker official image
- **Description:** Used as a cache.
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
