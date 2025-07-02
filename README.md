# 🏋️ UCSC Gym Occupancy Tracker & Predictor

## ❓ Problem

The UCSC gym is often overcrowded, and students rarely know the best times to work out. The current Campus Rec website shows real-time occupancy, but:

* There's no way to view historical trends
* There's no way to forecast future occupancy
* It requires checking manually every time

This project solves the problem by **automatically logging occupancy data**, analyzing patterns, and using a **custom-built machine learning model** to predict future gym traffic.

---

### 1. Web Scraper (Data Logger)

The scraper targets the UCSC Campus Rec website, which displays real-time gym occupancy. After inspecting the page with browser dev tools, I found the occupancy numbers are embedded directly in the HTML inside a specific `<div>`:

* **Facility ID used**: `facility-1799266f-57d9-4cb2-9f43-f5fd88b241db`

The scraper:
* Determines if the gym is currently open (based on predefined weekday/weekend hours)
* Every 15 minutes, if the gym is open:
  * Sends a GET request to the page
  * Extracts the occupancy count with BeautifulSoup
  * Appends a line to a `.txt` file for that date, e.g. `09:15, 74`

If the fetch fails or the gym is closed, an `ERROR` is logged or the script sleeps until reopening.

All logs are stored in the `occupancy_logs/` folder.

Example log:

```
09:15, 74
09:30, 88
09:45, 91
10:00, ERROR  ← means fetch failed or data was missing
```

All logs are saved to the `occupancy_logs/` directory.

---

### 2. Prediction Model

After collecting sufficient data, the log files are used to train a polynomial regression model that predicts gym occupancy based on time.

#### Feature Engineering

From each log entry, I extract:

* Day of week (1-7)
* Hour and minute
* Whether it’s a weekend
* Trigonometric encodings for periodic features (sin/cos of time)
* Polynomial combinations: squared/cubed terms, feature interactions

These are then standardized (`(x - mean) / std`) before feeding into the model.

#### Training

I use gradient descent to minimize **Mean Squared Error + L2 Regularization (Ridge penalty)**. The learning rate decays slowly over time to help convergence.

* **Initial learning rate**: 0.1
* **L2 penalty strength (λ)**: 0.05
* **Epochs**: 100,000

The model learns a weighted combination of polynomial features. After training, it can take user input (day, hour, minute) and return an estimated occupancy.

---

### 📊 Visualizations

The training script outputs:

![image](https://github.com/user-attachments/assets/0627ab75-8f1a-4230-b3d7-685d6d7dbd7c)
![image](https://github.com/user-attachments/assets/ead4d9ab-9157-4c46-9016-5d9f5eea7eda)

This helps validate how well the model captures trends and where it struggles.

#### 📉 Model Performance

The final regularized loss is **757.93**, which is relatively high. This could be due to:

* **Noise in data**: Some logs contain missing or inconsistent values (e.g. "ERROR" entries).
* **Rapid fluctuations**: Gym occupancy can change drastically within 15 minutes.
* **Lack of contextual features**: Events like holidays, finals week, or weather aren’t captured.
* **Model complexity**: Although polynomial features help, they may not fully capture underlying patterns.

Still, the model demonstrates useful trends and can provide helpful forecasts to reduce overcrowding.

---

### 3. Making Predictions

At the end of training, the user can input:

```
Day of the week (1=Mon, ..., 7=Sun)
Hour (0–23)
Minute (0, 15, 30, 45)
```

The script will apply the same feature transformations and output a prediction, for example:

```
Predicted gym occupancy at day 4, 17:30 → 63 people
```

This enables students to plan their workouts around low-traffic windows.

---

## ⚙️ Tech Stack

* **Python**: Core scripting
* **BeautifulSoup**: HTML parsing
* **Requests**: HTTP requests
* **Matplotlib**: Visualization
* **NumPy**: Model implementation, vector math
* **Standard file I/O**: To store logs and training data
