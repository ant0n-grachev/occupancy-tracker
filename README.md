# 🏋️ UCSC Gym Occupancy Tracker & Predictor

## ❓ Problem

The UCSC gym is often overcrowded, and students never really know when is the best time to go. The official website shows current occupancy, but:

- There's no way to view historical trends.
- There's no forecasting feature to plan future visits.
- You have to check the website manually every time.

This project solves that by **automatically logging occupancy data**, with the goal of **training a prediction model** and **notifying users via a Telegram bot** when the gym is likely to be least busy.

---

## 🔍 How It Works

### 1. Reverse-Engineering the Website

The UCSC Campus Rec [website](https://campusrec.ucsc.edu/FacilityOccupancy) displays real-time gym occupancy data via a dynamic frontend.

- Using Chrome DevTools, I inspected network requests made by the page.
- I found that the relevant data is embedded directly in the HTML.
- Each gym facility has a unique ID. For the UCSC main gym, it's:
```facility-1799266f-57d9-4cb2-9f43-f5fd88b241db```

### 2. Data Collection

The Python script does the following:

- Checks if the gym is open based on weekday/weekend hours.
- Every 15 minutes (during open hours), it:
  - Requests the page.
  - Parses the current occupancy using `BeautifulSoup`.
  - Logs the time and value into a daily `.txt` file.

Example log output:
```
09:15, 74
09:30, 88
09:45, 91
10:00, ERROR <- indicates fetch failure
```

All data is stored in the `occupancy_logs/` directory.

---

## 🚀 Next Steps (Roadmap)

### ✅ Phase 1: Web Parser (Completed)

- [x] Reverse engineer gym occupancy website
- [x] Automatically fetch & log data every 15 minutes
- [x] Organize data per day in text files
- [x] Handle website errors gracefully

### 🔜 Phase 2: Data Analysis & Prediction

- [ ] Convert raw logs into a structured dataset (CSV or Pandas DataFrame)
- [ ] Train a machine learning model to predict occupancy (e.g. XGBoost, LSTM)
- [ ] Visualize data trends (by time, day of week, etc.)
- [ ] Evaluate best low-traffic time windows

### 🔜 Phase 3: Telegram Bot Integration

- [ ] Create Telegram bot to notify users when the gym is likely to be empty
- [ ] Support user queries like “When should I go today?”
- [ ] Daily/weekly push notifications with “best time to go”

---

## ⚙️ Tech Stack

- **Python**: Core scripting
- **BeautifulSoup**: HTML parsing
- **Requests**: Web requests
- **Logging**: For runtime visibility
- **Telegram Bot API (planned)**: For user notifications
- **Pandas/NumPy (planned)**: For data analysis
- **ML models (planned)**: For time series forecasting

---

## 📈 Example Use Case

> You’re planning to work out after class, but you don’t want to wait 20 minutes for a squat rack.  
> Use this tool to check when it’s historically least crowded on Thursdays at 5 PM.  
> Get a Telegram message:  
> “Best window: 6:45-8:00 PM — avg. occupancy: 40.”
