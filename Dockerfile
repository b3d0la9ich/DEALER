FROM python:3.12-slim AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn==22.0.0

COPY . .
# >>> добавлено: каталог для загрузок и права
RUN mkdir -p /app/static/uploads \
    && chown -R appuser:appuser /app \
    && chmod -R 775 /app/static/uploads

ENV FLASK_APP=app.py \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER appuser
EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
