import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Factory Backend")

# 5. CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow ALL origins (Vercel, etc.)
    allow_credentials=False, # No cookies needed for this app
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
TEMPLATE_FILENAME = "AI_API_Test_Template.xlsx"
ARTIFACTS_DIR = Path("artifacts_storage")
TEMPLATE_PATH = ARTIFACTS_DIR / TEMPLATE_FILENAME

# Ensure artifacts dir exists
if not ARTIFACTS_DIR.exists():
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

# --- Integrated Existing Functionality ---
try:
    from routers import processing
    app.include_router(processing.router)
    logger.info("Successfully loaded 'processing' router.")
except Exception as e:
    logger.error(f"Failed to load 'processing' router: {e}")
    # We continue so the basic server still runs (Connection Refused fix)

# 7. Health Check
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"status": "running", "message": "Backend is active. Docs at /docs"}

# 2. Template Download API
@app.get("/api/template")
def download_template():
    """Returns the AI_API_Test_Template.xlsx file."""
    
    # Generate if missing (Best Effort)
    if not TEMPLATE_PATH.exists():
        logger.info(f"Template {TEMPLATE_FILENAME} not found. Generating default...")
        try:
            generate_default_template(TEMPLATE_PATH)
        except Exception as e:
            with open("error.log", "w") as f:
                f.write(str(e))
                import traceback
                traceback.print_exc(file=f)
            logger.error(f"Failed to generate template: {e}")
            raise HTTPException(status_code=404, detail="Template file not found and generation failed.")

    if not TEMPLATE_PATH.exists():
        raise HTTPException(status_code=404, detail="Template file not found.")

    return FileResponse(
        path=TEMPLATE_PATH,
        filename=TEMPLATE_FILENAME,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

def generate_default_template(path: Path):
    """Helper to create a valid .xlsx if missing using pandas."""
    import pandas as pd
    import json
    
    # Exact ordered columns as requested by user
    columns = [
        "Ref ID", "Module/Feature", "API Name", "HTTP Method", "Endpoint URL",
        "Headers Required", "Request Payload (JSON example)", "URL Params",
        "Expected Response (Success)", "Token Variable", "Is Token Generator", "Auth Scope"
    ]
    
    # Sheet 1: APIs
    apis_data = [
        {
            "Ref ID": "AUTH-01",
            "Module/Feature": "Authentication",
            "API Name": "Get Auth Token",
            "HTTP Method": "POST",
            "Endpoint URL": "getAuthToken", 
            "Headers Required": "Content-Type: application/x-www-form-urlencoded",
            "Request Payload (JSON example)": json.dumps({
                "login.username": "demo_user",
                "login.password": "secret123",
                "tenantId": "demo-tenant"
            }),
            "URL Params": "",
            "Expected Response (Success)": '{"token": "<authToken>"}',
            "Token Variable": "authToken",
            "Is Token Generator": "TRUE",
            "Auth Scope": ""
        },
        {
            "Ref ID": "USER-01",
            "Module/Feature": "Users",
            "API Name": "Get Profile",
            "HTTP Method": "GET",
            "Endpoint URL": "getCustomerProfileDetails",
            "Headers Required": "token: {{authToken}}",
            "Request Payload (JSON example)": "",
            "URL Params": json.dumps({
                "customerId": "20955",
                "fullDetails": "true"
            }),
            "Expected Response (Success)": '{"id": 20955}',
            "Token Variable": "",
            "Is Token Generator": "FALSE",
            "Auth Scope": ""
        }
    ]
    
    # Sheet 2: Environments
    env_data = [
        {"Variable": "base_url", "Value": "https://api.example.com/v2"},
        {"Variable": "tenantId", "Value": "demo-tenant"}
    ]
    
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        # Enforce column order for APIs sheet
        df_apis = pd.DataFrame(apis_data)
        # Ensure that the DataFrame has all the columns in the specified order.
        # This handles cases where some keys might be missing in dicts (filled with NaN/None)
        # and reorders them to match the user's requirement exactly.
        df_apis = df_apis.reindex(columns=columns)
        
        df_apis.to_excel(writer, sheet_name='apis', index=False)
        
        # Environments sheet
        pd.DataFrame(env_data).to_excel(writer, sheet_name='environments', index=False)

    logger.info(f"Generated default template at {path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
