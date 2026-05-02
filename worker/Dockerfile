FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# -u flag makes python output unbuffered, so we see prints instantly in docker logs
CMD ["python", "-u", "worker.py"]
