# services/inquiries_client.py
import os
import requests

BASE_URL = os.getenv("INQUIRIES_BASE", "http://inquiries:8080/api")
API_KEY = os.getenv("INQUIRIES_API_KEY", "")


def _headers():
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-Api-Key"] = API_KEY
    return headers


def _raise_api_error(resp: requests.Response):
    """
    Если бэк вернул JSON {"error": "..."} — поднимаем RuntimeError с этим текстом,
    иначе обычный raise_for_status().
    """
    try:
        data = resp.json()
        msg = data.get("error")
        if msg:
            raise RuntimeError(msg)
    except ValueError:
        # не JSON
        pass
    resp.raise_for_status()


def create_inquiry(payload: dict) -> dict:
    """
    payload = {
        "car_id": int,
        "buyer_id": int,
        "seller_id": int,
        "message": str,
        "preferred_time": "YYYY-MM-DDTHH:MM" | "",
        "contact_phone": str
    }
    """
    url = f"{BASE_URL}/inquiries"
    resp = requests.post(url, json=payload, headers=_headers(), timeout=5)
    if not resp.ok:
        _raise_api_error(resp)
    return resp.json()


def list_by_buyer(buyer_id: int) -> list[dict]:
    url = f"{BASE_URL}/inquiries"
    resp = requests.get(
        url,
        params={"buyer_id": buyer_id},
        headers=_headers(),
        timeout=5,
    )
    if not resp.ok:
        _raise_api_error(resp)
    return resp.json()


def list_by_seller(seller_id: int) -> list[dict]:
    url = f"{BASE_URL}/inquiries"
    resp = requests.get(
        url,
        params={"seller_id": seller_id},
        headers=_headers(),
        timeout=5,
    )
    if not resp.ok:
        _raise_api_error(resp)
    return resp.json()


def update_status(inquiry_id: int, status: str) -> None:
    url = f"{BASE_URL}/inquiries/{inquiry_id}/status"
    resp = requests.put(
        url,
        json={"status": status},
        headers=_headers(),
        timeout=5,
    )
    if not resp.ok:
        _raise_api_error(resp)
