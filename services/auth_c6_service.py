import requests
import logging
import base64
from config.config import C6_API_URL, C6_AUTH_URL

# Cache para token de acesso
c6_access_token_cache = {}

def get_c6_access_token(config):
    """Obtém o token de acesso para a API do C6 usando a configuração especificada."""
    try:
        if c6_access_token_cache.get(config["client_id"]):
            return c6_access_token_cache[config["client_id"]]

        response = requests.post(
            C6_AUTH_URL,
            data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "grant_type": config["grant_type"]
            },
            cert=(config["cert"]["client_cert"], config["cert"]["client_key"]),
            verify=True
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            c6_access_token_cache[config["client_id"]] = token
            logging.info("Token de acesso do C6 obtido com sucesso.")
            return token
        else:
            logging.error(f"Erro ao obter token do C6: {response.text}")
            raise Exception("Falha na autenticação do C6")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na autenticação do C6: {e}")
        raise

def send_to_c6(data, config):
    """Envia os dados para a API do C6 e gera o boleto."""
    try:
        token = get_c6_access_token(config)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.post(
            C6_API_URL,
            json=data,
            headers=headers,
            cert=(config["cert"]["client_cert"], config["cert"]["client_key"]),
            verify=True
        )

        if response.status_code in [200, 201]:
            logging.info(f"Boleto gerado com sucesso: {response.json()}")
            boleto_id = response.json().get("id")
            return consult_boleto(boleto_id, config)  # Consulta o boleto emitido
        elif response.status_code == 401:
            logging.warning("Token expirado, renovando...")
            c6_access_token_cache.pop(config["client_id"], None)
            return send_to_c6(data, config)
        else:
            logging.error(f"Erro na API do C6: {response.text}")
            raise Exception(f"Erro ao gerar boleto: {response.text}")

    except requests.exceptions.SSLError as e:
        logging.error(f"Erro de certificado SSL: {e}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na requisição ao C6: {e}")
        raise

def consult_boleto(boleto_id, config):
    """Consulta os detalhes de um boleto na API do C6."""
    try:
        token = get_c6_access_token(config)

        url = f"{C6_API_URL}/{boleto_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(
            url,
            headers=headers,
            cert=(config["cert"]["client_cert"], config["cert"]["client_key"]),
            verify=True
        )

        if response.status_code == 200:
            boleto_data = response.json()
            logging.info(f"Boleto consultado com sucesso: {boleto_data}")
            return boleto_data
        else:
            logging.error(f"Erro ao consultar boleto: {response.text}")
            raise Exception(f"Erro ao consultar boleto: {response.text}")

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro ao consultar boleto no C6: {e}")
        raise

def decode_boleto_pdf(base64_pdf, pdf_path):
    """Decodifica o PDF em Base64 e salva no caminho especificado."""
    try:
        decoded_pdf = base64.b64decode(base64_pdf)
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(decoded_pdf)
        logging.info(f"PDF do boleto salvo em {pdf_path}.")
        return pdf_path
    except Exception as e:
        logging.exception(f"Erro ao decodificar e salvar o PDF: {e}")
        raise
