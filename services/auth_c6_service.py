import requests
import logging
import time
from config.config import C6_AUTH_URL, C6_CREDENTIALS, CERTS

# Definição global da variável de cache para o token do C6
c6_access_token_cache = {
    "token": None,
    "expires_at": 0
}

def get_c6_access_token():
    """ Obtém e armazena o token OAuth 2.0 do C6 em cache """
    global c6_access_token_cache  # Garante que a variável global seja usada

    current_time = int(time.time())

    # Verifica se o token ainda é válido
    if c6_access_token_cache["token"] and c6_access_token_cache["expires_at"] > current_time:
        logging.info("Token de acesso do C6 ainda é válido.")
        return c6_access_token_cache["token"]

    logging.info("Solicitando novo token de acesso ao C6...")

    try:
        response = requests.post(
            C6_AUTH_URL,
            data=C6_CREDENTIALS,
            cert=(CERTS["client_cert"], CERTS["client_key"]),
            verify=False  # Ignorar verificação CA se não for necessária
        )

        if response.status_code == 200:
            token_data = response.json()
            c6_access_token_cache["token"] = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            c6_access_token_cache["expires_at"] = current_time + expires_in

            logging.info("Novo token C6 armazenado com sucesso.")
            return c6_access_token_cache["token"]
        else:
            logging.error(f"Erro ao obter token do C6: {response.text}")
            raise Exception("Falha ao obter token OAuth C6")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na solicitação ao C6: {e}")
        raise
