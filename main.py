from fastapi import FastAPI
import requests
import logging
import os

# --------------------------------------------------
# Configuration logging (logs visibles dans Render)
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Configuration Jotform
# --------------------------------------------------
JOTFORM_API_KEY = os.getenv("JOTFORM_API_KEY")

FORMS = {
    "medical_form": {
        "id": "242124684987064",
        "name": "formulaire médical"
    }
}

JOTFORM_BASE_URL = "https://api.jotform.com"

# --------------------------------------------------
# FastAPI app
# --------------------------------------------------
app = FastAPI(title="Jotform Data Service")

# --------------------------------------------------
# Healthcheck (obligatoire pour Render)
# --------------------------------------------------
@app.get("/")
def healthcheck():
    return {"status": "ok"}

# --------------------------------------------------
# Endpoint test : lecture des soumissions
# --------------------------------------------------
@app.get("/forms/{form_key}/columns")
def log_form_columns(form_key: str):
    if form_key not in FORMS:
        return {"error": "Form not found"}

    form_id = FORMS[form_key]["id"]

    url = f"{JOTFORM_BASE_URL}/form/{form_id}/submissions"
    params = {
        "apiKey": JOTFORM_API_KEY,
        "limit": 1  # on prend UNE soumission pour extraire les colonnes
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    submissions = data.get("content", [])

    if not submissions:
        logger.info("Aucune soumission trouvée.")
        return {"message": "No submissions found"}

    submission = submissions[0]

    columns = []

    # Champs du formulaire
    for answer in submission["answers"].values():
        columns.append(answer["text"])

    # Champs système intéressants
    columns.extend([
        "Submission ID",
        "Created At",
        "Approval Status"
    ])

    # 🔥 LOG IMPORTANT (ce que tu as demandé)
    logger.info("COLONNES FORMULAIRE : %s", " | ".join(columns))

    return {
        "form": FORMS[form_key]["name"],
        "columns": columns
    }
