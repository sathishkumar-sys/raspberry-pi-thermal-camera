
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import glob
import os
from datetime import datetime


class ThermalViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("MI48 Thermal Grid Viewer")
        self.root.geometry("1100x750")

        self.files = []
        self.rows = []
        self.headers = []

        self.create_interface()
        self.load_sessions()

    def create_interface(self):
        title = ttk.Label(
            self.root,
            text="MI48 THERMAL GRID VIEWER",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=12)

        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=15, pady=10)

        ttk.Label(controls, text="Recording Session:").pack(side="left")

        self.session_box = ttk.Combobox(
            controls,
            state="readonly",
            width=35
        )
        self.session_box.pack(side="left", padx=8)
        self.session_box.bind(
            "<<ComboboxSelected>>",
            self.load_selected_session
        )

        self.frame_box = ttk.Combobox(
            controls,
            state="readonly",
            width=12
        )
        self.frame_box.pack(side="left", padx=8)
        self.frame_box.bind(
            "<<ComboboxSelected>>",
            self.show_selected_frame
        )

        self.info = ttk.Label(
            self.root,
            text="Select a recording session",
            font=("Arial", 11)
        )
        self.info.pack(pady=5)

        self.grid_area = ttk.Frame(self.root)
        self.grid_area.pack(fill="both", expand=True, padx=15, pady=10)

        self.canvas = tk.Canvas(self.grid_area)
        self.scrollbar_y = ttk.Scrollbar(
            self.grid_area,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollbar_x = ttk.Scrollbar(
            self.grid_area,
            orient="horizontal",
            command=self.canvas.xview
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar_y.set,
            xscrollcommand=self.scrollbar_x.set
        )

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")

        self.grid_area.rowconfigure(0, weight=1)
        self.grid_area.columnconfigure(0, weight=1)

        self.cell_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.cell_frame,
            anchor="nw"
        )

        self.cell_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.selected_info = ttk.Label(
            self.root,
            text="Click a temperature cell to inspect it",
            font=("Arial", 12, "bold")
        )
        
        # Temperature table for selected frame
        table_frame = ttk.LabelFrame(
            self.root,
            text="Selected Frame - Zone Maximum Temperatures",
            padding=8
        )
        table_frame.pack(fill="x", padx=15, pady=5)

        self.zone_table = ttk.Treeview(
            table_frame,
            columns=("zone", "temperature"),
            show="headings",
            height=3
        )

        self.zone_table.heading("zone", text="Zone")
        self.zone_table.heading(
            "temperature",
            text="Maximum Temperature (°C)"
        )

        self.zone_table.column("zone", width=150, anchor="center")
        self.zone_table.column(
            "temperature", width=250, anchor="center"
        )

        self.zone_table.pack(fill="x")

        self.selected_info.pack(pady=12)

    def load_sessions(self):
        self.files = sorted(
            glob.glob("data/thermal_grid_*.csv"),
            key=os.path.getmtime,
            reverse=True
        )

        if not self.files:
            messagebox.showwarning(
                "No data",
                "No thermal grid CSV files found."
            )
            return

        self.session_box["values"] = [
            os.path.basename(f) for f in self.files
        ]

        self.session_box.current(0)
        self.load_selected_session()

    def load_selected_session(self, event=None):
        index = self.session_box.current()

        if index < 0:
            return

        filename = self.files[index]

        with open(filename, newline="") as file:
            reader = csv.DictReader(file)
            self.headers = reader.fieldnames
            self.rows = list(reader)

        self.frame_box["values"] = [
            row["Frame"] for row in self.rows
        ]

        if self.rows:
            self.frame_box.current(0)
            self.show_selected_frame()

    
    def show_selected_frame(self, event=None):
        index = self.frame_box.current()

        if index < 0:
            return

        record = self.rows[index]
        grid_headers = self.headers[2:]

        # Detect original sensor dimensions
        sensor_rows = len(set(
            header.split("_")[0] for header in grid_headers
        ))
        sensor_cols = len(grid_headers) // sensor_rows

        # Read all 62 x 80 sensor temperatures
        values = [
            float(record[header])
            for header in grid_headers
        ]

        # Divide sensor array into 3 x 3 zones
        for widget in self.cell_frame.winfo_children():
            widget.destroy()

        zone_values = []

        for zone_r in range(3):
            row_start = zone_r * sensor_rows // 3
            row_end = (zone_r + 1) * sensor_rows // 3

            zone_row = []

            for zone_c in range(3):
                col_start = zone_c * sensor_cols // 3
                col_end = (zone_c + 1) * sensor_cols // 3

                # Get temperatures inside this zone
                zone_temperatures = []

                for r in range(row_start, row_end):
                    for c in range(col_start, col_end):
                        value = values[r * sensor_cols + c]
                        zone_temperatures.append(value)

                # Calculate maximum temperature
                max_temp = sum(zone_temperatures) / len(zone_temperatures)
                zone_row.append(max_temp)

                # Display the zone
                color = "#ff5555" if max_temp >= 30 else "#ffbb66"

                cell = tk.Label(
                    self.cell_frame,
                    text=f"R{zone_r+1} C{zone_c+1}\n"
                         f"{max_temp:.2f} °C",
                    bg=color,
                    fg="black",
                    font=("Arial", 16, "bold"),
                    width=16,
                    height=5,
                    relief="ridge",
                    borderwidth=2
                )

                cell.grid(
                    row=zone_r,
                    column=zone_c,
                    padx=5,
                    pady=5,
                    sticky="nsew"
                )

                cell.bind(
                    "<Button-1>",
                    lambda event, r=zone_r+1,
                    c=zone_c+1, temp=max_temp:
                    self.show_cell(r, c, temp)
                )

            zone_values.append(zone_row)

        # Update timestamp
        timestamp = datetime.fromisoformat(record["Timestamp"])

        self.info.config(
            text=(
                f"Frame: {record['Frame']} | "
                f"Date: {timestamp.strftime('%d-%m-%Y')} | "
                f"Time: {timestamp.strftime('%H:%M:%S')}"
            )
        )

        overall_max = max(max(row) for row in zone_values)

        
        # Clear previous frame's table readings
        for item in self.zone_table.get_children():
            self.zone_table.delete(item)

        # Insert the nine zone temperatures
        for r in range(3):
            for c in range(3):
                zone_name = f"R{r+1}C{c+1}"
                temperature = zone_values[r][c]

                self.zone_table.insert(
                    "",
                    "end",
                    values=(zone_name, f"{temperature:.2f}")
                )

        self.selected_info.config(
            text=f"Highest temperature across all 9 zones: "
                 f"{overall_max:.2f} °C"
        )



    def show_cell(self, row, col, temp):
        self.selected_info.config(
            text=(
                f"Row {row}, Column {col} = "
                f"{temp:.2f} °C"
            )
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = ThermalViewer(root)
    root.mainloop()
