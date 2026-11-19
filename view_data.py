
import csv
import glob
import os
from datetime import datetime

# Find saved grid sessions
files = sorted(
    glob.glob("data/thermal_grid_*.csv"),
    key=os.path.getmtime,
    reverse=True
)

if not files:
    print("No thermal grid data found.")
    raise SystemExit

print("\n========== MI48 THERMAL DATA ==========")

for i, filename in enumerate(files, 1):
    print(f"{i}. {filename}")

choice = int(input("\nSelect session number: "))

if choice < 1 or choice > len(files):
    print("Invalid session number")
    raise SystemExit

filename = files[choice - 1]

with open(filename, newline="") as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    records = list(reader)

# Detect sensor dimensions
sensor_rows = len(set(
    h.split("_")[0] for h in headers[2:]
))
sensor_cols = len(headers[2:]) // sensor_rows

print("\nSession file:", filename)
print(f"Sensor grid: {sensor_rows} x {sensor_cols}")

zone_names = [
    "R1C1", "R1C2", "R1C3",
    "R2C1", "R2C2", "R2C3",
    "R3C1", "R3C2", "R3C3"
]

print("\n" + "=" * 150)

header = (
    f"{'Frame':<8}"
    f"{'Date':<13}"
    f"{'Time':<16}"
    + "".join(f"{name:<13}" for name in zone_names)
)

print(header)
print("-" * 150)

# Display every recorded frame
for record in records:

    values = [float(record[h]) for h in headers[2:]]

    zone_avg = []

    for zr in range(3):

        row_start = zr * sensor_rows // 3
        row_end = (zr + 1) * sensor_rows // 3

        for zc in range(3):

            col_start = zc * sensor_cols // 3
            col_end = (zc + 1) * sensor_cols // 3

            zone_values = [
                values[r * sensor_cols + c]
                for r in range(row_start, row_end)
                for c in range(col_start, col_end)
            ]

            zone_avg.append(sum(zone_values) / len(zone_values))

    timestamp = datetime.fromisoformat(record["Timestamp"])

    line = (
        f"{record['Frame']:<8}"
        f"{timestamp.strftime('%d-%m-%Y'):<13}"
        f"{timestamp.strftime('%H:%M:%S.%f')[:-3]:<16}"
        + "".join(f"{v:<13.2f}" for v in zone_avg)
    )

    print(line)

print("=" * 150)
print("Total frames displayed:", len(records))
print("All 9 zone values represent average temperatures.")
