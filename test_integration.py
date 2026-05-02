import json
import time
from fastapi.testclient import TestClient
from fakeredis import FakeRedis

# Create a FakeRedis mock instead of hitting a real redis container
fake_redis = FakeRedis()

import api.main as api_main
# Override the real redis connection in the API with our mock
api_main.r = fake_redis

# TestClient to bypass network layer completely
client = TestClient(api_main.app)

def run_test_pipeline():
    print("1. Sending payload to FastAPI...")
    res = client.post("/process", json={"my_data": "hello world"})
    if res.status_code != 200:
        print("API Failed:", res.content)
        return
        
    job_id = res.json()["job_id"]
    print(f"-> Job {job_id} accepted by API.")
    
    print("2. Verifying the queue contents (Checking if API pushed to Redis)...")
    queue_data = fake_redis.brpop("jobs_queue", timeout=1)
    if not queue_data:
        print("Queue is empty, API failed to push!")
        return
        
    _, data = queue_data
    job = json.loads(data)
    print(f"-> Found job in queue: {job}")
    
    print("3. Simulating the Python Worker picking it up and returning result...")
    payload = job.get("data", {})
    result = {
        "processed_data": payload,
        "processed": True,
        "completed_timestamp": time.time()
    }
    fake_redis.set(f"result:{job_id}", json.dumps(result))
    
    print("4. Fetching job status from API (Verifying API reads worker results from Redis)...")
    status_res = client.get(f"/status/{job_id}")
    data = status_res.json()
    if data["status"] == "completed":
        print(f"-> SUCCESS! Pipeline verified. Final result: {data['result']}")
    else:
        print("Failed to get completed status. Pipeline verification failed.")

if __name__ == "__main__":
    run_test_pipeline()
