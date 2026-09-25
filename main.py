import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from fastapi.responses import JSONResponse

app = FastAPI(title="Vehicle RC Lookup API")

# Credits Configuration
DEVELOPER_ID = "@wwnlf"
CHANNEL_NAME = "@ix_mrdeath"
CHANNEL_LINK = "https://t.me/ix_mrdeath"
CREDIT_SUPPORT = "@madara_x_support"

# API Key Protection
API_KEY = os.getenv("API_KEY", "baddie")
API_KEY_NAME = "api_key"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Source API Config
RC_SOURCE_URL = "https://madara-alapi.onrender.com/search"
RC_SOURCE_KEY = "madara"


def verify_api_key(
    api_key_q: str = Security(api_key_query),
    api_key_h: str = Security(api_key_header)
):
    if api_key_q == API_KEY or api_key_h == API_KEY:
        return True
    raise HTTPException(
        status_code=401,
        detail={
            "status": "error",
            "message": "Invalid or Missing API Key.",
            "developer": DEVELOPER_ID,
            "credit": CREDIT_SUPPORT
        }
    )


@app.get("/")
def home():
    return {
        "status": "running",
        "service": "Vehicle RC Lookup API",
        "developer": DEVELOPER_ID,
        "channel": CHANNEL_NAME,
        "support": CREDIT_SUPPORT
    }


@app.get("/search")
async def search_vehicle(
    vnum: str = Query(..., description="Vehicle registration number"),
    authenticated: bool = Security(verify_api_key)
):
    clean_vnum = str(vnum).strip().upper().replace(" ", "")

    try:
        # Render free-tier spin-up ke liye timeout 25s
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(
                RC_SOURCE_URL,
                params={"api_key": RC_SOURCE_KEY, "vnum": clean_vnum}
            )

        if response.status_code == 200:
            res_json = response.json()

            # Agar source status false de ya data na ho
            if not res_json.get("status"):
                return JSONResponse(
                    status_code=404,
                    content={
                        "status": "not_found",
                        "message": "Vehicle details not found.",
                        "developer": DEVELOPER_ID
                    }
                )

            return {
                "status": "success",
                "system_credits": {
                    "developer": DEVELOPER_ID,
                    "credit": CREDIT_SUPPORT,
                    "channel_link": CHANNEL_LINK
                },
                "registration_number": res_json.get("registration_number", clean_vnum),
                "owner_information": res_json.get("owner_information", {}),
                "vehicle_information": res_json.get("vehicle_information", {}),
                "technical_specifications": res_json.get("technical_specifications", {}),
                "registration_details": res_json.get("registration_details", {}),
                "insurance_details": res_json.get("insurance_details", {}),
                "pollution_certificate": res_json.get("pollution_certificate", {}),
                "finance_details": res_json.get("finance_details", {}),
                "address": res_json.get("address", {}),
                "other_information": res_json.get("other_information", {})
            }

        return JSONResponse(
            status_code=response.status_code,
            content={
                "status": "not_found",
                "message": "Source API returned error or vehicle not found.",
                "developer": DEVELOPER_ID
            }
        )

    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Source server took too long to respond or is offline.",
                "developer": DEVELOPER_ID
            }
        )
