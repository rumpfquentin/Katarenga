# This cell creates a downloadable Python script that provides a simple Tkinter UI
# to load accelerometer CSV data, integrate acceleration to velocity with optional
# ZUPT (zero-velocity updates) and detrending, and plot acceleration and velocity
# using matplotlib. It avoids seaborn and uses one chart per figure, as requested.

import os, textwrap, json, pathlib


"""
IMU Integrator UI (Tkinter + Matplotlib)
----------------------------------------
A simple desktop app to load accelerometer CSV logs, integrate acceleration to
velocity (with optional ZUPT and linear detrend between rests), and plot results.

CSV expectations (flexible headers):
- One column for time (seconds or timestamps like "2025-09-10 14:30:00.123").
- Columns for acceleration axes (e.g., ax, ay, az or X, Y, Z).
Only one acceleration column is used for 1D integration (choose forward axis).

Dependencies: Python 3.x, numpy, matplotlib. (pandas NOT required)
Run: python imu_integrator_ui.py
"""

import csv
import io
import math
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from datetime import datetime

APP_TITLE = "IMU Integrator UI — Acceleration → Velocity"

def parse_time_value(x, t0=None):
    """
    Try to parse a time value. Supports:
      - numeric seconds (float/int)
      - ISO-like timestamps: 'YYYY-mm-dd HH:MM:SS[.fff]' or 'HH:MM:SS[.fff]'
    Returns seconds relative to the first timestamp provided in a series.
    """
    # Numeric fast path
    try:
        return float(x), 'numeric'
    except Exception:
        pass
    # Try full datetime then time-only
    fmts = [
        "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S",
        "%H:%M:%S.%f", "%H:%M:%S"
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(x.strip(), fmt)
            if fmt.startswith("%H:%M"):
                # time only; use arbitrary date
                if t0 is None:
                    t0 = datetime(1970,1,1, dt.hour, dt.minute, dt.second, dt.microsecond)
                t = datetime(1970,1,1, dt.hour, dt.minute, dt.second, dt.microsecond)
            else:
                if t0 is None:
                    t0 = dt
                t = dt
            return (t - t0).total_seconds(), t0
        except Exception:
            continue
    raise ValueError(f"Unrecognized time format: {x}")

def moving_flag_rest(a, t, thr=0.15, min_rest_dur=0.3):
    """
    Return a boolean mask where the signal is considered 'at rest' (|a| < thr)
    and persists for at least min_rest_dur seconds. Uses run-length encoding over
    a simple absolute-threshold mask.
    """
    a = np.asarray(a)
    t = np.asarray(t)
    base_mask = np.abs(a) < thr
    mask = np.zeros_like(base_mask, dtype=bool)
    n = len(a)
    i = 0
    while i < n:
        if base_mask[i]:
            j = i + 1
            while j < n and base_mask[j]:
                j += 1
            # now [i, j) is a run of "rest" points
            if t[j-1] - t[i] >= min_rest_dur:
                mask[i:j] = True
            i = j
        else:
            i += 1
    return mask

def integrate_trapz(acc, t):
    """
    Trapezoidal integration of acceleration to velocity.
    v[0] = 0. Returns velocity array of same length as acc.
    """
    acc = np.asarray(acc, dtype=float)
    t = np.asarray(t, dtype=float)
    v = np.zeros_like(acc, dtype=float)
    if len(acc) < 2:
        return v
    dt = np.diff(t)
    # Guard against non-monotonic or zero dt
    dt[dt <= 0] = np.nan
    # incremental trapezoids
    dv = 0.5 * (acc[1:] + acc[:-1]) * dt
    # Replace NaNs (from bad dt) with 0 so cumulative sum doesn't blow up
    dv = np.where(np.isfinite(dv), dv, 0.0)
    v[1:] = np.cumsum(dv)
    return v

def detrend_between_resets(t, v, rest_mask):
    """
    Apply a linear detrend to force v=0 at the ends of each segment between rest regions.
    Set velocity to exactly zero where rest_mask is True.
    """
    t = np.asarray(t, dtype=float)
    v = np.array(v, dtype=float)
    v[rest_mask] = 0.0

    # Identify indices that are "anchors" (start/end of non-rest segments)
    n = len(v)
    i = 0
    while i < n:
        # skip rest
        while i < n and rest_mask[i]:
            i += 1
        if i >= n:
            break
        seg_start = i
        while i < n and not rest_mask[i]:
            i += 1
        seg_end = i - 1  # inclusive
        # Linear correction so that velocity at seg_start and seg_end are zero
        if seg_end > seg_start:
            t0, t1 = t[seg_start], t[seg_end]
            v0, v1 = v[seg_start], v[seg_end]
            # Desired endpoints are 0 and 0; current are v0 and v1
            # Build a line L(t) that goes from v0 to v1; subtract it
            # so adjusted endpoints become 0.
            denom = (t1 - t0) if t1 != t0 else 1.0
            slope = (v1 - v0) / denom
            intercept = v0 - slope * t0
            # Subtract line across this segment
            v[seg_start:seg_end+1] -= (slope * t[seg_start:seg_end+1] + intercept)
            # Also set boundaries precisely to zero
            v[seg_start] = 0.0
            v[seg_end] = 0.0
    return v

class IMUIntegratorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x720")

        self.data = {}         # column_name -> np.array
        self.headers = []      # CSV headers
        self.t = None          # time (seconds from start)
        self.a = None          # chosen acceleration
        self.v = None          # integrated velocity
        self.rest_mask = None

        self._build_ui()

    def _build_ui(self):
        # Top control frame
        ctrl = ttk.Frame(self, padding=(8,8))
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Button(ctrl, text="Open CSV…", command=self.open_csv).pack(side=tk.LEFT, padx=4)

        ttk.Label(ctrl, text="Time column:").pack(side=tk.LEFT, padx=(12,4))
        self.time_var = tk.StringVar()
        self.time_cb = ttk.Combobox(ctrl, textvariable=self.time_var, width=20, state="readonly")
        self.time_cb.pack(side=tk.LEFT, padx=4)

        ttk.Label(ctrl, text="Accel column:").pack(side=tk.LEFT, padx=(12,4))
        self.accel_var = tk.StringVar()
        self.accel_cb = ttk.Combobox(ctrl, textvariable=self.accel_var, width=20, state="readonly")
        self.accel_cb.pack(side=tk.LEFT, padx=4)

        ttk.Label(ctrl, text="Gravity offset (m/s²):").pack(side=tk.LEFT, padx=(12,4))
        self.g_offset = tk.DoubleVar(value=0.0)
        ttk.Entry(ctrl, textvariable=self.g_offset, width=8).pack(side=tk.LEFT, padx=4)
        ttk.Label(ctrl, text="(use ±9.81 if needed)").pack(side=tk.LEFT, padx=(2,10))

        ttk.Label(ctrl, text="Rest |a|<").pack(side=tk.LEFT, padx=(12,4))
        self.rest_thr = tk.DoubleVar(value=0.15)
        ttk.Entry(ctrl, textvariable=self.rest_thr, width=6).pack(side=tk.LEFT, padx=4)
        ttk.Label(ctrl, text="m/s² for ≥").pack(side=tk.LEFT, padx=(2,4))
        self.rest_dur = tk.DoubleVar(value=0.4)
        ttk.Entry(ctrl, textvariable=self.rest_dur, width=6).pack(side=tk.LEFT, padx=4)
        ttk.Label(ctrl, text="s").pack(side=tk.LEFT, padx=(2,10))

        self.use_zupt = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl, text="Use ZUPT + detrend", variable=self.use_zupt).pack(side=tk.LEFT, padx=10)

        ttk.Button(ctrl, text="Process & Plot", command=self.process_and_plot).pack(side=tk.LEFT, padx=10)

        # Figure
        self.fig = Figure(figsize=(8.2, 5.6), dpi=100)
        self.ax1 = self.fig.add_subplot(211)  # acceleration
        self.ax2 = self.fig.add_subplot(212)  # velocity

        self.ax1.set_title("Acceleration vs Time")
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Acceleration (m/s²)")

        self.ax2.set_title("Velocity vs Time (Integrated)")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Velocity (m/s)")

        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        self.canvas = canvas

        # Status bar
        self.status = tk.StringVar(value="Load a CSV to begin.")
        ttk.Label(self, textvariable=self.status, relief=tk.SUNKEN, anchor="w", padding=(6,4)).pack(side=tk.BOTTOM, fill=tk.X)

    def open_csv(self):
        path = filedialog.askopenfilename(
            title="Open accelerometer CSV",
            filetypes=[("CSV files","*.csv"), ("All files","*.*")]
        )
        if not path:
            return
        try:
            with open(path, "r", newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                rows = list(reader)
            if not rows:
                raise ValueError("Empty file.")
            headers = rows[0]
            self.headers = headers
            self.data = {h: [] for h in headers}
            for row in rows[1:]:
                if len(row) != len(headers):
                    # skip malformed lines
                    continue
                for h, val in zip(headers, row):
                    self.data[h].append(val)
            # Convert numeric where possible
            for h in headers:
                # try float conversion; if fails, keep as str for possible time parsing
                vals = self.data[h]
                try:
                    arr = np.array([float(x) for x in vals], dtype=float)
                except Exception:
                    arr = np.array(vals, dtype=object)
                self.data[h] = arr

            # Populate comboboxes
            self.time_cb["values"] = headers
            self.accel_cb["values"] = headers
            # Pre-select likely columns
            def pick(colnames, candidates):
                for c in candidates:
                    for h in colnames:
                        if h.lower() == c.lower():
                            return h
                return colnames[0] if colnames else ""

            t_guess = pick(headers, ["time", "timestamp", "t"])
            a_guess = pick(headers, ["ax", "ay", "az", "x", "y", "z", "linear_acceleration.x", "linear_acceleration.y", "linear_acceleration.z"])
            self.time_var.set(t_guess)
            self.accel_var.set(a_guess)

            self.status.set(f"Loaded {os.path.basename(path)} with {len(rows)-1} rows.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{e}")
            self.status.set("Failed to load CSV.")

    def _extract_time_seconds(self, col):
        raw = self.data[col]
        # If numeric seconds
        if raw.dtype != object:
            t = raw.astype(float)
            # Ensure strictly increasing time by small epsilon on ties
            t = np.array(t, dtype=float)
            # Fix non-increasing times
            for i in range(1, len(t)):
                if not (t[i] > t[i-1]):
                    t[i] = t[i-1] + 1e-6
            return t
        # Else parse strings
        t = np.zeros(len(raw), dtype=float)
        t0 = None
        for i, x in enumerate(raw):
            try:
                val, state = parse_time_value(x, t0)
                if state == 'numeric':
                    t[i] = val if i == 0 else (val if val > t[i-1] else t[i-1] + 1e-6)
                else:
                    # state is actually t0 (datetime) due to our implementation
                    t0 = state if isinstance(state, datetime) else t0
                    t[i] = val if i == 0 else (val if val > t[i-1] else t[i-1] + 1e-6)
            except Exception as e:
                raise ValueError(f"Time parse error at row {i+2}: {e}")
        # Normalize to start at zero
        t -= t[0]
        return t

    def process_and_plot(self):
        if not self.headers:
            messagebox.showinfo("No data", "Please load a CSV first.")
            return
        time_col = self.time_var.get()
        accel_col = self.accel_var.get()
        if not time_col or not accel_col:
            messagebox.showinfo("Select columns", "Please choose a time and an acceleration column.")
            return
        try:
            t = self._extract_time_seconds(time_col)
            a_raw = self.data[accel_col].astype(float)
        except Exception as e:
            messagebox.showerror("Error", f"Column parse error:\n{e}")
            return

        # Optional gravity offset
        g_off = float(self.g_offset.get())
        a = a_raw - g_off

        # Rest detection
        thr = max(0.0, float(self.rest_thr.get()))
        min_rest = max(0.0, float(self.rest_dur.get()))
        rest_mask = moving_flag_rest(a, t, thr=thr, min_rest_dur=min_rest)

        # Integrate
        v = integrate_trapz(a, t)

        # Apply ZUPT + detrend if requested
        if self.use_zupt.get():
            v = detrend_between_resets(t, v, rest_mask)

        # Update plots
        self.ax1.clear()
        self.ax2.clear()

        self.ax1.set_title("Acceleration vs Time")
        self.ax1.set_xlabel("Time (s)")
        self.ax1.set_ylabel("Acceleration (m/s²)")
        self.ax1.plot(t, a, linewidth=1.2)
        # shade rest regions
        if rest_mask.any():
            # Find contiguous rest blocks to shade
            n = len(rest_mask)
            i = 0
            while i < n:
                if rest_mask[i]:
                    j = i + 1
                    while j < n and rest_mask[j]:
                        j += 1
                    self.ax1.axvspan(t[i], t[j-1], alpha=0.15)
                    i = j
                else:
                    i += 1

        self.ax2.set_title("Velocity vs Time (Integrated)")
        self.ax2.set_xlabel("Time (s)")
        self.ax2.set_ylabel("Velocity (m/s)")
        self.ax2.plot(t, v, linewidth=1.2)

        self.ax1.grid(True, alpha=0.3)
        self.ax2.grid(True, alpha=0.3)

        self.fig.tight_layout()
        self.canvas.draw()

        self.t, self.a, self.v, self.rest_mask = t, a, v, rest_mask
        # Basic sanity: report end velocity at last rest (should be ~0 with ZUPT)
        info = []
        if rest_mask.any():
            last_rest_idx = np.where(rest_mask)[0][-1]
            info.append(f"last-rest v ≈ {v[last_rest_idx]:.3f} m/s")
        info.append(f"N={len(t)}")
        self.status.set("Processed. " + " | ".join(info))


if __name__ == "__main__":
    app = IMUIntegratorApp()
    app.mainloop()


path = "/mnt/data/imu_integrator_ui.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(script)

path
