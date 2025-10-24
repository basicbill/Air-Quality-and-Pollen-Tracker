# Air Quality & Pollen Forecast Tracker

Automatically tracks air quality and pollen levels across 11 US locations, comparing forecasts to actual conditions to measure prediction accuracy over time.

## 🌟 What It Does

- **Daily Data Collection**: Automatically collects air quality (AQI, PM2.5, PM10, O3) and pollen levels (tree, grass, weed) every day at 9 AM UTC
- **Forecast Tracking**: Saves 1-5 day forecasts and later compares them to actual conditions
- **Accuracy Scoring**: Measures how accurate the forecasts were (AQI within ±20 points, pollen within ±1 level)
- **Web Dashboard**: Beautiful visualizations showing current conditions, historical trends, and forecast accuracy
- **11 Locations**: Tracks major US cities for comprehensive geographic coverage

## 📍 Tracked Locations

- KBIS - Bismarck, ND
- KBOS - Boston Logan, MA
- KDFW - Dallas/Fort Worth, TX
- KDEN - Denver, CO
- KLAX - Los Angeles, CA
- KMIA - Miami, FL
- KOMA - Omaha, NE
- KORD - Chicago O'Hare, IL
- KPDX - Portland, OR
- KPHX - Phoenix Sky Harbor, AZ
- KTUS - Tucson, AZ

## 🚀 Quick Setup

### 1. Get Your API Keys

**AirNow API (Air Quality Data)**
- Go to https://docs.airnowapi.org/account/request/
- Fill out the form (free for personal use)
- You'll receive your API key via email

**Tomorrow.io API (Pollen Data)**
- Go to https://app.tomorrow.io/signup
- Create free account
- Navigate to Development → API Keys
- Copy your API key

### 2. Create GitHub Repository

- Go to https://github.com/new
- Name it `air-quality-pollen-tracker`
- Make it **Public** (required for free GitHub Actions)
- Don't add README, .gitignore, or license (we'll add our files)
- Click "Create repository"

### 3. Add Your Files

**Option A: Using GitHub's Web Interface**
1. On your new repo page, click "uploading an existing file"
2. Drag these files:
   - `air_quality_pollen_tracker.py`
   - `index.html`
3. Commit the files
4. Create the workflow file:
   - Click "Add file" → "Create new file"
   - Type: `.github/workflows/daily-collection.yml`
   - Paste the workflow content
   - Commit

**Option B: Using Git Command Line**
```bash
# In your project folder
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR-USERNAME/air-quality-pollen-tracker.git
git push -u origin main
```

### 4. Create Data Folders

Create these empty folders in your repo (GitHub needs at least a placeholder file to track empty folders):

1. Click "Add file" → "Create new file"
2. Type: `data/air_quality/current/.gitkeep` and commit
3. Repeat for:
   - `data/air_quality/forecasts/.gitkeep`
   - `data/pollen/current/.gitkeep`
   - `data/pollen/forecasts/.gitkeep`

(The `.gitkeep` files are just placeholders so Git tracks the empty folders)

### 5. Add Your API Keys as Secrets

1. Go to your repo's **Settings** tab
2. Click **Secrets and variables** → **Actions** (left sidebar)
3. Click **New repository secret**
4. Add two secrets:
   - Name: `AIRNOW_API_KEY`, Value: [your AirNow key]
   - Name: `TOMORROW_API_KEY`, Value: [your Tomorrow.io key]

### 6. Enable GitHub Actions Permissions

1. Go to repo **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select **Read and write permissions**
3. Click **Save**

This lets GitHub Actions commit the collected data back to your repo.

### 7. Deploy to Netlify

1. Go to https://app.netlify.com
2. Click **Add new site** → **Import an existing project**
3. Choose **GitHub** and authorize Netlify
4. Select your `air-quality-pollen-tracker` repo
5. Build settings:
   - Build command: (leave blank)
   - Publish directory: `/` (the root)
6. Click **Deploy site**

Your dashboard will be live at something like `https://your-site-name.netlify.app`

### 8. Test It!

Don't wait for the scheduled run - test immediately:

1. Go to your repo's **Actions** tab
2. Click **Daily Air Quality & Pollen Collection** (left sidebar)
3. Click **Run workflow** → **Run workflow**
4. Wait ~60 seconds for it to complete
5. Check your repo - you should see new files in the `data/` folders
6. Check your Netlify site - it will show "Loading data..." (correct, since you need 2 days for the first forecast score)

## 📊 Understanding the Data

### When You'll See Results

- **Day 1**: First data collection (current conditions + forecasts saved)
- **Day 2**: First 1-day forecast gets scored! 🎉
- **Day 3**: First 2-day forecast scored
- **Day 6**: First 5-day forecast scored
- **After 30 days**: Meaningful patterns start emerging
- **After 90 days**: Seasonal trends become clear

### Accuracy Metrics

**Air Quality Forecasts**
- "Accurate" = within ±20 AQI points
- Example: Forecast of 80, actual 95 = accurate (diff of 15)
- Example: Forecast of 50, actual 120 = not accurate (diff of 70)

**Pollen Forecasts**
- "Accurate" = within ±1 level on the 0-5 scale
- Example: Forecast level 2, actual level 3 = accurate (diff of 1)
- Example: Forecast level 1, actual level 4 = not accurate (diff of 3)

## 🎨 Dashboard Features

Your live dashboard shows:

- **Current Conditions**: Latest AQI and pollen levels for all 11 locations
- **Accuracy Statistics**: How accurate forecasts have been by lead time
- **Best/Worst Locations**: Which cities have the cleanest/worst air
- **Forecast Accuracy Chart**: See how accuracy degrades over 1-5 days
- **Location Comparison**: Side-by-side current conditions

## 🔧 Customization

### Change Collection Time

Edit `.github/workflows/daily-collection.yml`:

```yaml
- cron: '0 9 * * *'  # 9 AM UTC (4 AM Central)
```

Use https://crontab.guru/ to help with cron format.

### Modify Accuracy Tolerances

Edit `air_quality_pollen_tracker.py` (around line 30):

```python
TOLERANCES = {
    "aqi": 20,      # Change to 15 for stricter scoring
    "pollen": 1     # 0-5 scale, within ±1 level
}
```

### Add/Remove Locations

Edit `air_quality_pollen_tracker.py` (around line 12):

```python
LOCATIONS = {
    "KORD": {"lat": 41.9742, "lon": -87.9073, "name": "Chicago O'Hare, IL"},
    # Add more locations...
}
```

Use airport codes for consistency. Find coordinates at https://www.latlong.net/

## 📁 Project Structure

```
air-quality-pollen-tracker/
├── .github/
│   └── workflows/
│       └── daily-collection.yml    # GitHub Actions automation
├── data/
│   ├── air_quality/
│   │   ├── current/                # Daily AQI snapshots (auto-created)
│   │   └── forecasts/              # AQI forecasts for scoring (auto-created)
│   ├── pollen/
│   │   ├── current/                # Daily pollen snapshots (auto-created)
│   │   └── forecasts/              # Pollen forecasts for scoring (auto-created)
│   └── results.json                # Accuracy scores (auto-created)
├── air_quality_pollen_tracker.py   # Main Python collection script
├── index.html                      # Web dashboard
└── README.md                       # This file
```

## 🔍 Troubleshooting

**Actions tab shows "no workflows"**
- Verify `.github/workflows/daily-collection.yml` is in the correct folder
- Make sure repo is public

**Workflow fails with permission error**
- Go to Settings → Actions → General
- Enable "Read and write permissions"

**Dashboard shows "Loading data..."**
- Normal for first day - wait until Day 2 for first results
- Check that `data/results.json` exists after second run

**Missing data for some locations**
- Some locations may have API data gaps (normal)
- Script continues collecting for other locations
- Check Actions logs for details

**API rate limits**
- AirNow: Very generous, should never hit limits
- Tomorrow.io: 500 calls/day, 25/hour (plenty for 11 locations)
- Script adds delays between calls to be respectful

## 📈 What You'll Learn

After collecting data for a while:

1. **Best Location for Your Health**: Which city has consistently better air quality and lower pollen?
2. **Seasonal Patterns**: When is pollen season in each location? When is air quality worst?
3. **Forecast Reliability**: Are 1-day forecasts accurate? What about 5-day?
4. **Location Comparisons**: How does Phoenix air quality compare to Chicago?
5. **Planning Insights**: When should you plan outdoor activities? When to stay inside?

## 🎯 Why This Matters

- **Health Planning**: Know when air quality will be poor before it happens
- **Respiratory Health**: Track pollen to manage allergies proactively
- **Location Decisions**: Use real data if considering moving cities
- **Forecast Trust**: Understand if you can rely on air quality and pollen forecasts

## 📝 API Documentation

- **AirNow API**: https://docs.airnowapi.org/
- **Tomorrow.io API**: https://docs.tomorrow.io/

## 💡 Tips

- Let it run for at least 30 days before drawing conclusions
- Check the dashboard weekly to see trends emerging
- Compare forecast accuracy between locations - some may be more predictable
- Use the data to plan outdoor activities and travel timing

## 🐛 View Detailed Logs

Want to see what's happening?
1. Go to **Actions** tab in your repo
2. Click on any workflow run
3. View detailed logs of what was collected

The script logs everything it does, including any errors or missing data.

---

**Similar Project**: Check out the Weather Forecast Tracker that inspired this project: https://github.com/basicbill/Weather-forecast-tracker
