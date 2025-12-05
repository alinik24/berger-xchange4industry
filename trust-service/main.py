from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI(
    title="Gaia-X Trust Service (Mock)",
    description="Simulates the DAPS (Identity) and Federated Catalog services of the Gaia-X Trust Framework.",
    version="1.0.0"
)

class Participant(BaseModel):
    id: str
    name: str
    role: str
    status: str
    certificate_expiry: str

# Mock Registry of Trusted Participants
participants_db = [
    {
        "id": "did:web:werkzeugbau-berger.com",
        "name": "Werkzeugbau Berger",
        "role": "Provider",
        "status": "Verified",
        "certificate_expiry": "2026-12-31"
    },
    {
        "id": "did:web:stripmeier.com",
        "name": "Stripmeier",
        "role": "Consumer",
        "status": "Verified",
        "certificate_expiry": "2026-12-31"
    }
]

@app.get("/")
def read_root():
    return {"service": "Gaia-X Trust Framework", "status": "Online"}

@app.get("/api/trust/participants", response_model=List[Participant])
def get_participants():
    """
    Returns the list of participants in the Federated Catalog.
    """
    return participants_db

@app.get("/api/trust/verify/{participant_id}")
def verify_participant(participant_id: str):
    """
    Simulates DAPS verification of a participant's identity.
    """
    participant = next((p for p in participants_db if p["id"] == participant_id), None)
    if participant:
        return {
            "verified": True,
            "participant": participant,
            "token": f"mock-daps-token-{participant_id}-{datetime.datetime.now().timestamp()}"
        }
    return {"verified": False, "error": "Participant not found in Trust Anchor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
