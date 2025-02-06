import os
import pathlib

# Diretório base e de certificados
BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()
CERTS_DIR = BASE_DIR / "certs"

# Configurações para diferentes filiais
FILIAIS = {
    "Toolkit": {
        # CLIENTE_ID: 6d651c51-5c59-4c2c-8e56-19bc19a4b298
        # CLIENTE_SECRET: vw67M2S92fsWVAVgAkGgJmm6e9uzvzGd
        "client_id": os.getenv("C6_CLIENT_ID_TOOLKIT", "4804b8af-0f37-40f9-a8ae-a6f90da3d2f4"),
        "client_secret": os.getenv("C6_CLIENT_SECRET_TOOLKIT", "LJL7MoFDnKtTJS2Xs5dSu2ku7HAPKtrN"),
        "cert": {
            "client_cert": str(CERTS_DIR / "certToolKit.crt"),
            "client_key": str(CERTS_DIR / "certToolKit.key")
        },
        "grant_type": "client_credentials"
    },
    "Inteligente TI": {
        # CLIENTE_ID: 01ea9d70-e868-4964-8f66-695f98a06298
        # CLIENTE_SECRET: 1ZM68PYLrWX2ISzmvx572IGQdeU2nqKJ
        "client_id": os.getenv("C6_CLIENT_ID_INTELIGENTETI", "5f448d96-f686-46f7-90cc-9d167a51778f"),
        "client_secret": os.getenv("C6_CLIENT_SECRET_INTELIGENTETI", "X8wT2jZFeAGOTyMrw9oH4V1uLA20oVsz"),
        "cert": {
            "client_cert": str(CERTS_DIR / "certInteligente.crt"),
            "client_key": str(CERTS_DIR / "certInteligente.key")
        },
        "grant_type": "client_credentials"
    }
}

# Configuração da API do C6 Sandbox
# C6_API_URL = "https://baas-api-sandbox.c6bank.info/v1/bank_slips/"
# C6_AUTH_URL = "https://baas-api-sandbox.c6bank.info/v1/auth/"

# Configuração da API do C6
C6_API_URL = "https://baas-api.c6bank.info/v1/bank_slips/"
C6_AUTH_URL = "https://baas-api.c6bank.info/v1/auth/"

# Configuração da API Zoho (única para todas as filiais)
ZOHO_API_URL = "https://www.zohoapis.com/books/v3/"
ZOHO_AUTH_URL = "https://accounts.zoho.com/oauth/v2/token"
ZOHO_CREDENTIALS = {
    "client_id": os.getenv("ZOHO_CLIENT_ID", "1000.38NHD8V6UA2VT73SCHLUSI7SVKE2ES"),
    "client_secret": os.getenv("ZOHO_CLIENT_SECRET", "2f312b4c81439fafda995253c0b4d33f11c477d1fe"),
    "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN", "1000.da54cea07dcff842c2918cf26363d4fe.02d6639087b45f9ceaf597c2aaee3922"),
    "grant_type": "refresh_token"
}

# Configuração de logging
LOG_FILE = "logs/app.log"
