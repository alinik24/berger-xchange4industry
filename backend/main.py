from fastapi import FastAPI
from routers import asset_mgmt, policy_engine, data_ingestion, registry
import models, database
import os
import json

app = FastAPI(
    title="BergerConnect X - Digital Twin API",
    description="API for the Sovereign Data Exchange prototype. Manages Digital Twin assets for Werkzeugbau Berger.",
    version="2.0.0"
)

# --- DATABASE INIT ---
models.Base.metadata.create_all(bind=database.engine)

# --- ROUTERS ---
app.include_router(asset_mgmt.router)
app.include_router(policy_engine.router)
app.include_router(data_ingestion.router)
app.include_router(registry.router)

# --- CONFIGURATION ---
DATA_DIR = os.getenv("DATA_DIR", "../data")

# --- INITIAL DATA LOADING ---
@app.on_event("startup")
async def startup_event():
    # Initialize DB with default tool if empty
    db = database.SessionLocal()
    try:
        # Initialize Registry Data
        registry.initialize_registry_data(db)

        if db.query(models.Tool).count() == 0:
            print("Initializing Database with Default Tool 2201...")
            
            # Load initial JSON data
            bom_data = None
            timeline_data = None
            
            try:
                with open(os.path.join(DATA_DIR, "bom.json"), 'r') as f:
                    bom_data = json.load(f)
                with open(os.path.join(DATA_DIR, "timeline.json"), 'r') as f:
                    timeline_data = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load initial JSON data: {e}")

            default_tool = models.Tool(
                id="2201",
                name="Visitenkarten ETUI",
                description="High-precision injection mold for business card cases.",
                owner="Werkzeugbau Berger",
                status="Active",
                assets={
                    "bom": bom_data,
                    "timeline": timeline_data,
                    "steel_cert": "CERT-S-2201-V1.pdf",
                    "documents": []
                }
            )
            db.add(default_tool)
            db.commit()
            print("Database Initialized.")
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "BergerConnect X Digital Twin API (Microservices Architecture) is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
