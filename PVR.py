import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

# ---------------------- 
# Directory paths
# ----------------------
DRAWING_DIR = r"L:\CONTROLLED PDF's\Drawings"
EO_DIR = r"L:\CONTROLLED PDF's\EO's and Deviation-Waivers\Drawings"
PATTERN_DIR = r"G:\Operations\Industrial Engineering Dept\Patterns Approval Log\Patterns\MANUFACTURING'S PATTERNS & JIGS 01"

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
def open_files():
    part = entry_part.get().strip()
    if not part:
        messagebox.showwarning("Input Error", "Please enter a part number.")
        return

    first_three = part[:3]
    drawing_subfolder = os.path.join(DRAWING_DIR, first_three)
    eo_subfolder = os.path.join(EO_DIR, first_three)
    pattern_folder = os.path.join(PATTERN_DIR, part)

    drawing_file = find_latest_revision_pdf(drawing_subfolder, part)
    eo_file = find_latest_revision_pdf(eo_subfolder, part)

    status_drawing.set("Found" if drawing_file else "Not Found")
    status_eo.set("Found" if eo_file else "Not Found")
    status_pattern.set("Found" if os.path.exists(pattern_folder) else "Not Found")

    # Open files
    if drawing_file:
        os.startfile(drawing_file)
    if eo_file:
        os.startfile(eo_file)
    if os.path.exists(pattern_folder):
        os.startfile(pattern_folder)

# ----------------------
# Build GUI
# ----------------------
root = tk.Tk()
root.title("Auto PVR Lookup Tool")
root.geometry("420x280")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")

# Title Label
title = ttk.Label(root, text="Auto PVR Lookup Tool", font=("Segoe UI", 14, "bold"))
title.pack(pady=10)

# Part input frame
frame_input = ttk.Frame(root)
frame_input.pack(pady=5)

ttk.Label(frame_input, text="Part Number:").grid(row=0, column=0, padx=5)
entry_part = ttk.Entry(frame_input, width=30)
entry_part.grid(row=0, column=1, padx=5)

# Open button
btn_open = ttk.Button(root, text="Open Files", command=open_files)
btn_open.pack(pady=10)

# Status Frame
frame_status = ttk.LabelFrame(root, text="Status")
frame_status.pack(padx=10, pady=10, fill="both")

status_drawing = tk.StringVar(value="Waiting…")
status_eo = tk.StringVar(value="Waiting…")
status_pattern = tk.StringVar(value="Waiting…")

ttk.Label(frame_status, text="Drawing PDF:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_status, textvariable=status_drawing).grid(row=0, column=1, sticky="w")

ttk.Label(frame_status, text="EO PDF:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_status, textvariable=status_eo).grid(row=1, column=1, sticky="w")

ttk.Label(frame_status, text="Pattern Folder:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
ttk.Label(frame_status, textvariable=status_pattern).grid(row=2, column=1, sticky="w")

root.mainloop()