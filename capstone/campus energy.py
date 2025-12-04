import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ===================================================================
#  Task 3: OOP Model
# ===================================================================

class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh


class Building:
    def __init__(self, name):
        self.name = name
        self.meter_readings = []

    def add_reading(self, reading: MeterReading):
        self.meter_readings.append(reading)

    def calculate_total_consumption(self):
        return sum(r.kwh for r in self.meter_readings)

    def generate_report(self):
        total = self.calculate_total_consumption()
        return f"{self.name}: Total Consumption = {total} kWh"


class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def add_reading(self, building_name, reading):
        if building_name not in self.buildings:
            self.buildings[building_name] = Building(building_name)
        self.buildings[building_name].add_reading(reading)

    def get_buildings(self):
        return self.buildings


# ===================================================================
#  Task 1: Data Ingestion & Validation
# ===================================================================

def load_data(data_folder="data"):
    df_list = []
    errors = []

    for file in Path(data_folder).glob("*.csv"):
        try:
            df = pd.read_csv(file, on_bad_lines='skip')
            df["building"] = file.stem  # add building name
            df_list.append(df)
        except Exception as e:
            errors.append(str(e))

    if not df_list:
        raise Exception("No valid CSV files found in /data/ folder!")

    df_combined = pd.concat(df_list, ignore_index=True)
    df_combined["timestamp"] = pd.to_datetime(df_combined["timestamp"])

    print("Data Loaded Successfully!")
    return df_combined


# ===================================================================
#  Task 2: Aggregation Functions
# ===================================================================

def calculate_daily_totals(df):
    return df.resample("D", on="timestamp")["kwh"].sum().reset_index()


def calculate_weekly_aggregates(df):
    return df.resample("W", on="timestamp")["kwh"].sum().reset_index()


def building_wise_summary(df):
    summary = df.groupby("building")["kwh"].agg(["mean", "min", "max", "sum"])
    summary = summary.rename(columns={"sum": "total"})
    return summary


# ===================================================================
#  Task 4: Dashboard Visualization
# ===================================================================

def generate_dashboard(df):
    plt.figure(figsize=(14, 8))
    buildings = df["building"].unique()

    # --- Daily Trend Line ---
    plt.subplot(2, 2, 1)
    for b in buildings:
        d = df[df["building"] == b].resample("D", on="timestamp")["kwh"].sum()
        plt.plot(d.index, d.values, label=b)
    plt.title("Daily Electricity Consumption")
    plt.xlabel("Date")
    plt.ylabel("kWh")
    plt.legend()

    # --- Weekly Bar Chart ---
    plt.subplot(2, 2, 2)
    weekly = df.resample("W", on="timestamp").sum().groupby(df["building"]).mean()
    plt.bar(weekly.index, weekly["kwh"])
    plt.title("Avg Weekly Usage By Building")
    plt.xlabel("Building")
    plt.ylabel("kWh")

    # --- Scatter Plot: Peak Hours ---
    plt.subplot(2, 2, 3)
    plt.scatter(df["timestamp"], df["kwh"], alpha=0.5)
    plt.title("Consumption vs Time")
    plt.xlabel("Timestamp")
    plt.ylabel("kWh")

    plt.tight_layout()
    plt.savefig("output/dashboard.png")
    plt.close()
    print("Dashboard saved as output/dashboard.png")


# ===================================================================
#  Task 5: Save Outputs & Summary
# ===================================================================

def save_outputs(df, summary):
    os.makedirs("output", exist_ok=True)

    df.to_csv("output/cleaned_energy_data.csv", index=False)
    summary.to_csv("output/building_summary.csv")

    total_consumption = df["kwh"].sum()
    highest_building = summary["total"].idxmax()
    peak_row = df.loc[df["kwh"].idxmax()]

    text = f"""
Campus Energy Summary Report
-----------------------------------------
Total Campus Consumption: {total_consumption:.2f} kWh
Highest Consuming Building: {highest_building}
Peak Load Time: {peak_row['timestamp']} (Value: {peak_row['kwh']} kWh)

Daily & Weekly Trends:
- Daily totals and weekly aggregates generated.
- Visual dashboard saved as dashboard.png.
"""

    with open("output/summary.txt", "w") as f:
        f.write(text)

    print("Summary report saved.")


# ===================================================================
#  MAIN PIPELINE
# ===================================================================

def main():
    print("\n--- Campus Energy Dashboard ---\n")

    # Load and validate data
    df = load_data()

    # Aggregations
    daily = calculate_daily_totals(df)
    weekly = calculate_weekly_aggregates(df)
    summary = building_wise_summary(df)

    # OOP population
    manager = BuildingManager()
    for _, row in df.iterrows():
        reading = MeterReading(row["timestamp"], row["kwh"])
        manager.add_reading(row["building"], reading)

    # Plot dashboard
    generate_dashboard(df)

    # Save outputs
    save_outputs(df, summary)

    print("\nProject Executed Successfully!")


if __name__ == "__main__":
    main()