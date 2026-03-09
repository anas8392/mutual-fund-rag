# MF Advisor: Mutual Fund RAG Assistant

A robust, fully open-source **Retrieval-Augmented Generation (RAG)** chatbot specifically tailored to provide strictly cited mutual fund advice based on real-time datascraping from Indmoney.

## 🚀 Features
- **Strict Grounding & PII Protection**: Powered by `Groq` and `LLaMA-3.1-8b`, the LLM is tightly constrained to *never* answer from internal knowledge and *never* interact with Personally Identifiable Information (PII).
- **In-Memory Vector Search**: Uses local `FAISS` and HuggingFace's `all-MiniLM-L6-v2` dense embeddings, maximizing portability by avoiding C++ native compilation dependencies limiters on Windows environments.
- **Glassmorphic UI**: A stunning, dependency-free vanilla HTML/JS/CSS frontend served seamlessly alongside the backend.
- **Automated CI/CD Pipelines**: Self-updating financial data logic built into GitHub actions. Scheduled to perform automated NAV/Return scrapings and auto-commit the embedded vector database every day at 10 AM IST.

---

## 🏗️ Architecture Design (8 Phases)

1. **Phase 1: Data Acquisition** (`phase1_data_acquisition/`) - Scrapes comprehensive Mutual Fund schemas directly from the `indmoney.com` endpoints.
2. **Phase 2: Knowledge Base Indexing** (`phase2_knowledge_base/`) - Chunks the raw structured data into natural language queries and builds the numerical representations into a `mutual_funds.index` FAISS vector store.
3. **Phase 3: Retrieval Pipeline** (`phase3_retrieval/`) - Injects the active user query and calculates Cosine similarity against the nearest indexed fund metrics (K-window=4).
4. **Phase 4: Generation Pipeline** (`phase4_generation/`) - Configures the Groq API system persona, instructing the model to behave politely while returning strict source URL citations.
5. **Phase 5: Backend Application** (`phase5_backend/`) - A blazingly fast `FastAPI` application exposing the `/api/chat` LLM streaming logic. 
6. **Phase 6: Frontend Interface** (`phase6_frontend/`) - The polished "Orbita GPT Plus" style web interface.
7. **Phase 7: Automated Updates Scheduler** (`.github/workflows/`) - A YAML pipeline executing a standalone Python orchestrator (`scheduler.py`) through GitHub actions every 24 hours.
8. **Phase 8: Evaluation & Refinement** - Expanded k-neighbors and adjusted source multi-link referencing rules safely.

---

## 💻 Local Setup & Installation

### Prerequisites
- Python 3.10+
- An API Key from **Groq** (`GROQ_API_KEY`) 

### 1. Clone the Repository
```bash
git clone https://github.com/anas8392/mutual-fund-rag.git
cd mutual-fund-rag
```

### 2. Install Dependencies
```bash
pip install playwright beautifulsoup4 sentence-transformers faiss-cpu pandas pydantic python-dotenv groq APScheduler fastapi uvicorn
playwright install chromium
```

### 3. Environment Variables
Create a file named `.env` in the root directory of the project, and add your API Key:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 4. Running the Application
Spin up the `Uvicorn` server. This command will simultaneously launch both the FastAPI backend and serve the Vanilla JS Frontend application.
```bash
cd phase5_backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open a web browser and navigate to **[`http://localhost:8000`](http://localhost:8000)** to begin interacting with the MF Advisor bot!

---

## 🔄 Automated Updates
The application includes a self-updating CI/CD pipeline located in `.github/workflows/update_pipeline.yml`.

When deployed to GitHub, the workflow safely spins up an ephemeral runner every day at exactly `10:00 AM IST` (`04:30 UTC`). It executes `scheduler.py`, which:
1. Re-scrapes the indmoney site for the latest daily returns and NAVs.
2. Passes the updated CSV into FAISS to rebuild vector indexes.
3. Automatically Git Commits and Pushes the new index files straight back to your master branch. 

*Zero manual intervention required.*

---

## ☁️ Setting up Vercel Deployment
This repository is configured natively for serverless deployment on **Vercel** with a dedicated lightweight PyTorch environment overriding to prevent 250MB size failures.
1. Sign up for [Vercel](https://vercel.com/) and link your GitHub account.
2. Click **Add New Project** and import your `mutual-fund-rag` repository.
3. Open the **Environment Variables** tab and add your generated `GROQ_API_KEY`.
4. Leave the Framework Preset as `Other` and click **Deploy**. Vercel will automatically parse `vercel.json`, serve your vanilla frontend globally via Edge Network, and boot your Python FastAPI onto their Serverless instances!

---

## 📚 Source List
The application leverages the following data sources and technologies:
- **Financial Data Source:** Dynamically scraped from [Indmoney Mutual Funds](https://www.indmoney.com/mutual-funds)
- **Vector Embeddings Models:** Generated via `fastembed` using `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Database:** Local `FAISS` index (Facebook AI Similarity Search)
- **Large Language Model:** Powered via `Groq` using the `llama-3.1-8b-instant` model
- **Frameworks:** `FastAPI` (Backend), `Playwright` & `BeautifulSoup` (Scraping), Vanilla HTML/CSS/JS (Frontend)

---

## 💬 Sample Q&A

**User:** *What is the exit load of HDFC flexi cap fund?*
**MF Advisor:** The Exit load for HDFC Flexi Cap Fund Direct Plan Growth Option is 1.0%.
*Source URL: [https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184](https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184)*

**User:** *What is the phone number of the CEO?*
**MF Advisor:** I'm sorry, but as a mutual fund advisor, I cannot provide personal information. I can only assist with questions related to mutual funds.

**User:** *Which mutual fund has the lowest expense ratio?*
**MF Advisor:** Based on the context provided, the fund with the lowest expense ratio is the ICICI Prudential Liquid Fund Direct Plan Growth at 0.09%.
*Source URL: [https://www.indmoney.com/mutual-funds/icici-prudential-liquid-fund-direct-plan-growth](https://www.indmoney.com/mutual-funds/icici-prudential-liquid-fund-direct-plan-growth)*
