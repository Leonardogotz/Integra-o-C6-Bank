from flask import Flask, request, jsonify
import requests
import logging
from config.config import C6_API_URL, CERTS

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(level=logging.INFO)

@app.route('/zoho-webhook', methods=['POST'])
def receive_zoho_data():
    """Recebe dados do Zoho Books e envia para o C6 via mTLS"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        logging.info(f"Recebido JSON do Zoho: {data}")

        # Enviar para API do C6
        response = send_to_c6(data)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        logging.error(f"Erro ao processar a requisição: {e}")
        return jsonify({"error": str(e)}), 500


def send_to_c6(data):
    """Envia dados para a API do C6 usando mTLS sem CA"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer SEU_TOKEN_AQUI"
        }

        response = requests.post(
            C6_API_URL,
            json=data,
            headers=headers,
            cert=(CERTS["client_cert"], CERTS["client_key"]),  # Apenas cert e key
            verify=False  # Ignorar verificação da CA
        )

        logging.info(f"Resposta da API do C6: {response.status_code} {response.text}")
        return response

    except requests.exceptions.RequestException as e:
        logging.error(f"Erro na chamada da API do C6: {e}")
        raise


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
