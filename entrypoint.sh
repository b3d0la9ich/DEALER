#!/usr/bin/env bash
set -euo pipefail

wait_for_db() {
  echo "[entrypoint] Ожидание БД..."
  for i in {1..30}; do
    if python - <<'PY'
import sys, os, psycopg2
url = os.environ.get('DATABASE_URL','')
if not url: sys.exit(1)
url = url.replace('postgresql+psycopg2://','postgresql://',1)
try:
    psycopg2.connect(url).close()
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

echo "[entrypoint] Применяю миграции (если есть)..."
flask db upgrade || true

echo "[entrypoint] Проверяю наличие администратора..."
python - <<'PY'
import os
import sys
from app import app, db

with app.app_context():
    # Импортируем модели внутри контекста приложения
    from models import User

    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")

    # Используем правильное имя поля для email (в модели оно lowercase)
    admin_email = admin_email.lower()

    if not User.query.filter_by(email=admin_email).first():
        print(f"[entrypoint] Администратор не найден, создаю {admin_email}...")
        user = User(
            email=admin_email,
            role='admin',  # Используем 'admin' вместо 'administrator'
            full_name="Администратор"
        )
        # Используем правильный метод set_password (работает с password_hash)
        user.set_password(admin_password)
        db.session.add(user)
        db.session.commit()
        print("[entrypoint] Администратор успешно создан.")
    else:
        print("[entrypoint] Администратор уже существует.")
PY

echo "[entrypoint] Запуск приложения..."
exec "$@"
