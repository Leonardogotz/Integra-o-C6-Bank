import requests
import logging
from config.config import ZOHO_AUTH_URL, ZOHO_CREDENTIALS

zoho_access_token_cache = {
    "token": None
}

def get_zoho_access_token():
    """ Obtém e armazena o token OAuth 2.0 da Zoho em cache """

    if zoho_access_token_cache["token"]:
        logging.info("Token de acesso da Zoho ainda é válido.")
        return zoho_access_token_cache["token"]

    logging.info("Solicitando novo token de acesso à Zoho...")

    try:
        response = requests.post(
            ZOHO_AUTH_URL,
            data=ZOHO_CREDENTIALS
        )

        if response.status_code == 200:
            token_data = response.json()
            zoho_access_token_cache["token"] = token_data.get("access_token")
            logging.info("Novo token Zoho armazenado com sucesso.")
            return zoho_access_token_cache["token"]
        else:
            logging.error(f"Erro ao obter token da Zoho: {response.text}")
            raise Exception("Falha ao obter token OAuth Zoho")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na solicitação à Zoho: {e}")
        raise
