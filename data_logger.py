
import csv
from pathlib import Path
from datetime import datetime


class ThermalDataLogger:
    def __init__(self, output_dir="data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        session = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Summary data file
        self.filename = self.output_dir / f"thermal_summary_{session}.csv"
        self.file = open(self.filename, "w", newline="", encoding="utf-8")
        self.writer = csv.writer(self.file)

        self.writer.writerow([
            "Timestamp", "Frame", "Minimum_C", "Maximum_C",
            "Average_C", "Centre_C"
        ])

        # Individual grid data file
        self.grid_filename = self.output_dir / f"thermal_grid_{session}.csv"
        self.grid_file = None
        self.grid_writer = None
        self.grid_shape = None

        print("Thermal data logging started")
        print("Summary file:", self.filename)
        print("Grid file:", self.grid_filename)

    def log_frame(self, frame_number, temp_img,
                  min_temp, max_temp, avg_temp, center_temp):

        timestamp = datetime.now().isoformat(timespec="milliseconds")

        # Save summary readings
        self.writer.writerow([
            timestamp,
            frame_number,
            round(float(min_temp), 2),
            round(float(max_temp), 2),
            round(float(avg_temp), 2),
            round(float(center_temp), 2)
        ])

        # Check sensor grid dimensions
        if temp_img.ndim != 2:
            raise ValueError("Expected a 2D thermal image array")

        rows, cols = temp_img.shape

        # Create grid CSV header on the first frame
        if self.grid_writer is None:
            self.grid_shape = (rows, cols)

            self.grid_file = open(
                self.grid_filename,
                "w",
                newline="",
                encoding="utf-8"
            )
            self.grid_writer = csv.writer(self.grid_file)

            headers = ["Timestamp", "Frame"]

            for r in range(1, rows + 1):
                for c in range(1, cols + 1):
                    headers.append(f"Row{r}_Column{c}")

            self.grid_writer.writerow(headers)

        elif self.grid_shape != (rows, cols):
            raise ValueError("Thermal image dimensions changed during logging")

        # Save every grid cell's temperature
        grid_values = [
            round(float(value), 2)
            for row in temp_img
            for value in row
        ]

        self.grid_writer.writerow([
            timestamp,
            frame_number,
            *grid_values
        ])

        # Flush both files after every frame
        self.file.flush()
        self.grid_file.flush()

    def close(self):
        self.file.flush()
        self.file.close()

        if self.grid_file is not None:
            self.grid_file.flush()
            self.grid_file.close()

        print("Summary and grid data saved successfully.")
