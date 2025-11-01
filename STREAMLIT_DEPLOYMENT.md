# 🚀 Streamlit Cloud Deployment Guide

## Quick Deploy Steps

### 1. Prerequisites
- ✅ Code pushed to GitHub: `vaibhav-dev-arch/rag-agent-platform`
- ✅ `app.py` in root directory ✅
- ✅ `requirements.txt` includes `streamlit>=1.28.0` ✅
- ✅ `.streamlit/config.toml` configured ✅

### 2. Deploy to Streamlit Cloud

1. **Visit Streamlit Cloud:**
   - Go to: https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App:**
   - Click "New app" button
   - Select "From existing repo"

3. **Configure Deployment:**
   - **Repository**: `vaibhav-dev-arch/rag-agent-platform`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Python version**: `3.11`

4. **Optional: Add Secrets**
   - Go to "Settings" → "Secrets"
   - Add secrets if using external API:
     ```toml
     API_URL = "https://your-api-server.com"
     OPENAI_MODEL = "gpt-3.5-turbo"
     ```

5. **Deploy:**
   - Click "Deploy!"
   - Wait for deployment (usually 1-2 minutes)
   - Your app will be live at: `https://your-app-name.streamlit.app`

## 📋 Configuration Files

### `.streamlit/config.toml`
Streamlit configuration with:
- Headless mode
- CORS settings
- Theme configuration
- Usage stats disabled

### `.streamlit/secrets.toml` (Optional)
Add in Streamlit Cloud settings:
```toml
API_URL = "https://your-api-server.com"
OPENAI_MODEL = "gpt-3.5-turbo"
```

### `packages.txt` (Optional)
System packages if needed (usually not required)

## 🔧 App Configuration

The dashboard reads configuration from:
1. **Streamlit Secrets** (in cloud) - `st.secrets.get("API_URL")`
2. **Environment Variables** - `os.getenv("API_URL")`
3. **Defaults** - `"http://localhost:8000"`

## 🎯 Dashboard Features

Once deployed, you'll have:
- ✅ Real-time cost tracking (24h, hourly, all-time)
- ✅ Latency monitoring (p95, average, min/max)
- ✅ Interactive charts (Cost over time, Query volume)
- ✅ Query testing interface
- ✅ Auto-refresh every 30 seconds

## 🔗 URLs

- **Streamlit Cloud**: https://share.streamlit.io/
- **Dashboard**: `https://your-app-name.streamlit.app`
- **Repository**: https://github.com/vaibhav-dev-arch/rag-agent-platform

## 📝 Notes

- **API Server**: If your API server is deployed separately, add its URL in secrets
- **Local Development**: Use `streamlit run app.py` for local testing
- **Environment Variables**: For local dev, use `.env` file or environment variables

## 🆘 Troubleshooting

### Deployment Fails
- Check that `requirements.txt` is correct
- Verify Python version is 3.11+
- Check Streamlit Cloud logs for errors

### API Connection Issues
- Ensure API_URL is set correctly in secrets
- Verify API server is accessible from Streamlit Cloud
- Check CORS settings if API is on different domain

### Missing Dependencies
- Verify all packages in `requirements.txt`
- Check Streamlit Cloud build logs

---

**Ready to deploy!** 🚀

