FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /home/user/app
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir fastapi uvicorn pydantic requests openai

COPY --chown=user:user models.py environment.py server.py inference.py pyproject.toml ./

EXPOSE 7860
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "7860"]
