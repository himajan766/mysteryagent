# 🚀 Deployment Guide

This guide will help you deploy your Murder Mystery Agent to **Streamlit Community Cloud** (free hosting) so anyone can play it online!

## Prerequisites

1. ✅ Your code is pushed to a **public GitHub repository**
2. ✅ You have a **GitHub account**
3. ✅ You have an **OpenAI API key** (for the LLM)

---

## Step 1: Push Your Code to GitHub

If you haven't already:

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Murder Mystery Agent v2.0"

# Create a new repository on GitHub (via web interface)
# Then connect it:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Streamlit Community Cloud

### 2.1 Sign Up / Sign In

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your **GitHub account**
3. Click **"New app"**

### 2.2 Configure Your App

Fill in the deployment form:

- **Repository**: Select your GitHub repository
- **Branch**: `main` (or your default branch)
- **Main file path**: `web_app.py`
- **App URL**: Choose a custom subdomain (e.g., `murder-mystery-agent`)

### 2.3 Set Environment Variables

**Important**: You need to add your OpenAI API key as a secret!

1. In the Streamlit dashboard, go to **"Settings"** → **"Secrets"**
2. Add this configuration:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```

**⚠️ Security Note**: Never commit your API key to GitHub! Always use Streamlit's secrets feature.

### 2.4 Deploy!

Click **"Deploy"** and wait 1-2 minutes. Your app will be live at:
```
https://YOUR-APP-NAME.streamlit.app
```

---

## Step 3: Share Your App! 🎉

Once deployed, you can:
- Share the URL with anyone
- Embed it in websites
- Add it to your portfolio
- Post it on social media

---

## Alternative: Other Hosting Options

### Railway
- Go to [railway.app](https://railway.app)
- Connect your GitHub repo
- Set `OPENAI_API_KEY` as an environment variable
- Deploy!

### Render
- Go to [render.com](https://render.com)
- Create a new "Web Service"
- Connect your GitHub repo
- Set build command: `pip install -r requirements.txt`
- Set start command: `streamlit run web_app.py --server.port=$PORT`
- Add `OPENAI_API_KEY` environment variable

### Heroku
- Install Heroku CLI
- Create `Procfile` with: `web: streamlit run web_app.py --server.port=$PORT --server.address=0.0.0.0`
- Deploy: `git push heroku main`

---

## Troubleshooting

### App Won't Start
- ✅ Check that `web_app.py` is in the root directory
- ✅ Verify `requirements.txt` includes all dependencies
- ✅ Check Streamlit logs for error messages

### API Key Issues
- ✅ Ensure `OPENAI_API_KEY` is set in Streamlit secrets
- ✅ Verify the key is valid and has credits
- ✅ Check the key doesn't have extra spaces

### Import Errors
- ✅ Make sure all files in `agent/` directory are committed
- ✅ Verify `agent/__init__.py` exists
- ✅ Check that all dependencies in `requirements.txt` are correct

### Performance Issues
- ✅ Consider upgrading to a paid OpenAI plan for higher rate limits
- ✅ Monitor API usage in OpenAI dashboard
- ✅ Enable caching (already implemented in the code)

---

## Cost Considerations

**Streamlit Community Cloud**: **FREE** ✅
- Unlimited apps
- Free hosting
- Public repos only

**OpenAI API Costs**:
- GPT-4o: ~$0.01-0.05 per game session
- GPT-3.5-turbo: ~$0.001-0.005 per game session (cheaper option)
- Monitor usage at [platform.openai.com/usage](https://platform.openai.com/usage)

**Tip**: You can set usage limits in your OpenAI account to prevent unexpected charges.

---

## Need Help?

- 📖 [Streamlit Community Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- 💬 [Streamlit Community Forum](https://discuss.streamlit.io)
- 🐛 [Report Issues](https://github.com/YOUR_USERNAME/YOUR_REPO/issues)

---

**Happy Deploying! 🎩🔍**

