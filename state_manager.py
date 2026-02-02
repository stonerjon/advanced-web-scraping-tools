import os
import redis
import psycopg2
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class StateManager:
    """
    Manages persistence (Postgres) and caching/queueing (Redis).
    """
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.db_url = os.getenv("DATABASE_URL")
        
        self.r = redis.from_url(self.redis_url)

    def cache_set(self, key: str, value: Any, expire: int = 3600):
        """Sets a value in Redis with an expiration."""
        self.r.set(key, value, ex=expire)

    def cache_get(self, key: str) -> Optional[Any]:
        """Gets a value from Redis."""
        val = self.r.get(key)
        return val.decode('utf-8') if val else None

    def save_result(self, table: str, data: Dict[str, Any]):
        """Saves data into PostgreSQL."""
        if not self.db_url:
            print("DATABASE_URL not set. Skipping DB save.")
            return

        cols = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, list(data.values()))
                conn.commit()
        except Exception as e:
            print(f"Postgres Error: {e}")

    def push_task(self, queue: str, task: Dict[str, Any]):
        """Pushes a task to a Redis-based queue."""
        import json
        self.r.lpush(queue, json.dumps(task))

if __name__ == "__main__":
    state = StateManager()
    # state.cache_set("test_key", "hello")
    # print(state.cache_get("test_key"))
