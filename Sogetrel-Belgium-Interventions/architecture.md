# 🏗 Architecture Overview

## Data Flow
PDF Reports (Technicians)
        ↓
Python PDF Parser (Regex + PyMuPDF)
        ↓
Structured Dataset (Excel / CSV)
        ↓
Power BI Data Model
        ↓
Operational Dashboards & KPIs

---

## Key Challenges Solved
- Inconsistent PDF formats
- Missing fields and partial timestamps
- Non-standard technician inputs
- Time slot vs real arrival/departure alignment
- Robust error handling and fallback extraction

---

## Why This Architecture
- Lightweight (no database required)
- Easy deployment for operational teams
- Fully auditable raw source (PDFs)
- Scalable to thousands of reports
