from fastapi import FastAPI
import os

app = FastAPI(title="Mock EDC Connector")

PARTICIPANT_ID = os.getenv("EDC_PARTICIPANT_ID", "unknown")

@app.get("/")
def read_root():
    return {
        "message": f"Eclipse EDC Connector ({PARTICIPANT_ID}) is Online",
        "status": "Active",
        "type": "Mock"
    }

@app.get("/api/v1/data")
def get_data():
    return {"message": "This is a mock data plane response."}

@app.get("/api/v1/management/assets")
def get_assets():
    return [{"id": "asset-1", "properties": {"name": "Mock Asset"}}]

if __name__ == "__main__":
    import uvicorn
    # Listen on 8080 inside the container
    uvicorn.run(app, host="0.0.0.0", port=8080)
