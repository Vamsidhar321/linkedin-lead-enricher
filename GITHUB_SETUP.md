# GitHub Setup & Deployment Guide

This guide will help you push your LinkedIn Lead Enricher to GitHub and deploy it online.

## Step 1: Create a GitHub Repository

### Option A: Create on GitHub Website (Recommended)
1. Go to https://github.com/new
2. Enter repository name: `linkedin-lead-enricher`
3. Add description: "Web app for discovering and enriching LinkedIn leads from companies and keywords"
4. Make it **Public** (so your manager can view it)
5. Skip "Add .gitignore" (we already have one)
6. Skip "Add license" (or choose MIT)
7. Click **Create repository**

### Option B: Create Using GitHub CLI
```bash
gh repo create linkedin-lead-enricher \
  --public \
  --source=. \
  --remote=origin \
  --push
```

---

## Step 2: Push Code to GitHub

After creating the repository, copy the HTTPS URL from GitHub, then run:

```bash
cd "/Users/apple/Desktop/Claude Code /Test 1/linkedin_enricher"

# Add your GitHub repository URL (replace with your actual URL)
git remote add origin https://github.com/YOUR_USERNAME/linkedin-lead-enricher.git

# Rename branch to main (if not already)
git branch -M main

# Push code to GitHub
git push -u origin main
```

**That's it!** Your code is now on GitHub.

---

## Step 3: Share with Your Manager

Send them the GitHub link:
```
https://github.com/YOUR_USERNAME/linkedin-lead-enricher
```

They can view:
- All source code
- Project structure
- Documentation (README.md)
- Setup instructions

---

## Step 4: Deploy Publicly (Optional but Recommended)

### Option A: Deploy to Render.com (FREE)

**Benefits:**
- ✅ Free tier available
- ✅ Automatic deploys when you push to GitHub
- ✅ Your manager can access the live app
- ✅ Easy to use dashboard

**Steps:**

1. **Go to Render.com**
   - https://render.com
   - Click "Get Started"
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Click "Connect" next to your `linkedin-lead-enricher` repository
   - Authorize Render to access your GitHub account

3. **Configure Service**
   - **Name:** `linkedin-lead-enricher`
   - **Environment:** Python 3.11
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

4. **Add Environment Variables**
   - Click "Advanced" at the bottom
   - Click "Add Environment Variable" for each:
     - **RAPIDAPI_KEY:** (your API key)
     - **RAPIDAPI_HOST:** `realtime-linkedin-bulk-data.p.rapidapi.com`
     - **FLASK_ENV:** `production`

5. **Deploy**
   - Click "Create Web Service"
   - Render starts deploying (takes 2-3 minutes)
   - Your app is live at: `https://linkedin-lead-enricher.onrender.com`
   - (Your actual URL will be different)

**Share with Manager:**
- Send them the live URL
- They can use the app without installing anything!

---

### Option B: Deploy to Railway.app (FREE)

**Benefits:**
- ✅ Very simple setup
- ✅ Good Flask support
- ✅ Auto-deploys from GitHub

**Steps:**

1. **Go to Railway.app**
   - https://railway.app
   - Sign up with GitHub

2. **Deploy**
   - Click "Create Project"
   - Select "Deploy from GitHub"
   - Choose your repository
   - Railway auto-detects Flask

3. **Add Environment Variables**
   - Click "Variables" tab
   - Add: `RAPIDAPI_KEY`, `RAPIDAPI_HOST`, `FLASK_ENV=production`

4. **Deploy**
   - Railway automatically deploys
   - Your URL: Copy from Railway dashboard

---

### Option C: Deploy to Heroku (PAID)

⚠️ **Note:** Heroku free tier ended in November 2022.
- Paid dynos start at $7/month
- Uses the provided `Procfile` automatically

**Not recommended unless you want a professional production setup.**

---

## Step 5: Update README with Live Link (Optional)

After deployment, edit your README to include the live link:

```markdown
## 🚀 Try it Live

Visit the live demo: https://your-live-url.onrender.com

(Or share your GitHub link for manager review)
```

---

## Sharing with Your Manager

You have two options:

### Option 1: GitHub Link (Code Review)
- Share GitHub URL
- Manager can view source code
- Manager runs it locally following README
- Best for code review and understanding

### Option 2: Live URL (Live Demo)
- Share Render/Railway live URL
- Manager can test the app immediately
- No setup required on their end
- Best for quick demo and feedback

### Option 3: Both (Recommended)
- Share GitHub link for code review
- Share live URL for testing
- Manager can choose their preference

---

## Troubleshooting

### "Repository not found" error
- Make sure the GitHub URL is correct
- Verify you created the repo on GitHub
- Check you're in the correct project directory

### Deployment fails on Render/Railway
- Verify environment variables are set correctly
- Check the logs in the dashboard
- Ensure `RAPIDAPI_KEY` is valid
- Make sure `requirements.txt` includes all dependencies

### Live app shows error
- Check the deployment logs
- Verify environment variables are set
- Ensure your API key is active
- Try restarting the service from dashboard

---

## Quick Reference Commands

```bash
# View git status
git status

# View commit history
git log --oneline

# Make changes and push
git add .
git commit -m "Your message here"
git push

# View remote URL
git remote -v
```

---

## Next Steps

1. ✅ Create GitHub repository (Step 1-2)
2. ✅ Push your code (Step 2)
3. ✅ Deploy to Render (Step 4) - **RECOMMENDED**
4. ✅ Share links with your manager (Step 5)
5. ✅ Start gathering leads! 🚀

---

## Need Help?

- **GitHub Issues:** Add an issue on your GitHub repo
- **Render Support:** https://render.com/support
- **Railway Support:** https://railway.app/support
- **Check logs:** Look at deployment logs in the dashboard

---

**You're all set!** Your LinkedIn Lead Enricher is ready to share with your manager. 🎉
