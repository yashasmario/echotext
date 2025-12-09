import requests

def fetch_medicine_info(name):
    url = f"https://example-medicine-api.com/search?query={name}"
    r = requests.get(url)
    return r.json()
