# BergerConnect X - Sovereign Data Exchange Prototype

## Overview
**BergerConnect X** is a Hackathon prototype designed for **Werkzeugbau Berger** to securely share Digital Twin assets (BOMs, Steel Certs, Timelines) with customers like **Stripmeier**. 

It leverages the **International Data Spaces (IDS)** and **Gaia-X** principles to ensure **Data Sovereignty**. The system uses **Eclipse EDC** (Eclipse Dataspace Components) as the connector technology to enforce Usage Control policies (e.g., "Delete after 7 days", "Log all access").

## Architecture
The system consists of a centralized Digital Twin Database (FastAPI) and a Unified Dashboard (Streamlit) for both the Provider (Berger) and Consumer (Customer).

**Version: 1**
<img width="1408" height="768" alt="Image_zemsz0zemsz0zems" src="https://github.com/user-attachments/assets/4ef9fd49-2a57-4f5c-aa21-bc983d87646d" />

**Version: 2 - High Level**
<img width="2784" height="1536" alt="Image_gba35ugba35ugba3 (1)" src="https://github.com/user-attachments/assets/1d8738bd-8c91-4d68-b5b8-3590b24c50a4" />


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
