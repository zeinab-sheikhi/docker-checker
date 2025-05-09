import time
from pathlib import Path

import requests


def test_docker_performance_service():
    """Test the Docker Performance Service API"""
    # API base URL
    base_url = "http://localhost:8000"

    # Create a test Dockerfile
    dockerfile_content = """
FROM ubuntu:latest
# Example ML model that outputs performance
CMD echo '{"perf":0.99}' > /data/perf.json
"""

    # Save Dockerfile
    Path("test_dockerfile").write_text(dockerfile_content)

    try:
        # Submit Dockerfile
        print("Submitting Dockerfile...")
        with open("test_dockerfile", "rb") as f:
            response = requests.post(f"{base_url}/jobs/", files={"file": ("Dockerfile", f)})
        response.raise_for_status()
        result = response.json()
        job_id = result["job_id"]
        print(f"Job created with ID: {job_id}")

        # Poll for status
        print("\nPolling for job status...")
        while True:
            response = requests.get(f"{base_url}/jobs/{job_id}")
            response.raise_for_status()
            status = response.json()
            print(f"Status: {status['status']}")

            if status["status"] in ["SUCCESS", "FAILED"]:
                print("\nFinal result:")
                print(f"Status: {status['status']}")
                print(f"Performance: {status.get('performance')}")
                print(f"Message: {status.get('message')}")
                break

            time.sleep(2)  # Wait 2 seconds before next poll

    finally:
        # Cleanup
        Path("test_dockerfile").unlink(missing_ok=True)


if __name__ == "__main__":
    test_docker_performance_service()
