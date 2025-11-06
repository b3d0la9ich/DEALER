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

exec "$@"
