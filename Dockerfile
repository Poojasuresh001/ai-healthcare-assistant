FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CHROMA_DIRECTORY=/app/chroma_db \
    DATABASE_PATH=/app/data/synthetic_healthcare.sqlite3

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt \
    && groupadd --system app \
    && useradd --system --gid app --create-home app \
    && mkdir -p /app/chroma_db /app/data \
    && chown -R app:app /app

COPY --chown=app:app app ./app
COPY --chown=app:app documents ./documents
COPY --chown=app:app scripts ./scripts
COPY --chown=app:app evaluations ./evaluations

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
