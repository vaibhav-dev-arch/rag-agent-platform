# RAG Agent Platform

A comprehensive, production-ready RAG (Retrieval-Augmented Generation) platform with agent architecture, security hardening, and database persistence.

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start API server:**
   ```bash
   python -m src.rag_agent.api_server
   ```

3. **Start Streamlit Dashboard:**
   ```bash
   streamlit run app.py
   ```

## 📊 Streamlit Dashboard

The platform includes a **1-Click Cost & Latency Dashboard** built with Streamlit.

### Features:
- Real-time cost tracking (24h, hourly, all-time)
- Latency monitoring (p95, average, min/max)
- Interactive charts (Cost over time, Query volume)
- Query testing interface
- Auto-refresh every 30 seconds

### Local Access:
```bash
streamlit run app.py
```
Open: http://localhost:8501

## ☁️ Deploy to Streamlit Cloud

### Prerequisites:
1. Push your code to GitHub
2. Have a Streamlit Cloud account (free): https://streamlit.io/cloud

### Deployment Steps:

1. **Fork or use your repository:**
   - Ensure `app.py` is in the root directory ✅
   - Ensure `requirements.txt` includes `streamlit` ✅

2. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"

3. **Configure Deployment:**
   - **Repository**: Select `vaibhav-dev-arch/rag-agent-platform`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Python version**: `3.11`

4. **Set Secrets (Optional):**
   - If your API server is external, add secrets:
     - `API_URL`: Your API server URL
     - `OPENAI_MODEL`: Model name (optional)

5. **Deploy:**
   - Click "Deploy!"
   - Your dashboard will be live at: `https://your-app.streamlit.app`

### Configuration:

The dashboard can be configured via environment variables or Streamlit secrets:

- `API_URL`: API server URL (default: `http://localhost:8000`)
- `OPENAI_MODEL`: Model to track (default: `gpt-3.5-turbo`)

### For External API:

If your API server is deployed separately:

1. Add to Streamlit Secrets:
   ```
   API_URL = "https://your-api-server.com"
   ```

2. Update `app.py` to read from secrets:
   ```python
   API_URL = st.secrets.get("API_URL", "http://localhost:8000")
   ```

## 📁 Project Structure

```
rag-agent-platform/
├── app.py                 # Streamlit Dashboard (main file)
├── agent.py              # LangGraph Anomaly Detection Agent
├── requirements.txt      # Dependencies
├── src/
│   └── rag_agent/        # RAG platform core
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md
```

## 🔧 Requirements

See `requirements.txt` for full dependencies. Key requirements:
- Python 3.11+
- streamlit>=1.28.0
- pandas>=2.0.0
- langgraph>=0.0.20

## 📖 Documentation

- [API Documentation](docs/API_DOCUMENTATION.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Production Readiness](docs/PRODUCTION_READINESS_ASSESSMENT.md)

## 📄 License

MIT License

