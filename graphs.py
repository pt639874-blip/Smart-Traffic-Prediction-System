import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# load dataset
data = pd.read_csv("Metro_Interstate_Traffic_Volume.csv")

data["date_time"] = pd.to_datetime(data["date_time"])
data["hour"] = data["date_time"].dt.hour

# traffic state
def traffic_state(volume):

    if volume < 1500:
        return 0
    elif volume < 3500:
        return 1
    else:
        return 2

data["traffic_state"] = data["traffic_volume"].apply(traffic_state)

X = data[[
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "hour"
]]

y = data["traffic_state"]

X_train,X_test,y_train,y_test = train_test_split(
X,y,test_size=0.2,random_state=42
)

model = RandomForestClassifier(n_estimators=400)

model.fit(X_train,y_train)

pred = model.predict(X_test)

acc = accuracy_score(y_test,pred)
prec = precision_score(y_test,pred,average="weighted")
rec = recall_score(y_test,pred,average="weighted")
f1 = f1_score(y_test,pred,average="weighted")

# performance graph
metrics = ["Accuracy","Precision","Recall","F1 Score"]
values = [acc,prec,rec,f1]

plt.figure()

plt.bar(metrics,values)

plt.title("Model Performance")

plt.ylabel("Score")

plt.savefig("static/performance.png")

# traffic trend graph

traffic = data.groupby("hour")["traffic_volume"].mean()

plt.figure()

traffic.plot()

plt.title("Traffic Volume by Hour")

plt.xlabel("Hour")

plt.ylabel("Traffic Volume")

plt.grid(True)

plt.savefig("static/traffic_trend.png")

print("Graphs created")