# DataDoc AI Deployment Guide

## Overview
Deploy DataDoc AI on Render with:
- **Backend**: FastAPI server
- **Frontend**: Streamlit web app  
- **Database**: PostgreSQL

## Prerequisites
1. Render account (https://render.com)
2. GitHub repository with your code
3. Groq API key

## Step 1: Prepare Your Code

### 1.1 Update .env file
```bash
# Set your Groq API key
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 1.2 Test locally (optional)
```bash
# Install dependencies
pip install -r requirements.txt

# Test backend
python backend_server.py

# Test frontend (in separate terminal)
streamlit run streamlit_app.py
```

## Step 2: Deploy to Render

### 2.1 Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2.2 Create Render Services
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the repository
5. **Deploy Backend First**:
   - Name: `datadoc-backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend_server:app --host 0.0.0.0 --port $PORT`
   - Add Environment Variables:
     - `GROQ_API_KEY`: Your Groq API key
6. **Deploy Database**:
   - Click "New +" → "PostgreSQL"
   - Name: `datadoc-db`
   - Plan: Free
7. **Deploy Frontend**:
   - Click "New +" → "Web Service"
   - Name: `datadoc-frontend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
   - Add Environment Variable:
     - `BACKEND_URL`: Your backend URL (e.g., `https://datadoc-backend.onrender.com`)

### 2.3 Configure Database Connection
1. Go to your PostgreSQL service on Render
2. Copy the "External Database URL"
3. Go to your backend service
4. Add these environment variables:
   - `DB_HOST`: Extract from URL
   - `DB_NAME`: Database name from URL
   - `DB_USER`: Username from URL
   - `DB_PASSWORD`: Password from URL
   - `DB_PORT`: Port from URL (usually 5432)

### 2.4 Migrate Data (Optional)
If you want to migrate your existing SQLite data:
1. Set up local PostgreSQL connection in `.env`
2. Run: `python migrate_to_postgresql.py`

## Step 3: Verify Deployment

### 3.1 Check Backend
- Visit: `https://datadoc-backend.onrender.com/health`
- Should return: `{"status": "healthy", "database": "connected"}`

### 3.2 Check Frontend  
- Visit: `https://datadoc-frontend.onrender.com`
- Should show DataDoc AI interface

### 3.3 Test Functionality
1. Check backend connection in sidebar
2. Select a table and explore
3. Test AI summary generation

## Environment Variables Reference

### Backend (datadoc-backend)
```
GROQ_API_KEY=your_groq_api_key
DB_HOST=your_db_host
DB_NAME=datadoc_ai
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=5432
```

### Frontend (datadoc-frontend)
```
BACKEND_URL=https://datadoc-backend.onrender.com
```

## Troubleshooting

### Common Issues

**Backend not connecting to database**
- Verify database credentials in environment variables
- Check database logs on Render
- Ensure database is in same region as backend

**Frontend not connecting to backend**
- Verify `BACKEND_URL` is correct
- Check backend is running and healthy
- Ensure CORS is properly configured

**AI summaries not working**
- Verify `GROQ_API_KEY` is set and valid
- Check backend logs for API errors
- Ensure Groq API quota is not exceeded

**Build failures**
- Check `requirements.txt` has correct versions
- Verify Python version compatibility
- Check build logs on Render

### Debug Commands
```bash
# Check backend health
curl https://datadoc-backend.onrender.com/health

# Check tables
curl https://datadoc-backend.onrender.com/tables

# Check frontend logs
# Go to Render dashboard → Services → datadoc-frontend → Logs
```

## Cost Optimization
- Use free tier for testing (limited resources)
- Upgrade to paid plans for production:
  - PostgreSQL: $7/month for basic
  - Web Services: $7/month each
- Monitor usage in Render dashboard

## Security Notes
- Never commit API keys to Git
- Use Render's environment variables for secrets
- Consider adding authentication for production
- Enable database IP restrictions if needed

## Next Steps
1. Set up custom domain
2. Add user authentication
3. Implement caching for better performance
4. Set up monitoring and alerts
5. Add automated backups
