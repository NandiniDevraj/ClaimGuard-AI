# 🏥 Healthcare Prior Authorization Platform

An AI-powered prior authorization and coverage intelligence platform 
that acts as a real-time intelligence bridge between clinical 
documentation and insurance policy logic.

## 🎯 Problem Statement

- Physicians spend 15+ hours/week on prior authorization paperwork
- ~20% claim denial rate due to documentation gaps
- Patients face surprise billing from coverage mismatches

## 🤖 Solution

A multi-agent AI system that:
1. Reads insurance policy documents and extracts coverage requirements
2. Analyzes clinical documentation for completeness
3. Identifies exact gaps that will cause claim denial
4. Generates persona-specific recommendations for physicians, 
   billing staff, and patients

## 🏗️ Architecture
```
Clinical Notes + Insurance PDFs
         ↓
   PII Scrubber (HIPAA)
         ↓
   Document Parser + Chunker
         ↓
   ChromaDB Vector Store
         ↓
┌────────────────────────────┐
│     LangGraph Orchestrator  │
│  ┌──────────────────────┐  │
│  │ 1. Policy Agent      │  │
│  │ 2. Clinical Agent    │  │
│  │ 3. Gap Detector      │  │
│  │ 4. Recommendation    │  │
│  └──────────────────────┘  │
└────────────────────────────┘
         ↓
   FastAPI Backend
         ↓
   Streamlit Frontend
   (3 Personas: Doctor/Billing/Patient)
```

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Agent Orchestration | LangGraph |
| Vector Database | ChromaDB |
| Embeddings | OpenAI text-embedding-3-small |
| PII Scrubbing | Microsoft Presidio (HIPAA) |
| NLP | spaCy |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Database | SQLite / PostgreSQL |
| Language | Python 3.11 |

## 🚀 Quick Start

### Prerequisites
- Python 3.11
- OpenAI API key

### Installation
```bash
# Clone the repo
git clone https://github.com/NandiniDevraj/healthcare-auth-platform.git
cd healthcare-auth-platform

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install torch==2.4.1
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### Configuration
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

### Run
```bash
# Terminal 1 — Start API
uvicorn app.api.main:app --reload --port 8000

# Terminal 2 — Start Frontend
streamlit run frontend/streamlit_app.py
```

Open http://localhost:8501

## 💡 Key Features

- **HIPAA Compliant** — Microsoft Presidio scrubs all PHI/PII 
  before any LLM processing
- **Multi-Agent Architecture** — LangGraph orchestrates 4 
  specialized AI agents
- **3 Persona Views** — Different interfaces for Physician, 
  Billing Staff, and Patient
- **Approval Likelihood Score** — AI predicts authorization 
  approval probability
- **Actionable Recommendations** — Specific steps to fix 
  documentation gaps
- **PDF Upload** — Upload real insurance policy PDFs
- **Full Audit Trail** — Every analysis saved to database

## 📊 Sample Output
```
Procedure: Spinal Fusion L4-L5 (CPT 22612)
Current Approval Likelihood: 40%
After Implementing Recommendations: 75%
Improvement: +35%

Critical Gaps Found:
- Physical therapy duration not documented (need 6 weeks)
- MRI report missing radiologist interpretation
- Conservative treatment dates incomplete
```

## 🔒 HIPAA Compliance

All patient data is scrubbed of PHI before processing:
- Names → [PATIENT_NAME]
- SSNs → [SSN_REDACTED]  
- Phone numbers → [PHONE_REDACTED]
- Dates → [DATE_REDACTED]
- Locations → [LOCATION_REDACTED]

## 🗺️ Future Roadmap

- [ ] Fine-tuned BERT classifier for authorization likelihood
- [ ] EHR/FHIR integration
- [ ] Real insurance policy database
- [ ] Multi-language support
- [ ] Cloud deployment (AWS/GCP)

## 👩‍💻 Author

**Nandini Devaraj**  
MS Artificial Intelligence — Illinois Institute of Technology  
[LinkedIn](https://www.linkedin.com/in/nandinidevraj/) | [Portfolio](https://nandinidevaraj.com/)