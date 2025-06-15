import requests

BASE_URL = "https://accept.paymobsolutions.com/api"
API_KEY = "your_api_key_here"
def get_auth_token():
    url = f"{BASE_URL}/auth/tokens"
    response = requests.post(url, json={"api_key": API_KEY})
    data = response.json()

    print("Paymob auth response:", data)
    if "token" not in data:
        raise Exception("Paymob authentication failed: " + str(data))
    
    return data["token"]

def create_paymob_order(token, amount_cents, items=[]):
    url = f"{BASE_URL}/ecommerce/orders"
    data = {
        "auth_token": token,
        "delivery_needed": "false",
        "amount_cents": amount_cents,
        "items": items,
    }
    response = requests.post(url, json=data)
    return response.json()["id"]

def generate_payment_key(token, order_id, amount_cents, billing_data):
    url = f"{BASE_URL}/acceptance/payment_keys"
    integration_id = "your_integration_id"  # من Paymob Dashboard

    data = {
        "auth_token": token,
        "amount_cents": amount_cents,
        "expiration": 3600,
        "order_id": order_id,
        "billing_data": billing_data,
        "currency": "EGP",
        "integration_id": integration_id,
    }
    response = requests.post(url, json=data)
    return response.json()["token"]
