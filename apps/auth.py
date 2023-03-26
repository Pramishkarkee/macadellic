from django.conf import settings
import requests

def get_access_token():
    try:
        url = "https://{}/oauth/token".format(settings.AUTH0_MACHINE_DOMAIN)
        payload = {
            "client_id": settings.AUTH0_MACHINE_ID,
            "client_secret": settings.AUTH0_MACHINE_SECRET,
            "audience": "https://{}/api/v2/".format(settings.AUDIENCE),
            "grant_type": "client_credentials"
        }
        headers = {
            "content-type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        access_token= response.json()["access_token"]
        return access_token
    except Exception as e:
        return None

def get_user_stripe_id_auth0(user_id):
    try:
        access_token = get_access_token()
        url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user_id}"
        headers = {
            'authorization': f"Bearer {access_token}",
            'content-type': "application/json"
        }
        response = requests.get(url, headers=headers)
        stripe_id = response.json()["user_metadata"]["stripe_customer_id"]
        return stripe_id
    except Exception as e:
        return {"status": "failed", "error": str(e)}

def update_user_metadata(user_id, stripe_customer_id):
    try:
        metadata = {"stripe_customer_id": stripe_customer_id}
        access_token = get_access_token()
        url = f"https://{settings.AUTH0_DOMAIN}/api/v2/users/{user_id}"
        payload = {"user_metadata": metadata}
        headers = {
            'authorization': f"Bearer {access_token}",
            'content-type': "application/json"
        }
        response = requests.patch(url, json=payload, headers=headers)
        # return str(response.content.decode('utf-8'))
        return response

    except Exception as e:
        return str(e)