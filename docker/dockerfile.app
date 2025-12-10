FROM python:3.11-slim
WORKDIR /app

# system deps for pypdf, etc.
RUN apt-get update && apt-get install -y build-essential libffi-dev poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy code
COPY src /app/src
ENV PYTHONPATH=/app/src

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
