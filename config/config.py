import os
import pathlib

# Configuração da API do C6
C6_API_URL = "https://baas-api-sandbox.c6bank.info/v1/bank_slips/"
C6_AUTH_URL = "https://baas-api-sandbox.c6bank.info/v1/auth/"

C6_CREDENTIALS = {
    "client_id": os.getenv("C6_CLIENT_ID", "ede8508d-c937-49b6-8949-1aeb3e60dcb9"),
    "client_secret": os.getenv("C6_CLIENT_SECRET", "CZV6AyfvVJHcfyyNqqdIVpINRECMMlGn"),
    "grant_type": "client_credentials"
}

# Configuração da API Zoho
ZOHO_API_URL = "https://www.zohoapis.com/books/v3/"
ZOHO_AUTH_URL = "https://accounts.zoho.com/oauth/v2/token"

ZOHO_CREDENTIALS = {
    "client_id": os.getenv("ZOHO_CLIENT_ID", "1000.FZYBSQLVN9TTP8A5USXOMF5PE32X3W"),
    "client_secret": os.getenv("ZOHO_CLIENT_SECRET", "02de551adab46ce882ce0a439c65da11551474596e"),
    "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN", "1000.91f9dd5c087c37703eb058e69b27887b.a262b27993879b66681830be57e3d4ef"),
    "grant_type": "refresh_token"
}

# Certificados SSL/TLS para C6 Bank (Sem CA Cert)
BASE_DIR = pathlib.Path(__file__).parent.resolve()
# Sobe um nível no diretório para encontrar a pasta 'certs'
CERTS_DIR = BASE_DIR.parent / "certs"

CERTS = {
    "client_cert": str(CERTS_DIR / "cert.crt"),
    "client_key": str(CERTS_DIR / "cert.key")
}
print(f"Caminho do certificado: {CERTS['client_cert']}")

# Configuração de logging
LOG_FILE = "logs/app.log"
