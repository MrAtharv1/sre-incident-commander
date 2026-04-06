FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir fastapi uvicorn pydantic requests openai

COPY models.py environment.py server.py inference.py ./

EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]