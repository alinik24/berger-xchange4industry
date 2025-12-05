# BergerConnect X - Sovereign Data Exchange Demo Guide

This guide provides a step-by-step walkthrough of the **BergerConnect X** prototype, demonstrating the Sovereign Data Exchange features, Gaia-X Trust Framework integration, and the Microservices architecture.

## Ì∫Ä System Setup

Ensure the entire infrastructure is running:

```bash
cd infrastructure
docker-compose up -d --build
```

Access the **User Interface** at: [http://localhost:8501](http://localhost:8501)

---

## Ìæ≠ Demo Walkthrough

### **Scenario 1: The Provider (Werkzeugbau Berger)**
*Goal: Create a Digital Twin, attach data, and define usage policies.*

1.  **Login**:
    *   Select **"Internal (Werkzeugbau Berger)"** from the sidebar.
    *   *Observation*: Note the "IDS Connector: Provider-EDC (Online)" status.

2.  **Create Digital Twin**:
    *   Go to **"Asset Management"** -> **"Create New Digital Twin"**.
    *   **ID**: `5500`
    *   **Name**: `Injection Mold V8`
    *   **Description**: `High-performance mold for automotive parts.`
    *   Click **"Create Tool"**.
    *   *Result*: The new tool appears in the dropdown selector.

3.  **Attach Data & Parse PDF**:
    *   Select `Injection Mold V8` from the dropdown.
    *   Go to **"Document Repository (Local)"**.
    *   Select `Beispiel Ablaufplan.pdf` (or similar).
    *   Category: **"Timeline"**.
    *   Click **"Attach to Tool"**.
    *   *Result*: The system parses the PDF, extracts the Gantt chart data, and updates the Digital Twin's timeline automatically.

4.  **Define Usage Policy**:
    *   In the **"Publish Assets via IDS"** column.
    *   Select **"N-Times Usage"**.
    *   Max Downloads: `3`.
    *   Click **"Publish & Enforce Policy"**.
    *   *Result*: The asset is now "locked" under a contract.

---

### **Scenario 2: The Consumer (Stripmeier)**
*Goal: Verify trust, view status, and securely exchange data.*

1.  **Switch Role**:
    *   Select **"External (Customer: Stripmeier)"** in the sidebar.
    *   Select `Injection Mold V8` (or the tool you created).

2.  **Gaia-X Trust Verification**:
    *   Click **"Request Live Status Update"**.
    *   *Observation*: Watch for the toast notification: **"Gaia-X Trust Anchor: Identity Verified ‚úÖ"**.
    *   *Technical*: The frontend calls the `trust-service` to verify the Provider's DID (`did:web:werkzeugbau-berger.com`) before accepting data.

3.  **Traffic Light Status System**:
    *   Look at the **"Production Status"** section.
    *   You will see a large **Green**, **Yellow**, or **Red** light.
    *   *Logic*: This is derived dynamically from the parsed PDF timeline. If a milestone is "Delayed", it turns Yellow.

4.  **Secure Download**:
    *   Scroll to **"Secure Downloads"**.
    *   Click **"Download"** on the attached PDF.
    *   *Observation*: The "Contract Audit Log" (visible in Provider view) will record this action.

---

### **Scenario 3: Sovereign Change Loop**
*Goal: Securely upload an approval document back to the provider.*

1.  **Upload Approval**:
    *   Scroll to **"Secure Approval Uplink"**.
    *   Upload a dummy file (e.g., an image or PDF) representing a "Signed Change Request".
    *   Click **"Secure Upload"**.
    *   *Result*: Success message "Approval transmitted securely...".

2.  **Verify Receipt (Provider)**:
    *   Switch back to **"Internal (Werkzeugbau Berger)"**.
    *   Look at the **"Received Approvals"** table at the bottom.
    *   *Result*: You will see the file you just uploaded, timestamped and logged.

---

## ÌøóÔ∏è Architecture Highlights

*   **Microservices Backend**: The system is split into `asset_mgmt`, `policy_engine`, `data_ingestion`, and `pdf_parsing` routers.
*   **Structured DB**: All data is persisted in a **PostgreSQL** database (`ids_postgres` container).
*   **Trust Service**: A dedicated `trust-service` container simulates the Gaia-X Federated Catalog and DAPS.
*   **Frontend**: Streamlit UI with dynamic role-switching and real-time API integration.
