import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
data = pd.read_csv("Metro_Interstate_Traffic_Volume.csv")

# Convert datetime
data["date_time"] = pd.to_datetime(data["date_time"])

# Extract hour
data["hour"] = data["date_time"].dt.hour

# Create traffic state
def traffic_state(volume):

    if volume < 1500:
        return 0
    elif volume < 3500:
        return 1
    else:
        return 2

data["traffic_state"] = data["traffic_volume"].apply(traffic_state)

# Features
X = data[[
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "hour"
]]

# Target
y = data["traffic_state"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=400)

model.fit(X_train, y_train)

# Accuracy
pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))

# Save model
pickle.dump(model, open("traffic_model.pkl", "wb"))

print("Model trained successfully")