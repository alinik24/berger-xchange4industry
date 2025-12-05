# BergerConnect X - Sovereign Data Exchange Prototype

## Overview
**BergerConnect X** is a Hackathon prototype designed for **Werkzeugbau Berger** to securely share Digital Twin assets (BOMs, Steel Certs, Timelines) with customers like **Stripmeier**. 

It leverages the **International Data Spaces (IDS)** and **Gaia-X** principles to ensure **Data Sovereignty**. The system uses **Eclipse EDC** (Eclipse Dataspace Components) as the connector technology to enforce Usage Control policies (e.g., "Delete after 7 days", "Log all access").

## Architecture
The system consists of a centralized Digital Twin Database (FastAPI) and a Unified Dashboard (Streamlit) for both the Provider (Berger) and Consumer (Customer).

```mermaid
graph TD
    subgraph "Werkzeugbau Berger (Provider)"
        A[Streamlit Dashboard (View A)] -->|Manage Assets| B(FastAPI Backend)
        B -->|Read| D[(Data Folder / JSON)]
        B -->|Connects to| E[Provider EDC]
    end
    
    subgraph "Customer Stripmeier (Consumer)"
        F[Streamlit Dashboard (View B)] -->|Request Access| G[Consumer EDC]
    end
    
    E <-->|IDS Protocol (Contract Negotiation)| G
    G -->|Proxy Data| B
```

## Folder Structure
- `/backend`: FastAPI application serving the Digital Twin data.
- `/frontend`: Streamlit application for the User Interface.
- `/infrastructure`: Docker Compose setup for the ecosystem.
- `/data`: JSON files representing the raw asset data.
- `/docs`: Documentation.

## How to Run
Prerequisites: Docker and Docker Compose.

1. Navigate to the infrastructure folder:
   ```bash
   cd infrastructure
   ```

2. Start the ecosystem:
   ```bash
   docker-compose up --build
   ```

3. Access the Dashboard:
   - Open your browser at `http://localhost:8501`

4. Access the API Docs:
   - Open `http://localhost:8000/docs`

## Features
- **Role-Based Access**: Switch between Berger (Provider) and Customer views.
- **Digital Twin**: View real-time status and BOM of Tool 2201.
- **Usage Control Simulation**: Mocked negotiation of IDS contracts before data download.
- **Bidirectional Flow**: Customers can upload signed approval documents back to the provider.
