from fastapi import FastAPI
import redis
import json
import os
import uuid

app = FastAPI(title="Data Processor API")

# Connect to Redis. In docker-compose, the service name is 'redis'
redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0)

@app.post("/process")
def process_data(data: dict):
    job_id = str(uuid.uuid4())
    payload = {
        "job_id": job_id,
        "data": data
    }
    
    # Push job to the Redis queue
    r.lpush("jobs_queue", json.dumps(payload))
    
    return {"status": "accepted", "job_id": job_id}

@app.get("/status/{job_id}")
def get_status(job_id: str):
    # Fetch result key created by the worker
    result = r.get(f"result:{job_id}")
    if result:
        return {"status": "completed", "result": json.loads(result)}
    return {"status": "pending"}
