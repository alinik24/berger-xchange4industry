import pypdf
import os

def extract_timeline_from_pdf(filepath: str, force_mock: bool = False):
    """
    Simulates parsing a PDF to extract Gantt chart data.
    In a real app, this would use OCR or text extraction.
    For the demo, we detect the file content/name and return structured data.
    """
    print(f"DEBUG: Extracting timeline from {filepath}, force_mock={force_mock}")
    
    if force_mock:
        print("DEBUG: Force mock enabled, returning mock data directly.")
        return {
            "milestones": [
                {"phase": "Auftragserteilung", "status": "Completed", "date": "2025-11-01", "responsible": "Vertrieb"},
                {"phase": "Konstruktion (CAD)", "status": "Completed", "date": "2025-11-15", "responsible": "Konstruktion"},
                {"phase": "Materialbeschaffung", "status": "Completed", "date": "2025-11-20", "responsible": "Einkauf"},
                {"phase": "Kontur erodieren", "status": "In Progress", "progress_percent": 45, "start_date": "2025-11-27", "estimated_completion": "2025-12-05", "responsible": "Fertigung"},
                {"phase": "Montage & Tuschieren", "status": "Pending", "estimated_start": "2025-12-06", "responsible": "Montage"},
                {"phase": "Qualitätskontrolle", "status": "Pending", "estimated_start": "2025-12-10", "responsible": "QS"}
            ]
        }

    try:
        reader = pypdf.PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            
        # "Smart" Parsing Logic for the Demo
        # If we detect "Ablaufplan" or "Terminplan", we generate the specific demo data
        if "Ablaufplan" in filepath or "Terminplan" in filepath or "Kontur" in text:
            return {
                "milestones": [
                    {"phase": "Auftragserteilung", "status": "Completed", "date": "2025-11-01", "responsible": "Vertrieb"},
                    {"phase": "Konstruktion (CAD)", "status": "Completed", "date": "2025-11-15", "responsible": "Konstruktion"},
                    {"phase": "Materialbeschaffung", "status": "Completed", "date": "2025-11-20", "responsible": "Einkauf"},
                    {"phase": "Kontur erodieren", "status": "In Progress", "progress_percent": 45, "start_date": "2025-11-27", "estimated_completion": "2025-12-05", "responsible": "Fertigung"},
                    {"phase": "Montage & Tuschieren", "status": "Pending", "estimated_start": "2025-12-06", "responsible": "Montage"},
                    {"phase": "Qualitätskontrolle", "status": "Pending", "estimated_start": "2025-12-10", "responsible": "QS"}
                ]
            }
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    
    return None
