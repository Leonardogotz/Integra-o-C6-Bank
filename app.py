from flask import Flask, request, jsonify
import logging
from services.auth_c6_service import send_to_c6, decode_boleto_pdf
from services.auth_zoho_service import get_zoho_access_token, upload_attachment_to_zoho

app = Flask(__name__)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

@app.route('/zoho-webhook', methods=['POST'])
def receive_zoho_data():
    """Recebe dados do Zoho, gera boleto no C6 e anexa o PDF ao Zoho."""
    try:
        # Recebe o JSON enviado pelo Zoho
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        logging.info(f"Recebido JSON do Zoho: {data}")

        # Montar o JSON para a API do C6 com base nos dados do Zoho
        boleto_data = {
            "external_reference_id": data.get("external_reference_id"),
            "amount": data.get("amount"),
            "due_date": data.get("due_date"),
            "instructions": [data.get("instructions")],
            "payer": {
                "name": data.get("name"),
                "tax_id": data.get("tax_id"),
                "email": data.get("email"),
                "address": {
                    "street": data.get("address", {}).get("street"),
                    "number": data.get("address", {}).get("number"),
                    "complement": data.get("address", {}).get("complement"),
                    "city": data.get("address", {}).get("city"),
                    "state": data.get("address", {}).get("state"),
                    "zip_code": data.get("address", {}).get("zip_code"),
                }
            }
        }

        # Gera o boleto no C6 (inclui emissão e consulta)
        boleto_response = send_to_c6(boleto_data)

        # Decodifica o PDF do boleto retornado
        pdf_base64 = boleto_response.get("base64_pdf_file")
        pdf_path = decode_boleto_pdf(pdf_base64)

        # Faz o upload do PDF para a fatura no Zoho
        zoho_token = get_zoho_access_token()
        invoice_id = data.get("invoice_id")
        upload_attachment_to_zoho(invoice_id, pdf_path, zoho_token)

        return jsonify({"message": "Boleto gerado e anexado com sucesso"}), 200

    except Exception as e:
        logging.error(f"Erro no processamento: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
