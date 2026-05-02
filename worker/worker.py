import redis
import json
import os
import time

redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0)

print(f"Worker started, connected to redis at {redis_host}")

while True:
    # Block until an item is available in jobs_queue. Timeout is 0 (infinite)
    queue, data = r.brpop("jobs_queue")
    
    if data:
        job = json.loads(data)
        job_id = job.get("job_id")
        payload = job.get("data", {})
        
        print(f"Processing job {job_id}...")
        
        # Simulate an expensive data processing step
        time.sleep(2)
        
        # Mock result of processing
        result = {
            "processed_data": payload,
            "processed": True,
            "completed_timestamp": time.time()
        }
        
        # Store result so the API can fetch it for the status route
        r.set(f"result:{job_id}", json.dumps(result))
        
        # Expire result in 1 hour so redis memory doesn't blow up
        r.expire(f"result:{job_id}", 3600)
        
        print(f"Job {job_id} completed.")
