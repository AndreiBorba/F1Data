from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests, os, logging
load_dotenv()

openf1_username = os.getenv("OPENF1_USERNAME")
openf1_password = os.getenv("OPENF1_PASSWORD")

token_chace = {
    'token': None,
    'expiry': None
}

def get_token(username: str, password: str):
    if token_chace['token'] and token_chace['expiry'] and datetime.now() < token_chace['expiry']:
        logging.info("get_token - reutilizando token")
        return token_chace['token']
    
    logging.info("get_token - solicitando novo token")
    token_url = "https://api.openf1.org/token"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(token_url, data=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()

        expires_in = int(data['expires_in'])

        token_chace['token'] = data['access_token']
        token_chace['expiry'] = datetime.now() + timedelta(seconds=expires_in - 300) # Margem de 300s

        logging.info(f"get_token - novo token obtido (valido por {expires_in}s)")
        return token_chace['token']
    
    return


def make_request_with_token(url, username, password, method='GET', **kwargs):
    token = get_token(username, password)

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.request(method, url, headers=headers, **kwargs)

    if response.status_code == 401:
        logging.info("make_request_with_token - token expirado, renovando")

        token_chace['token'] = None
        token_chace['expiry'] = None

        token = get_token(username, password)
        response = requests.request(method, url, headers=headers, **kwargs)
    
    return response


def get_sessions_by_year(year: int):
    url = "https://api.openf1.org/v1/sessions"

    params = {
        "year": year
    }

    return make_request_with_token(
        url=url,
        username=openf1_username,
        password=openf1_password,
        params=params
    )
