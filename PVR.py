import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------
# Color Scheme (Airborne Systems)
# ----------------------
COLOR_NAVY = "#002F6C"
COLOR_BLUE = "#005EB8"
COLOR_LIGHTGRAY = "#E6E6E6"
COLOR_WHITE = "#FFFFFF"
COLOR_HOVER = "#004A99"

# ----------------------
# Directory paths
# ----------------------
DRAWING_DIR = r"L:\CONTROLLED PDF's\Drawings"
EO_DIR = r"L:\CONTROLLED PDF's\EO's and Deviation-Waivers\Drawings"
PATTERN_DIR = r"G:\Operations\Industrial Engineering Dept\Patterns Approval Log\Patterns\MANUFACTURING'S PATTERNS & JIGS 01"
PVR_DIR = r"G:\Operations\Cutting Dept\Pattern Buy Offs (PVR)\Pattern Verification Records"

# ----------------------
# Revision logic
# ----------------------
REV_ORDER = ["NC"] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]

def revision_value(rev):
    rev = rev.upper()
    if rev.isdigit():
        return 100 + int(rev)
    if rev in REV_ORDER:
        return REV_ORDER.index(rev)
    return 999

def find_latest_revision_pdf(folder, part):
    if not os.path.exists(folder):
        return None

    files = []
    for filename in os.listdir(folder):
        if filename.startswith(part) and filename.lower().endswith(".pdf"):
            match = re.search(r"rev[_ -]?([a-z0-9]+)", filename, re.IGNORECASE)
            revision = match.group(1) if match else "NC"
            files.append((revision, filename))

    if not files:
        return None

    files.sort(key=lambda x: revision_value(x[0]))
    latest_file = files[-1][1]
    return os.path.join(folder, latest_file)

# ----------------------
# GUI Logic
# ----------------------
def open_files(event=None):
    part = entry_part.get().strip()
    if not part:
        messagebox.showwarning("Input Error", "Please enter a part number.")
        return

    first_three = part[:3]
    drawing_subfolder = os.path.join(DRAWING_DIR, first_three)
    eo_subfolder = os.path.join(EO_DIR, first_three)
    pattern_folder = os.path.join(PATTERN_DIR, part)
    pvr_folder = os.path.join(PVR_DIR, part)

    drawing_file = find_latest_revision_pdf(drawing_subfolder, part)
    eo_file = find_latest_revision_pdf(eo_subfolder, part)

    status_drawing.set("Found" if drawing_file else "Not Found")
    status_eo.set("Found" if eo_file else "Not Found")
    status_pattern.set("Found" if os.path.exists(pattern_folder) else "Not Found")
    status_pvr.set("Found" if os.path.exists(pvr_folder) else "Not Found")

    if drawing_file:
        os.startfile(drawing_file)
    if eo_file:
        os.startfile(eo_file)
    if os.path.exists(pattern_folder):
        os.startfile(pattern_folder)
    if os.path.exists(pvr_folder):
        os.startfile(pvr_folder)

# ----------------------
# Build GUI
# ----------------------
root = tk.Tk()
root.title("Auto PVR Lookup Tool")
root.geometry("500x350")
root.resizable(False, False)
root.configure(bg=COLOR_LIGHTGRAY)

# ----------------------
# Header Bar (No Logo)
# ----------------------
header = tk.Frame(root, bg=COLOR_NAVY, height=60)
header.pack(fill="x")

title = tk.Label(header,
                 text="Auto PVR Lookup Tool",
                 font=("Segoe UI", 18, "bold"),
                 fg=COLOR_WHITE,
                 bg=COLOR_NAVY)
title.pack(pady=12)

# ----------------------
# Rounded Button Style
# ----------------------
style = ttk.Style()
style.theme_use("clam")

style.configure(
    "RoundedButton.TButton",
    font=("Segoe UI", 11, "bold"),
    foreground=COLOR_WHITE,
    background=COLOR_BLUE,
    padding=10,
    relief="flat",
    borderwidth=0
)

style.map(
    "RoundedButton.TButton",
    background=[
        ("active", COLOR_HOVER),
        ("disabled", "#999999")
    ]
)

# Hover style
style.configure("Hover.TButton",
                background=COLOR_HOVER,
                foreground=COLOR_WHITE)

# ----------------------
# Input Section
# ----------------------
frame_input = ttk.Frame(root, padding=10)
frame_input.pack(pady=10)

ttk.Label(frame_input, text="Part Number:",
          font=("Segoe UI", 11),
          background=COLOR_LIGHTGRAY).grid(row=0, column=0, padx=5)

entry_part = ttk.Entry(frame_input, width=34)
entry_part.grid(row=0, column=1, padx=5)
entry_part.bind("<Return>", open_files)  # PRESS ENTER TO SEARCH

# ----------------------
# Open Button with Hover
# ----------------------
def on_enter(e):
    btn_open.configure(style="Hover.TButton")
def on_leave(e):
    btn_open.configure(style="RoundedButton.TButton")

btn_open = ttk.Button(root, text="Open Files",
                      command=open_files,
                      style="RoundedButton.TButton")
btn_open.pack(pady=10)

btn_open.bind("<Enter>", on_enter)
btn_open.bind("<Leave>", on_leave)

# ----------------------
# Status Section
# ----------------------
frame_status = tk.LabelFrame(root, text="Status",
                             bg=COLOR_LIGHTGRAY,
                             fg=COLOR_NAVY,
                             font=("Segoe UI", 11, "bold"),
                             padx=10, pady=5)
frame_status.pack(padx=15, pady=5, fill="both")

status_drawing = tk.StringVar(value="Waiting…")
status_eo = tk.StringVar(value="Waiting…")
status_pattern = tk.StringVar(value="Waiting…")
status_pvr = tk.StringVar(value="Waiting…")
ttk.Label(frame_status, text="Drawing PDF:",
          background=COLOR_LIGHTGRAY).grid(row=0, column=0, sticky="w", pady=5)
ttk.Label(frame_status, textvariable=status_drawing,
          background=COLOR_LIGHTGRAY).grid(row=0, column=1, sticky="w")

ttk.Label(frame_status, text="EO PDF:",
          background=COLOR_LIGHTGRAY).grid(row=1, column=0, sticky="w", pady=5)
ttk.Label(frame_status, textvariable=status_eo,
          background=COLOR_LIGHTGRAY).grid(row=1, column=1, sticky="w")

ttk.Label(frame_status, text="Pattern Folder:",
          background=COLOR_LIGHTGRAY).grid(row=2, column=0, sticky="w", pady=5)
ttk.Label(frame_status, textvariable=status_pattern,
          background=COLOR_LIGHTGRAY).grid(row=2, column=1, sticky="w")

ttk.Label(frame_status, text="PVR Folder:",
          background=COLOR_LIGHTGRAY).grid(row=3, column=0, sticky="w", pady=5)
ttk.Label(frame_status, textvariable=status_pvr,
          background=COLOR_LIGHTGRAY).grid(row=3, column=1, sticky="w")

root.mainloop()