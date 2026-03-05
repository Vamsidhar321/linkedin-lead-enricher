# 🔗 LinkedIn Lead Enricher

A powerful web application for discovering and enriching LinkedIn leads from companies and keywords. Extract leads, enrich profiles with job titles, companies, and industry data, and export comprehensive datasets.

## ✨ Features

- **Dual Input Processing**
  - 📊 Company-based scraping: Extract posts from company pages and employees
  - 🔍 Keyword-based search: Find posts matching specific topics
  - ✅ Process one or both simultaneously

- **Lead Enrichment**
  - Extract engagement data (likes, comments, shares)
  - Enrich profiles with: job title, company, seniority level, industry
  - Automatic deduplication of leads across search paths
  - Profile completion from LinkedIn data

- **Real-time Tracking**
  - Live progress updates during processing
  - Processing stage indicators
  - Stats display: posts found, engagements, unique people

- **Multiple Export Formats**
  - CSV export for spreadsheet analysis
  - Excel export with formatting
  - JSON export for data pipelines
  - Customizable filtering before export

- **Optional Slack Integration**
  - Notifications when processing starts
  - Completion alerts with results summary
  - Error notifications for troubleshooting

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/linkedin-lead-enricher.git
   cd linkedin-lead-enricher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**
   ```bash
   cp .env.template .env
   ```

   Edit `.env` and add your RapidAPI key:
   ```
   RAPIDAPI_KEY=your_api_key_here
   RAPIDAPI_HOST=realtime-linkedin-bulk-data.p.rapidapi.com
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## 📋 API Configuration

### Getting Your RapidAPI Key

1. Go to: https://rapidapi.com/apibuilderz/api/realtime-linkedin-bulk-data
2. Click "Subscribe to Test" (free tier available)
3. Copy your "X-RapidAPI-Key" from the dashboard
4. Paste into your `.env` file as `RAPIDAPI_KEY`

### Optional: Slack Notifications

1. Go to: https://api.slack.com/messaging/webhooks
2. Create an Incoming Webhook for your Slack workspace
3. Copy the webhook URL
4. Paste into `.env` as `SLACK_WEBHOOK_URL`

## 🌐 Deployment Options

### Option 1: GitHub Actions + Render.com (Recommended for Automated Deployment)
Deploy automatically to Render.com when you push code to GitHub.

1. **Set up Render.com**
   - Go to https://render.com and sign up with GitHub
   - Create a new Web Service from your GitHub repository
   - Use the `render.yaml` configuration file (already included)

2. **Configure GitHub Secrets**
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `RENDER_API_KEY`: Your Render API key (from Render dashboard → Account → API)
     - `RENDER_SERVICE_ID`: Your service ID (from Render service URL)

3. **Add Environment Variables in Render**
   - In Render dashboard, add your environment variables:
     - `RAPIDAPI_KEY`
     - `RAPIDAPI_HOST`
     - `SLACK_WEBHOOK_URL` (optional)

4. **Deploy**
   - Push code to GitHub main branch
   - GitHub Actions will automatically deploy to Render
   - Your app will be available at `https://your-app.onrender.com`

### Option 2: Manual Render.com Deployment
Free tier available. Flask-compatible cloud platform.

1. **Create Render account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create new Web Service**
   - Connect your GitHub repository
   - Environment: Python 3.11
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`

3. **Add environment variables**
   - In Render dashboard, add your environment variables:
     - `RAPIDAPI_KEY`
     - `RAPIDAPI_HOST`
     - `FLASK_ENV=production`

4. **Deploy**
   - Render automatically deploys when you push to GitHub
   - Your app will be available at `https://your-app.onrender.com`

### Option 3: Railway.app (Alternative)
Another free-tier option with good Flask support.

1. **Create Railway account**
   - Go to https://railway.app
   - Connect GitHub

2. **Deploy from GitHub**
   - Select your repository
   - Railway auto-detects Flask
   - Add environment variables in dashboard
   - Deploy with one click

3. **Get your URL**
   - Railway provides your live URL automatically

### Option 4: GitHub (For Code Sharing Only)
Perfect for sharing code with your manager and team.

1. **Your repository is already on GitHub**
   - Repository: https://github.com/Vamsidhar321/linkedin-lead-enricher
   - Share this link with your manager
   - They can view the code and follow "Quick Start" to run locally

### Option 5: Heroku (Legacy - Requires Credit Card)
⚠️ Note: Heroku free tier ended November 2022. Paid dynos required.

## 📁 Project Structure

```
linkedin-lead-enricher/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── .env.template         # Environment configuration template
├── .env                  # Your local environment (git ignored)
├── .gitignore           # Git ignore patterns
│
├── backend/             # Backend modules
│   ├── config.py        # Configuration loader
│   ├── linkedin_api.py  # RapidAPI wrapper
│   ├── data_models.py   # Pydantic data models
│   ├── workflow_orchestrator.py  # Main enrichment logic
│   ├── deduplication.py # Lead deduplication
│   ├── data_exporter.py # CSV/Excel/JSON export
│   └── slack_notifier.py # Slack integration
│
├── templates/           # HTML templates
│   └── index.html       # Main web interface
│
└── static/              # Static assets
    ├── style.css        # Styling
    └── app.js           # Frontend logic
```

## 💻 Usage

### 1. Enter Input Data
- **Company URLs**: LinkedIn company profile URLs (optional)
- **Keywords**: Topics to search for (optional)
- **Time Window**: Select date range or use presets (Last 7/14/30 days)
- **Slack Notifications**: Optional webhook URL

### 2. Monitor Progress
- Real-time progress updates
- Processing stage indicators
- Live stats: posts found, engagements, unique people

### 3. Export Results
- Download as CSV, Excel, or JSON
- Optional filtering by job title, seniority, company size
- All enriched profile data included

## 📊 Output Data Structure

Each exported lead includes:
- Full Name
- Job Title & Seniority Level
- Current Company & Industry
- Company Domain
- LinkedIn Profile URL
- Engagement Type (like, comment, share)
- Post Information
- Source Details (company/keyword that found them)

## 🔧 Troubleshooting

### "API not configured" error
- Ensure your `.env` file has `RAPIDAPI_KEY` set
- Verify you've subscribed to the RapidAPI endpoint
- Restart the application after updating `.env`

### No results found
- Verify the company URLs are correct LinkedIn URLs
- Check keywords are specific enough
- Ensure date range is appropriate
- Some companies/keywords may have limited public data

### Export fails
- Ensure at least one enrichment has completed
- Check browser console for JavaScript errors
- Verify output folder exists and is writable

## 🤝 Support

- Check the [Issues](https://github.com/yourusername/linkedin-lead-enricher/issues) page
- Review `.env.template` for configuration options
- Ensure all dependencies in `requirements.txt` are installed

## 📝 License

MIT License - Feel free to use and modify for your needs.

## 🎯 Next Steps

1. **Get your RapidAPI key** (5 minutes)
2. **Run locally** to test (Quick Start section)
3. **Deploy to Render** or share GitHub link with your manager
4. **Start enriching leads!** 🚀

---

Built with ❤️ using Flask, Python, and LinkedIn API
