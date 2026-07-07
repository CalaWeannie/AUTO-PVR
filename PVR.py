# ============================================================
# Airborne Lookup Tool
# ============================================================
# Imports, global constants, Airborne theme palette, theme engine base
# ============================================================

import os
import re
import json
import configparser
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ============================================================
# FONT CONFIGURATION
# ============================================================

DEFAULT_FONT_FAMILY = "Segoe UI"
DEFAULT_FONT_SIZE = 10
DEFAULT_FONT = (DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)

# ============================================================
# AIRBORNE SYSTEMS COLOR PALETTES (MODERNIZED)
# ============================================================

# Light mode
LIGHT_BG = "#F5F6F7"
LIGHT_PANEL = "#FFFFFF"
LIGHT_BORDER = "#DDDDDD"
LIGHT_TEXT = "#1A1A1A"
LIGHT_ACCENT_RED = "#C8102E"
AIRBORNE_BLUE = "#004481"

# Dark mode
DARK_BG = "#1F1F1F"
DARK_PANEL = "#2B2B2B"
DARK_BORDER = "#3A3A3A"
DARK_TEXT = "#F0F0F0"
DARK_ACCENT_RED = "#A00F25"

# Status colors
STATUS_FOUND = "#0A9B31"
STATUS_NOT_FOUND = "#C8102E"
STATUS_SKIPPED = "#888888"
STATUS_WAITING = "#666666"

# ============================================================
# DEFAULT DIRECTORY PATHS
# ============================================================

DEFAULT_DRAWING_DIR = r"L:\\CONTROLLED PDF's\\Drawings"
DEFAULT_EO_DIR = r"L:\\CONTROLLED PDF's\\EO's and Deviation-Waivers\\Drawings"
DEFAULT_PATTERN_DIR = r"G:\\Operations\\Industrial Engineering Dept\\Patterns Approval Log\\Patterns\\MANUFACTURING'S PATTERNS & JIGS 01"

# ============================================================
# CONFIG FILE LOADING (settings.ini)
# ============================================================

config = configparser.ConfigParser()
if os.path.exists("settings.ini"):
    config.read("settings.ini")
    DRAWING_DIR = config["paths"].get("drawings_dir", DEFAULT_DRAWING_DIR)
    EO_DIR = config["paths"].get("eo_dir", DEFAULT_EO_DIR)
    PATTERN_DIR = config["paths"].get("patterns_dir", DEFAULT_PATTERN_DIR)
else:
    DRAWING_DIR = DEFAULT_DRAWING_DIR
    EO_DIR = DEFAULT_EO_DIR
    PATTERN_DIR = DEFAULT_PATTERN_DIR

# ============================================================
# USER CHECKBOX PREFERENCES (preferences.json)
# ============================================================

def load_checkbox_preferences():
    if not os.path.exists("preferences.json"):
        return {}
    try:
        with open("preferences.json", "r") as f:
            return json.load(f)
    except:
        return {}

USER_PREFS = load_checkbox_preferences()

# ============================================================
# REVISION ORDER LOGIC
# ============================================================

REV_ORDER = ["NC"] + [chr(c) for c in range(ord("A"), ord("Z") + 1)]

def revision_value(rev):
    rev = rev.upper()
    if rev.isdigit():
        return 100 + int(rev)
    if rev in REV_ORDER:
        return REV_ORDER.index(rev)
    return 999

# ============================================================
# SEARCH REGISTRY + SEARCH ENGINE
# ============================================================

SEARCH_ITEMS = {
    "drawing_pdf": {
        "label": "Drawing PDF",
        "type": "pdf_revision",
        "enabled": True,
        "path": DRAWING_DIR
    },
    "eo_pdf": {
        "label": "EO PDF",
        "type": "pdf_revision",
        "enabled": True,
        "path": EO_DIR
    },
    "pattern_folder": {
        "label": "Pattern Folder",
        "type": "folder",
        "enabled": False,
        "path": PATTERN_DIR
    },
    "iwo": {
        "label": "IWO",
        "type": "syspro_lookup",
        "enabled": False,
        "path": None
    },
    "posys": {
        "label": "POSYS Info",
        "type": "syspro_lookup",
        "enabled": False,
        "path": None
    },
    "pro_info": {
        "label": "PRO Info",
        "type": "syspro_lookup",
        "enabled": False,
        "path": None
    }
}

# ============================================================
# FILE SEARCHING LOGIC
# ============================================================

def find_latest_revision_pdf(folder, part):
    """Return highest revision PDF for part inside folder."""
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
    return os.path.join(folder, files[-1][1])


def search_pdf_revision(item_key, part_number):
    """Search for part folder → highest rev PDF inside."""
    item = SEARCH_ITEMS[item_key]
    base_dir = item["path"]
    folder = os.path.join(base_dir, part_number[:3])
    return find_latest_revision_pdf(folder, part_number) if os.path.exists(folder) else None


def search_folder(item_key, part_number):
    """Look for folder matching part number exactly."""
    item = SEARCH_ITEMS[item_key]
    full_path = os.path.join(item["path"], part_number)
    return full_path if os.path.exists(full_path) else None


def search_syspro_placeholder(item_key, part_number):
    """Placeholder - can fill with real SYSPRO/POSYS logic later."""
    return None


def run_search(item_key, part_number):
    """Dispatch search depending on item type."""
    item = SEARCH_ITEMS[item_key]
    t = item["type"]

    if t == "pdf_revision":
        return search_pdf_revision(item_key, part_number)

    if t == "folder":
        return search_folder(item_key, part_number)

    if t == "syspro_lookup":
        return search_syspro_placeholder(item_key, part_number)

    return None

# ------------------------------------------------------------
# THEME ENGINE CLASS
# ------------------------------------------------------------

class ThemeEngine:
    """Handles light/dark mode styling for the entire UI."""

    def __init__(self, root):
        self.root = root
        self.dark_mode = False  # default, will be overwritten by preference later

        # Store all themed widgets for dynamic updates
        self.themable_frames = []
        self.themable_labels = []
        self.themable_entries = []
        self.themable_buttons = []
        self.themable_text_widgets = []
        self.themable_labelframes = []
        self.themable_checkboxes = []

    def apply_theme(self):
        """Apply the active theme across all registered widgets."""

        if self.dark_mode:
            bg = DARK_BG
            panel = DARK_PANEL
            border = DARK_BORDER
            text = DARK_TEXT
        else:
            bg = LIGHT_BG
            panel = LIGHT_PANEL
            border = LIGHT_BORDER
            text = LIGHT_TEXT

        # Root background
        self.root.configure(bg=bg)

        # Frames
        for f in self.themable_frames:
            f.configure(style="Custom.TFrame")

        # LabelFrames
        for lf in self.themable_labelframes:
            lf.configure(style="Custom.TLabelframe")

        # Labels
        for lbl in self.themable_labels:
            lbl.configure(style="Custom.TLabel")

        # Entry boxes
        for entry in self.themable_entries:
            entry.configure(background=panel, foreground=text, insertbackground=text)

        # Buttons
        for btn in self.themable_buttons:
            btn.configure(style="Accent.TButton")

        # Text widgets (logs)
        for txt in self.themable_text_widgets:
            txt.configure(bg=panel, fg=text, insertbackground=text)

        # Checkboxes
        for chk in self.themable_checkboxes:
            chk.configure(style="Custom.TCheckbutton")

        self._apply_styles()

    def _apply_styles(self):
        """Configure ttk style objects for all theme-aware widget classes."""
        style = ttk.Style()

        if self.dark_mode:
            bg = DARK_BG
            panel = DARK_PANEL
            border = DARK_BORDER
            text = DARK_TEXT
        else:
            bg = LIGHT_BG
            panel = LIGHT_PANEL
            border = LIGHT_BORDER
            text = LIGHT_TEXT

        style.configure("Custom.TFrame", background=bg)
        style.configure("Custom.TLabelframe", background=bg, foreground=text)
        style.configure("Custom.TLabel", background=bg, foreground=text, font=DEFAULT_FONT)
        style.configure("Custom.TCheckbutton", background=bg, foreground=text, font=DEFAULT_FONT)

        # Notebook tabs
        style.configure("TNotebook", background=bg, bordercolor=border)
        style.configure("TNotebook.Tab", background=panel, padding=(10, 5), font=DEFAULT_FONT)
        style.map("TNotebook.Tab",
                  background=[("selected", AIRBORNE_BLUE)],
                  foreground=[("selected", "white")])

        # Buttons
        style.configure("Accent.TButton",
                        background=AIRBORNE_BLUE,
                        foreground="white",
                        font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE, "bold"),
                        padding=6)
        style.map("Accent.TButton",
                  background=[("active", "#003764")])

    def toggle_dark_mode(self):
        """Flip dark mode state."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()


# ============================================================
# MAIN APPLICATION ROOT WINDOW
# ============================================================

root = tk.Tk()
root.title("Airborne Lookup Tool - Modern UI Edition")
root.geometry("900x700")
root.configure(bg=LIGHT_BG)  # initial background before theme engine loads

# Apply modern default font globally
root.option_add("*Font", DEFAULT_FONT)

# ============================================================
# NOTEBOOK TABS
# ============================================================

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

tab_search = ttk.Frame(notebook, style="Custom.TFrame")
tab_logs = ttk.Frame(notebook, style="Custom.TFrame")
tab_settings = ttk.Frame(notebook, style="Custom.TFrame")

notebook.add(tab_search, text="Search")
notebook.add(tab_logs, text="Logs")
notebook.add(tab_settings, text="Settings")

# ============================================================
# THEME ENGINE INSTANCE
# ============================================================

theme_engine = ThemeEngine(root)

# ============================================================
# PRESET SYSTEM
# ============================================================

PRESETS = {
    "Full Search": ["drawing_pdf", "eo_pdf", "pattern_folder"],
    "Drawings Only": ["drawing_pdf"],
    "EO Only": ["eo_pdf"],
    "Patterns Only": ["pattern_folder"],
    "All Disabled": []
}

def apply_preset(preset_name, checkbox_vars, status_vars, add_log):
    """Enable/disable search items according to preset."""
    if preset_name not in PRESETS:
        return

    enabled = PRESETS[preset_name]
    for key in checkbox_vars:
        checkbox_vars[key].set(key in enabled)
        status_vars[key].set("waiting...")

    add_log(f"Preset applied: {preset_name}")


# ============================================================
# STATUS ANIMATION UTILITIES
# ============================================================

def animate_status_label(label_widget, final_color):
    """Fade in color animation for status labels."""
    # Colors transition from gray → target color
    steps = 8
    start_color = "#444444"

    # Extract RGB
    sr, sg, sb = int(start_color[1:3], 16), int(start_color[3:5], 16), int(start_color[5:7], 16)
    fr, fg, fb = int(final_color[1:3], 16), int(final_color[3:5], 16), int(final_color[5:7], 16)

    # Increment per step
    dr = (fr - sr) // steps
    dg = (fg - sg) // steps
    db = (fb - sb) // steps

    def step(i=0, r=sr, g=sg, b=sb):
        if i >= steps:
            label_widget.configure(fg=final_color)
            return
        color = f"#{r:02X}{g:02X}{b:02X}"
        label_widget.configure(fg=color)
        label_widget.after(30, lambda: step(i + 1, r + dr, g + dg, b + db))

    step()


# ============================================================
# KEYBOARD SHORTCUT FOUNDATION
# ============================================================

def register_global_shortcuts(root, perform_search, open_logs_tab, apply_default_preset):
    """Setup Ctrl+L, Ctrl+P, Ctrl+S, Enter."""
    root.bind("<Return>", lambda e: perform_search())
    root.bind("<Control-l>", lambda e: open_logs_tab())
    root.bind("<Control-L>", lambda e: open_logs_tab())
    root.bind("<Control-p>", lambda e: apply_default_preset())
    root.bind("<Control-P>", lambda e: apply_default_preset())

# -------------------------------
# Part Number Input Section
# -------------------------------
frame_input = ttk.Frame(tab_search, style="Custom.TFrame")
frame_input.pack(pady=(10, 5), padx=15, anchor="w")

theme_engine.themable_frames.append(frame_input)

lbl_part = ttk.Label(frame_input, text="Part Number:", style="Custom.TLabel")
lbl_part.grid(row=0, column=0, padx=5, pady=5, sticky="w")
theme_engine.themable_labels.append(lbl_part)

entry_part = ttk.Entry(frame_input, width=35, font=DEFAULT_FONT)
entry_part.grid(row=0, column=1, padx=5, pady=5, sticky="w")
theme_engine.themable_entries.append(entry_part)

# Autofocus the part number field on startup
root.after(150, lambda: entry_part.focus_set())

# -------------------------------
# CHECKBOXES SECTION
# -------------------------------
frame_checks = ttk.LabelFrame(tab_search, text="Search Options", padding=10, style="Custom.TLabelframe")
frame_checks.pack(fill="x", padx=15, pady=(5, 10))

theme_engine.themable_labelframes.append(frame_checks)

checkbox_vars = {}

for key, item in SEARCH_ITEMS.items():
    initial_value = USER_PREFS.get(key, item["enabled"])
    var = tk.BooleanVar(value=initial_value)
    checkbox_vars[key] = var

    cb = ttk.Checkbutton(
        frame_checks,
        text=item["label"],
        variable=var,
        style="Custom.TCheckbutton"
    )
    cb.pack(anchor="w", padx=10, pady=2)
    theme_engine.themable_checkboxes.append(cb)

# -------------------------------
# STATUS FIELDS SECTION
# -------------------------------
frame_status = ttk.LabelFrame(tab_search, text="Status", padding=10, style="Custom.TLabelframe")
frame_status.pack(fill="x", padx=15, pady=(5, 15))
theme_engine.themable_labelframes.append(frame_status)

status_vars = {}
status_labels = {}

row = 0
for key, item in SEARCH_ITEMS.items():
    status_vars[key] = tk.StringVar(value="waiting...")

    lbl_name = ttk.Label(frame_status, text=item["label"], style="Custom.TLabel")
    lbl_name.grid(row=row, column=0, sticky="w", padx=5, pady=3)
    theme_engine.themable_labels.append(lbl_name)

    lbl_status = ttk.Label(frame_status, textvariable=status_vars[key], style="Custom.TLabel")
    lbl_status.grid(row=row, column=1, sticky="w", padx=5, pady=3)
    theme_engine.themable_labels.append(lbl_status)

    status_labels[key] = lbl_status
    row += 1

# ============================================================
# SEARCH EXECUTION ENGINE + LOGGING CALLS
# ============================================================

# -------------------------------
# LOG WINDOW (in Logs tab)
# -------------------------------
log_frame = ttk.Frame(tab_logs, style="Custom.TFrame", padding=10)
log_frame.pack(fill="both", expand=True)
theme_engine.themable_frames.append(log_frame)

log_text = tk.Text(
    log_frame,
    height=20,
    width=90,
    wrap="word",
    font=DEFAULT_FONT,
    borderwidth=1,
    relief="solid"
)
log_text.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
theme_engine.themable_text_widgets.append(log_text)

log_scroll = ttk.Scrollbar(log_frame, command=log_text.yview)
log_scroll.grid(row=0, column=1, sticky="ns")

log_text.configure(yscrollcommand=log_scroll.set)

log_frame.grid_rowconfigure(0, weight=1)
log_frame.grid_columnconfigure(0, weight=1)

# -------------------------------
# LOGGING FUNCTION
# -------------------------------
def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_text.insert("end", f"[{timestamp}] {message}\n")
    log_text.see("end")


# -------------------------------
# CHANGE STATUS AND RECOLOR
# -------------------------------
def update_status(key, new_text, color):
    status_vars[key].set(new_text)
    animate_status_label(status_labels[key], color)


# -------------------------------
# SWITCH TO LOGS TAB
# -------------------------------
def switch_to_logs_tab():
    notebook.select(tab_logs)


# -------------------------------
# EXECUTE SEARCH
# -------------------------------
def perform_search(event=None):
    part = entry_part.get().strip()

    if not part:
        messagebox.showwarning("Input Error", "Enter a part number.")
        return

    # Auto-switch to Logs tab
    switch_to_logs_tab()

    add_log(f"Starting search for: {part}")
    
    # Run each selected search item
    for key, var in checkbox_vars.items():
        label = SEARCH_ITEMS[key]["label"]

        if var.get():
            update_status(key, "searching...", STATUS_WAITING)
            add_log(f"Searching {label}...")

            result = run_search(key, part)

            if result:
                update_status(key, "Found", STATUS_FOUND)
                add_log(f"✔ {label} FOUND")

                # Try to open file if it's a path
                try:
                    if os.path.exists(result):
                        os.startfile(result)
                except Exception:
                    pass
            else:
                update_status(key, "Not Found", STATUS_NOT_FOUND)
                add_log(f"✘ {label} NOT FOUND")

        else:
            update_status(key, "Skipped", STATUS_SKIPPED)
            add_log(f"- {label} skipped")

    add_log("Search complete.\n")


# -------------------------------
# SEARCH BUTTON
# -------------------------------
btn_search = ttk.Button(
    tab_search,
    text="Run Search",
    style="Accent.TButton",
    command=perform_search
)
btn_search.pack(pady=(5, 15))

theme_engine.themable_buttons.append(btn_search)

# Bind Enter to run search
entry_part.bind("<Return>", perform_search)

# ============================================================
# CLEAR STATUS BUTTON + PRESET DROPDOWN
# ============================================================

# -------------------------------
# CLEAR STATUS BUTTON
# -------------------------------
def clear_status():
    for key in status_vars:
        status_vars[key].set("waiting...")
        animate_status_label(status_labels[key], STATUS_WAITING)
    add_log("Status cleared.")

btn_clear_status = ttk.Button(
    tab_search,
    text="Clear Status",
    style="Accent.TButton",
    command=clear_status
)
btn_clear_status.pack(pady=(0, 10))
theme_engine.themable_buttons.append(btn_clear_status)


# -------------------------------
# PRESET DROPDOWN + APPLY BUTTON
# -------------------------------
preset_frame = ttk.Frame(tab_search, style="Custom.TFrame")
preset_frame.pack(fill="x", padx=15, pady=(0, 10))
theme_engine.themable_frames.append(preset_frame)

lbl_preset = ttk.Label(preset_frame, text="Preset:", style="Custom.TLabel")
lbl_preset.grid(row=0, column=0, padx=5, pady=5, sticky="w")
theme_engine.themable_labels.append(lbl_preset)

preset_var = tk.StringVar(value="Full Search")
preset_dropdown = ttk.Combobox(
    preset_frame,
    textvariable=preset_var,
    values=list(PRESETS.keys()),
    state="readonly",
    width=25
)
preset_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")

def apply_selected_preset():
    preset_name = preset_var.get()
    apply_preset(preset_name, checkbox_vars, status_vars, add_log)

btn_apply_preset = ttk.Button(
    preset_frame,
    text="Apply Preset",
    style="Accent.TButton",
    command=apply_selected_preset
)
btn_apply_preset.grid(row=0, column=2, padx=10, pady=5)
theme_engine.themable_buttons.append(btn_apply_preset)


# -------------------------------
# DEFAULT PRESET FOR SHORTCUT
# -------------------------------
def apply_default_preset():
    apply_preset("Full Search", checkbox_vars, status_vars, add_log)


# -------------------------------
# SECTION SEPARATOR LINE
# -------------------------------
separator = ttk.Separator(tab_search, orient="horizontal")

# ============================================================
# SETTINGS TAB (Directories + Preferences)
# ============================================================

settings_frame = ttk.Frame(tab_settings, style="Custom.TFrame", padding=20)
settings_frame.pack(fill="both", expand=True)
theme_engine.themable_frames.append(settings_frame)

lbl_settings_header = ttk.Label(
    settings_frame,
    text="Settings Panel",
    style="Custom.TLabel",
    font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE + 2, "bold")
)
lbl_settings_header.pack(anchor="w", pady=(0, 10))
theme_engine.themable_labels.append(lbl_settings_header)

# -------------------------------
# CURRENT DIRECTORY PATHS SECTION
# -------------------------------
dirs_frame = ttk.LabelFrame(
    settings_frame,
    text="Current Directory Paths",
    padding=10,
    style="Custom.TLabelframe"
)
dirs_frame.pack(fill="x", pady=(5, 15))
theme_engine.themable_labelframes.append(dirs_frame)

lbl_dir1 = ttk.Label(dirs_frame, text=f"Drawings Directory:\n{DRAWING_DIR}", style="Custom.TLabel")
lbl_dir2 = ttk.Label(dirs_frame, text=f"EO Directory:\n{EO_DIR}", style="Custom.TLabel")
lbl_dir3 = ttk.Label(dirs_frame, text=f"Patterns Directory:\n{PATTERN_DIR}", style="Custom.TLabel")

lbl_dir1.pack(anchor="w", pady=3)
lbl_dir2.pack(anchor="w", pady=3)
lbl_dir3.pack(anchor="w", pady=3)

theme_engine.themable_labels += [lbl_dir1, lbl_dir2, lbl_dir3]

# -------------------------------
# EDITABLE DIRECTORY PATHS
# -------------------------------
paths_frame = ttk.LabelFrame(
    settings_frame,
    text="Edit Directory Paths",
    padding=10,
    style="Custom.TLabelframe"
)
paths_frame.pack(fill="x", pady=(5, 15))
theme_engine.themable_labelframes.append(paths_frame)

drawings_path_var = tk.StringVar(value=DRAWING_DIR)
eo_path_var = tk.StringVar(value=EO_DIR)
patterns_path_var = tk.StringVar(value=PATTERN_DIR)

def entry_field(parent, label_text, var, on_blur=None):
    lbl = ttk.Label(parent, text=label_text, style="Custom.TLabel")
    ent = ttk.Entry(parent, textvariable=var, width=70, font=DEFAULT_FONT)
    lbl.pack(anchor="w", pady=2)
    ent.pack(anchor="w", pady=(0, 5))
    theme_engine.themable_labels.append(lbl)
    theme_engine.themable_entries.append(ent)
    if on_blur:
        ent.bind("<FocusOut>", lambda e: on_blur())
    return ent

# -------------------------------
# SAVE SETTINGS (auto-saved on blur)
# -------------------------------
def save_settings():
    global DRAWING_DIR, EO_DIR, PATTERN_DIR

    new_drawing = drawings_path_var.get().strip()
    new_eo = eo_path_var.get().strip()
    new_pattern = patterns_path_var.get().strip()

    if (new_drawing == DRAWING_DIR and new_eo == EO_DIR and new_pattern == PATTERN_DIR):
        return

    DRAWING_DIR = new_drawing
    EO_DIR = new_eo
    PATTERN_DIR = new_pattern

    SEARCH_ITEMS["drawing_pdf"]["path"] = DRAWING_DIR
    SEARCH_ITEMS["eo_pdf"]["path"] = EO_DIR
    SEARCH_ITEMS["pattern_folder"]["path"] = PATTERN_DIR

    config["paths"] = {
        "drawings_dir": DRAWING_DIR,
        "eo_dir": EO_DIR,
        "patterns_dir": PATTERN_DIR
    }
    with open("settings.ini", "w") as configfile:
        config.write(configfile)

    lbl_dir1.configure(text=f"Drawings Directory:\n{DRAWING_DIR}")
    lbl_dir2.configure(text=f"EO Directory:\n{EO_DIR}")
    lbl_dir3.configure(text=f"Patterns Directory:\n{PATTERN_DIR}")

    add_log("Settings saved.")

entry_field(paths_frame, "Drawings Directory:", drawings_path_var, on_blur=save_settings)
entry_field(paths_frame, "EO Directory:", eo_path_var, on_blur=save_settings)
entry_field(paths_frame, "Patterns Directory:", patterns_path_var, on_blur=save_settings)

# -------------------------------
# RESTORE DEFAULT SETTINGS
# -------------------------------
def reset_settings():
    drawings_path_var.set(DEFAULT_DRAWING_DIR)
    eo_path_var.set(DEFAULT_EO_DIR)
    patterns_path_var.set(DEFAULT_PATTERN_DIR)
    save_settings()
    add_log("Default directory paths restored.")
    messagebox.showinfo("Defaults Restored", "Default paths have been restored.")

btn_reset_settings = ttk.Button(
    settings_frame,
    text="Restore Defaults",
    style="Accent.TButton",
    command=reset_settings
)
btn_reset_settings.pack(anchor="w", pady=(0, 10))
theme_engine.themable_buttons.append(btn_reset_settings)

# ============================================================
# DARK MODE TOGGLE + THEME PERSISTENCE
# ============================================================

# -------------------------------
# LOAD DARK MODE PREFERENCE
# -------------------------------
def load_dark_mode_preference():
    if not os.path.exists("preferences.json"):
        return False
    try:
        with open("preferences.json", "r") as f:
            data = json.load(f)
            return data.get("dark_mode", False)
    except:
        return False

theme_engine.dark_mode = load_dark_mode_preference()


# -------------------------------
# SAVE DARK MODE PREFERENCE
# -------------------------------
def save_dark_mode_preference():
    prefs = load_checkbox_preferences()
    prefs["dark_mode"] = theme_engine.dark_mode
    with open("preferences.json", "w") as f:
        json.dump(prefs, f, indent=4)


# -------------------------------
# DARK MODE TOGGLE BUTTON
# -------------------------------
def toggle_dark_mode():
    theme_engine.toggle_dark_mode()
    save_dark_mode_preference()
    add_log(f"Dark mode toggled: {'ON' if theme_engine.dark_mode else 'OFF'}")

btn_dark_mode = ttk.Button(
    settings_frame,
    text="Toggle Dark Mode",
    style="Accent.TButton",
    command=toggle_dark_mode
)
btn_dark_mode.pack(anchor="w", pady=(10, 5))
theme_engine.themable_buttons.append(btn_dark_mode)


# -------------------------------
# APPLY THEME ON INITIAL LOAD
# -------------------------------
root.after(100, theme_engine.apply_theme)

# ============================================================
# SAVE CHECKBOX PREFERENCES ON EXIT
# ============================================================

def save_checkbox_preferences():
    """Save all checkbox states + dark mode to preferences.json."""
    prefs = {key: var.get() for key, var in checkbox_vars.items()}
    prefs["dark_mode"] = theme_engine.dark_mode
    try:
        with open("preferences.json", "w") as f:
            json.dump(prefs, f, indent=4)
    except Exception as e:
        add_log(f"Error saving preferences: {e}")


# ============================================================
# HANDLE WINDOW CLOSE EVENT
# ============================================================

def on_close():
    save_settings()
    save_checkbox_preferences()
    add_log("Preferences saved. Exiting application.")
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)

# ============================================================
# KEYBOARD SHORTCUTS (CTRL+L, CTRL+P, CTRL+S, ENTER)
# ============================================================

def open_logs_tab():
    notebook.select(tab_logs)

def shortcut_search():
    perform_search()

def shortcut_apply_preset():
    apply_default_preset()

# Register shortcuts
root.bind("<Return>", lambda e: perform_search())
root.bind("<Control-s>", lambda e: shortcut_search())
root.bind("<Control-S>", lambda e: shortcut_search())

root.bind("<Control-l>", lambda e: open_logs_tab())
root.bind("<Control-L>", lambda e: open_logs_tab())

root.bind("<Control-p>", lambda e: shortcut_apply_preset())
root.bind("<Control-P>", lambda e: shortcut_apply_preset())

# ============================================================
# THEME REGISTRATION + PERIODIC AUTOSAVE
# ============================================================

# -------------------------------
# REGISTER ALL WIDGETS FOR THEME ENGINE
# -------------------------------
def register_widget_for_theme(widget, widget_type):
    """Attach widgets to the correct theme group."""
    if widget_type == "frame":
        theme_engine.themable_frames.append(widget)
    elif widget_type == "labelframe":
        theme_engine.themable_labelframes.append(widget)
    elif widget_type == "label":
        theme_engine.themable_labels.append(widget)
    elif widget_type == "entry":
        theme_engine.themable_entries.append(widget)
    elif widget_type == "button":
        theme_engine.themable_buttons.append(widget)
    elif widget_type == "text":
        theme_engine.themable_text_widgets.append(widget)
    elif widget_type == "checkbox":
        theme_engine.themable_checkboxes.append(widget)


# -------------------------------
# PERIODIC AUTOSAVE OF PREFERENCES
# -------------------------------
def autosave_preferences():
    save_checkbox_preferences()
    root.after(30000, autosave_preferences)  # autosave every 30 seconds

root.after(30000, autosave_preferences)


# -------------------------------
# RESTORE CHECKBOX STATES ON LOAD
# (already loaded into USER_PREFS earlier)
# -------------------------------
for key, var in checkbox_vars.items():
    if key in USER_PREFS:
        var.set(USER_PREFS[key])


# -------------------------------
# REAPPLY THEME TO ENSURE ALL WIDGETS ARE STYLED
# -------------------------------
root.after(150, theme_engine.apply_theme)

# ============================================================
# UI POLISH + AIRBORNE ACCENT STRIPE + LOG TAB HEADER
# ============================================================

# -------------------------------
# AIRBORNE ACCENT STRIPE (RED)
# -------------------------------
accent_stripe = tk.Frame(root, height=4, bg=LIGHT_ACCENT_RED)
accent_stripe.place(relx=0, rely=0, relwidth=1)

def update_stripe_theme():
    accent_stripe.configure(bg=DARK_ACCENT_RED if theme_engine.dark_mode else LIGHT_ACCENT_RED)

# Rebind stripe to theme changes
original_apply_theme = theme_engine.apply_theme
def patched_apply_theme():
    original_apply_theme()
    update_stripe_theme()

theme_engine.apply_theme = patched_apply_theme


# -------------------------------
# LOGS TAB HEADER LABEL
# -------------------------------
log_header = ttk.Label(
    tab_logs,
    text="Search Log",
    style="Custom.TLabel",
    font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE + 2, "bold")
)
log_header.pack(anchor="w", padx=15, pady=(5, 5))
theme_engine.themable_labels.append(log_header)

# Separator under header
log_header_sep = ttk.Separator(tab_logs, orient="horizontal")
log_header_sep.pack(fill="x", padx=10, pady=(0, 10))


# -------------------------------
# EXTRA POLISH: ADD SPACING TO TABS
# -------------------------------
tab_search.configure(padding=(10, 10, 10, 10))
tab_logs.configure(padding=(10, 10, 10, 10))
tab_settings.configure(padding=(10, 10, 10, 10))


# -------------------------------
# REFRESH THEME NOW THAT NEW WIDGETS ARE ADDED
# -------------------------------
root.after(200, theme_engine.apply_theme)

# ============================================================
# FINAL UI ASSEMBLY + THEME REFRESH + LAYOUT CLEANUP
# ============================================================

# -------------------------------
# REAPPLY THEME AFTER ALL WIDGETS ARE REGISTERED
# -------------------------------
def full_theme_refresh():
    """Reapply theme after all widgets and frames are created."""
    theme_engine.apply_theme()
    update_stripe_theme()

root.after(300, full_theme_refresh)


# -------------------------------
# FINAL LAYOUT ADJUSTMENTS
# -------------------------------
def finalize_layout():
    # Add slight padding around elements for spacing consistency
    for child in tab_search.winfo_children():
        if isinstance(child, ttk.Frame) or isinstance(child, ttk.LabelFrame):
            child.configure(padding=(10, 10))

    for child in tab_settings.winfo_children():
        if isinstance(child, ttk.Frame) or isinstance(child, ttk.LabelFrame):
            child.configure(padding=(10, 10))

    # Logs tab elements stay naturally fitted
    update_stripe_theme()

root.after(350, finalize_layout)


# -------------------------------
# STARTUP MESSAGE AND DEFAULT LOG ENTRY
# -------------------------------
def initial_log_banner():
    add_log("======================================")
    add_log(" Airborne Lookup Tool - Modern UI Loaded")
    add_log("======================================")
    add_log(f"Dark Mode: {'ON' if theme_engine.dark_mode else 'OFF'}")
    add_log("Ready.\n")

root.after(500, initial_log_banner)

# ============================================================
# MAIN LOOP
# ============================================================

# Final theme touch
root.after(600, theme_engine.apply_theme)

# Start the application
root.mainloop()

# ============================================================
# END OF AIRBORNE LOOKUP TOOL
# ============================================================
