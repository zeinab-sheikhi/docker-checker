# Docker Scanner Backend

This is the backend server for Docker Scanner, a service that processes Dockerfiles, builds images, scans for vulnerabilities, and measures container performance.

---

## 🚀 Quick Start

### 1. **Install [uv](https://github.com/astral-sh/uv) (Python package manager)**

If you don't have `uv` installed, the Makefile will handle it for you:

```bash
make install-uv
```

### 2. **Install Python Dependencies**

This will install all required packages (including dev dependencies):

```bash
make install
```

### 3. **Run the Server (Locally)**

```bash
make run-server
```

This will run the server using the `docker-scanner` CLI entrypoint.

### 4. **Run in Docker**

Build the Docker image:

```bash
make build-docker
```

Run the Docker container (with access to the host Docker daemon):

```bash
make run-docker
```

> **Note:** The Docker container needs access to the host Docker daemon. The Makefile mounts `/var/run/docker.sock` for this purpose.


## 📖 API Endpoints

### 1. **POST `/api/v1/jobs/`**
_Submit a Dockerfile for analysis._

- **Request:**
  - `multipart/form-data` with a single file field named `file` (the Dockerfile, **no extension**).
- **Response (200):**
  ```json
  { "job_id": "string" }
  ```
- **Response (400):**
  ```json
  { "detail": "Error message" }
  ```
- **Description:**
  Validates and accepts a Dockerfile and returns a job ID.

---

### 2. **GET `/api/v1/jobs/status/{job_id}`**
_Start processing (build, scan, run) the docker file associated with the job_id and check its status_

- **Response (200):**
  ```json
  {
    "job_id": "string",
    "dockerfile": "string",
    "build_status": "success|failed|skipped",
    "image_id": "string|null",
    "scan_status": "success|failed|skipped",
    "is_safe": true,
    "vulnerabilities": [
      {
        "package": "string",
        "vulnerability_id": "string",
        "severity": "string",
        "title": "string|null",
        "description": "string|null",
        "fixed_version": "string|null"
      }
    ],
    "run_status": "success|failed|skipped",
    "performance": 0.99,
    "error": "string|null"
  }
  ```
- **Response (404):**
  ```json
  { "detail": "Job not found" }
  ```
- **Description:**
  Returns the current status and results for the job, including build, scan, and run steps, vulnerabilities, and performance metrics.

---

### 3. **GET `/health`**
_Health check endpoint._

- **Response (200):**
  ```json
  { "message": "API is running." }
  ```

---

### 4. **GET `/`**
_Redirects to the API documentation (`/docs`)._

---

## 📝 Notes

- **API Docs:**
  Interactive documentation is available at `/docs` (Swagger UI) and `/redoc`.

- **Docker Access:**
  The backend requires access to the Docker daemon. If running in Docker, ensure `/var/run/docker.sock` is mounted.

- **Redis:**
  The backend uses Redis for job state management. Default settings assume Redis is running locally on port 6379.

---

## 🧩 Example Usage

**Submit a Dockerfile:**

```bash
curl -F "file=@Dockerfile" http://localhost:8000/api/v1/jobs/
```

**Check job status:**

```bash
curl http://localhost:8000/api/v1/jobs/status/<job_id>
```
