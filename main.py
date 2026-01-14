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

FORMS_ID = {
    "medical_form": "242124684987064",
    "province_form": "260126850265353",
    "europe_form": "260053531330341",
    "special_form" : "260054216669357"
}

JOTFORM_BASE_URL = "https://eu-api.jotform.com"

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
# Approval workflow
# --------------------------------------------------
@app.get("/approval")
async def jotform_approval(request: Request):
    data = await request.json()

    submission_id = data.get("submission_id")
    approval_result = data.get("approval_result")

    if not submission_id or not approval_result:
        raise HTTPException(status_code=400, detail="Missing data")

    payload = {
        "submission[approval_status]": approval_result,
        "submission[approval_date]": datetime.utcnow().isoformat(),
    }

    response = requests.post(
        f"{JOTFORM_API_BASE}/submission/{submission_id}",
        params={"apiKey": JOTFORM_API_KEY},
        data=payload,
        timeout=10
    )
    
# --------------------------------------------------
# Endpoint test : lecture des soumissions
# --------------------------------------------------
@app.get("/generate_csv")
def log_form_columns():
    for form in FORMS_ID.keys():

        form_id = FORMS_ID[form]
        
        url = f"{JOTFORM_BASE_URL}/form/{form_id}/submissions"
        params = {
            "apiKey": JOTFORM_API_KEY,
            "limit": 10  # on prend UNE soumission pour extraire les colonnes
        }
    
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        submissions = data.get("content", [])

        print(form)
        print(data)
        print(submissions)
        
        if not submissions:
            logger.info("Aucune soumission trouvée.")
            continue
            
        logger.info(submissions)
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
        #logger.info("COLONNES FORMULAIRE : %s", " | ".join(columns))

    return
