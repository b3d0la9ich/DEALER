#!/usr/bin/env bash
set -euo pipefail

function wait_for_db() {
  echo "[entrypoint] Ожидание БД..."
  for i in {1..30}; do
    if python - <<'PY'
import sys, os
import psycopg2
url = os.environ.get('DATABASE_URL', '')
if not url:
    sys.exit(1)
url = url.replace('postgresql+psycopg2://', 'postgresql://', 1)
try:
    conn = psycopg2.connect(url)
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(2)
PY
    then
      echo "[entrypoint] БД доступна"
      return 0
    fi
    sleep 2
  done
  echo "[entrypoint] Не удалось дождаться БД" >&2
  return 1
}

wait_for_db

# --- применяем миграции (или генерим первые, если их нет) ---
if ! flask db upgrade; then
  echo "[entrypoint] Миграций нет — создаю начальные"
  flask db init || true
  flask db migrate -m "auto init"
  flask db upgrade
fi

# --- создаём админа после миграций ---
echo "[entrypoint] Создание админа (если отсутствует)..."
python - <<'PY'
import os
from sqlalchemy import inspect
from app import app
from extensions import db
from models import User

email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASSWORD")

with app.app_context():
    insp = inspect(db.engine)
    if not insp.has_table("users"):
        print("[entrypoint] Таблицы users ещё нет — пропускаю создание админа")
    else:
        if email and password:
            u = User.query.filter_by(email=email.lower()).first()
            if not u:
                u = User(email=email.lower(), role="admin", full_name="Администратор")
                u.set_password(password)
                db.session.add(u)
                db.session.commit()
                print(f"[entrypoint] Админ создан: {email}")
            else:
                print(f"[entrypoint] Админ уже существует: {u.email}")
        else:
            print("[entrypoint] ADMIN_EMAIL или ADMIN_PASSWORD не заданы — пропускаю")
PY

# --- запускаем gunicorn (или CMD из Dockerfile) ---
exec "$@"
