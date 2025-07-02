import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

# 1) Load data from log files
folder_path = "occupancy_logs"
X = []
y = []

for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(folder_path, filename)
        try:
            date = datetime.strptime(filename[:-4], "%Y-%m-%d")
            dow = date.isoweekday()  # 1 (Mon) to 7 (Sun)
            is_weekend = float(dow >= 6)
        except Exception as e:
            print(f"Skipping {filename}: invalid date format")
            continue

        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    time_str, count_str = line.split(",")
                    time_obj = datetime.strptime(time_str.strip(), "%H:%M")
                    hour = time_obj.hour
                    minute = time_obj.minute
                    if "ERROR" in count_str: continue
                    count = int(count_str.strip())
                    X.append([dow, hour, minute, is_weekend])
                    y.append(count)
                except Exception as e:
                    print(f"Skipping line in {filename}: {line} -> {e}")
                    continue
print("X:", X)
print("y:", y)
X = np.array(X, dtype=np.float64)
y = np.array(y, dtype=np.float64)

# 2) Determine polynomial features
dow = X[:, 0]
hour = X[:, 1]
minute = X[:, 2]
is_weekend = X[:, 3]

minute_of_day = hour * 60 + minute
minute_norm = (minute_of_day / (24 * 60)) * 2 * np.pi
dow_norm = (dow / 7) * 2 * np.pi
hour_cubed = hour ** 3
minute_cubed = minute ** 3
dow_hour_squared = dow * (hour ** 2)

X_poly = np.column_stack([
    dow, hour, minute,
    np.sin(dow_norm), np.cos(dow_norm),
    np.sin(minute_norm), np.cos(minute_norm),
    dow ** 2, hour ** 2, minute ** 2,
    hour_cubed, minute_cubed, dow_hour_squared,
    dow * hour, dow * minute, hour * minute, is_weekend
])

# 3) Feature scaling
X_mean = X_poly.mean(axis=0)
X_std = X_poly.std(axis=0)
X_scaled = (X_poly - X_mean) / X_std

# 4) Initialize weights & hyperparameters
w = np.zeros(X_scaled.shape[1])
b = 0.0
m = len(y)

initial_lr = 0.1
decay_rate = 1e-10

epochs = 100000
lmbda = 0.05  # regularization strength

# 5) Gradient descent
for epoch in range(epochs):
    learning_rate = initial_lr / (1 + decay_rate * epoch)
    y_pred = X_scaled @ w + b
    error = y - y_pred

    dw = (-2 / m) * (X_scaled.T @ error) + (lmbda / m) * w
    db = (-2 / m) * np.sum(error)

    w -= learning_rate * dw
    b -= learning_rate * db

    if epoch % 10000 == 0:
        mse = np.mean(error ** 2)
        l2_penalty = (lmbda / (2 * m)) * np.sum(w ** 2)
        loss = mse + l2_penalty
        print(f"Epoch {epoch}: Loss = {loss:.2f}")

# 6) Final model output
feature_names = [
    "dow", "hour", "minute",
    "sin(dow_norm)", "cos(dow_norm)",
    "sin(minute_norm)", "cos(minute_norm)",
    "dow**2", "hour**2", "minute**2",
    "hour**3", "minute**3", "dow*(hour**2)",
    "(dow * hour)", "(dow * minute)", "(hour * minute)", "is_weekend"
]
terms = [f"{w[i]:.2f}*{feature_names[i]}" for i in range(len(w))]
model_eq = " + ".join(terms) + f" + {b:.2f}"
print("\nFinal model:")
print(f"y = {model_eq}")

# 7) Plot results
plt.figure(figsize=(20, 10))
plt.plot(y, label="Actual", marker="o")
plt.plot(y_pred, label="Predicted", marker="x")
plt.title("Actual vs Predicted Gym Occupancy")
plt.legend()
plt.grid()
plt.show()

plt.figure(figsize=(20, 10))
plt.plot(y - y_pred, label="Residuals", marker=".")
plt.title("Prediction Error")
plt.axhline(0, color="gray", linestyle="--")
plt.legend()
plt.grid()
plt.show()

# 8) Make a prediction
try:
    print("\nLet's make a prediction!")
    dow = int(input("Enter day of the week (1=Mon, ..., 7=Sun): "))
    hour = int(input("Enter hour (0–23): "))
    minute = int(input("Enter minute (0, 15, 30, 45): "))
except ValueError:
    print("Invalid input. Please enter integers.")
    sys.exit()

is_weekend = float(dow >= 6)
minute_of_day = hour * 60 + minute
minute_norm = (minute_of_day / (24 * 60)) * 2 * np.pi
dow_norm = (dow / 7) * 2 * np.pi
hour_cubed = hour ** 3
minute_cubed = minute ** 3
dow_hour_squared = dow * (hour ** 2)

x_raw = np.array([
    dow, hour, minute,
    np.sin(dow_norm), np.cos(dow_norm),
    np.sin(minute_norm), np.cos(minute_norm),
    dow ** 2, hour ** 2, minute ** 2,
    hour_cubed, minute_cubed, dow_hour_squared,
    dow * hour, dow * minute, hour * minute,
    is_weekend
])
x_scaled = (x_raw - X_mean) / X_std
prediction = x_scaled @ w + b
if prediction < 0: prediction = 0
print(f"Predicted gym occupancy at day {dow}, {hour:02d}:{minute:02d} -> {int(prediction)} people\n")
