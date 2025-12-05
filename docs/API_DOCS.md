# Digital Twin API Documentation

The Backend is built with **FastAPI** and serves as the "Digital Twin" repository for the tools.

## Base URL
`http://localhost:8000`

## Endpoints

### 1. Get Tool Metadata
**GET** `/api/tool/{id}`

Retrieves the full Asset Administration Shell (AAS) structure for a specific tool.

**Parameters:**
- `id` (path): The unique ID of the tool (e.g., `2201`).

**Response (200 OK):**
```json
{
  "id": "2201",
  "name": "Visitenkarten ETUI",
  "description": "High-precision injection mold...",
  "owner": "Werkzeugbau Berger",
  "status": "Active",
  "assets": {
    "bom": { ... },
    "timeline": { ... },
    "steel_cert": "CERT-S-2201-V1.pdf"
  },
  "approvals": []
}
```

### 2. Approve Tool / Upload Document
**POST** `/api/tool/{id}/approve`

Allows the customer to upload a signed approval document (e.g., "Milestone Acceptance").

**Parameters:**
- `id` (path): The unique ID of the tool.
- `file` (form-data): The file to upload.

**Response (200 OK):**
```json
{
  "message": "Approval document received and processed successfully.",
  "approval_record": {
    "filename": "signed_acceptance.pdf",
    "timestamp": "2023-12-03T10:00:00",
    "status": "Received"
  }
}
```
