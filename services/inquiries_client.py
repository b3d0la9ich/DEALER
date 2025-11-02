import os
import requests

# 1) База из переменной окружения. МОЖЕТ быть с /api или без — нормализуем.
_raw_base = os.getenv("INQUIRIES_BASE", "http://inquiries:8080").strip()

# убираем хвостящий слэш
_raw_base = _raw_base.rstrip('/')

# если база оканчивается на /api — отрежем его, чтобы не было /api/api
if _raw_base.lower().endswith('/api'):
    BASE = _raw_base[:-4]  # без '/api'
else:
    BASE = _raw_base

API_KEY = os.getenv("INQUIRIES_API_KEY", "dev-secret")
TIMEOUT = 5

def _headers():
    return {"X-Api-Key": API_KEY, "Content-Type": "application/json"}

def create_inquiry(payload: dict):
    url = f"{BASE}/api/inquiries"
    r = requests.post(url, json=payload, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def list_by_buyer(buyer_id: int):
    url = f"{BASE}/api/inquiries"
    r = requests.get(url, params={"buyer_id": buyer_id}, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def list_by_seller(seller_id: int):
    url = f"{BASE}/api/inquiries"
    r = requests.get(url, params={"seller_id": seller_id}, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def update_status(inq_id: int, status: str):
    url = f"{BASE}/api/inquiries/{inq_id}/status"
    r = requests.put(url, json={"status": status}, headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return True
