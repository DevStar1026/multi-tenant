import requests

def run_api_task(url: str, method: str = "GET", payload: dict = None):
    if method == "POST":
        res = requests.post(url, json=payload)
    else:
        res = requests.get(url)
    try:
        return res.json()
    except Exception:
        return {"error": res.text}
