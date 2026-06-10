import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("Metro_Interstate_Traffic_Volume.csv")

data["date_time"] = pd.to_datetime(data["date_time"])

data["hour"] = data["date_time"].dt.hour

traffic = data.groupby("hour")["traffic_volume"].mean()

plt.figure()

traffic.plot()

plt.title("Average Traffic Volume by Hour")

plt.xlabel("Hour of Day")

plt.ylabel("Traffic Volume")

plt.grid(True)

plt.savefig("static/traffic_chart.png")

print("Chart created")