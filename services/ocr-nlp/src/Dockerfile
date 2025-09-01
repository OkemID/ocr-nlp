FROM python:3.10-slim

WORKDIR /app

COPY test_client.py ./

# Note: file-uploads will be mounted via volume
RUN pip install requests

CMD ["python", "test_client.py"]
