# Playwright Python image: Chromium + OS libs (glib, nss, etc.) for Railway/Docker deploys.
# Tag must match backend/requirements.txt (playwright==1.49.0).
FROM mcr.microsoft.com/playwright/python:v1.49.0-jammy

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install chromium

COPY . .

EXPOSE 8000

# Railway sets PORT; local fallback 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
