import json
from typing import Any

import redis

from docker_scanner.settings import settings


class RedisService:
    def __init__(
        self,
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
    ):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def update_job_data(self, job_id: str, data: dict[str, Any], expire_seconds: int | None = None):
        """
        Save a mapping of job data (dockerfile, perf, perf_json, etc.) for a job_id.
        Optionally set an expiration time in seconds.
        """
        # Convert any non-string values to JSON strings
        data_to_store = {k: (json.dumps(v) if not isinstance(v, str) else v) for k, v in data.items()}
        self.client.hset(job_id, mapping=data_to_store)
        if expire_seconds:
            self.client.expire(job_id, expire_seconds)

    def get_job_data(self, job_id: str) -> dict[str, Any] | None:
        """
        Retrieve all data for a job_id as a dict.
        """
        data = self.client.hgetall(job_id)
        if not data:
            return None
        for k, v in data.items():
            try:
                data[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                pass
        return data

    def get_job_field(self, job_id: str, field: str) -> Any | None:
        """
        Retrieve a specific field for a job_id.
        """
        value = self.client.hget(job_id, field)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def delete_job(self, job_id: str):
        """
        Delete all data for a job_id.
        """
        self.client.delete(job_id)
