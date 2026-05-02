# Serverless Data Processor VM

This repository contains a full-stack event-driven data processing pipeline.

## Architecture

* **API**: FastAPI service that accepts incoming data jobs and returns job status.
* **Queue**: Redis list used as a message broker between the API and Worker.
* **Worker**: Python background worker that picks up jobs from the queue, processes them, and saves the results back to Redis.

## Local Setup (Docker)

1. Ensure Docker Desktop is running.
2. Run `docker-compose up --build -d` to start the Redis, API, and Worker containers.
3. The API will be available at `http://localhost:8000`.

## Testing the API

1. Submit a job:
```bash
curl -X POST http://localhost:8000/process -H "Content-Type: application/json" -d '{"data": "test payload"}'
```
This returns a `job_id`.

2. Check job status:
```bash
curl http://localhost:8000/status/<job_id>
```

## Running Integration Tests

To run the pipeline integration test without Docker (using `fakeredis`):

```bash
pip install -r api/requirements.txt
pip install -r worker/requirements.txt
pip install fakeredis httpx pytest
python test_integration.py
```

## Cloud Deployment (Terraform)

This repository includes a Terraform script to deploy the stack to an AWS EC2 instance.

1. Navigate to the `terraform` directory.
2. Run `terraform init`.
3. Run `terraform apply` to provision the VM and install Docker.
4. SSH into the VM and run the `docker-compose` command.
