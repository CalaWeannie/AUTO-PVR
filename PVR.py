import os
import re

# ----------------------
# Directory paths
# ----------------------
DRAWING_DIR = r"L:\CONTROLLED PDF's\Drawings"
EO_DIR = r"L:\CONTROLLED PDF's\EO's and Deviation-Waivers\Drawings"
PATTERN_DIR = r"G:\Operations\Industrial Engineering Dept\Patterns Approval Log\Patterns\MANUFACTURING'S PATTERNS & JIGS 01"

# ----------------------
# Revision ranking logic
# ----------------------
REV_ORDER = ["NC"] + [chr(c) for c in range(ord('A'), ord('Z') + 1)]

def revision_value(rev):
    rev = rev.upper()

    # Numeric revisions get ranked higher than letter revisions
    if rev.isdigit():
        return 100 + int(rev)

    # Letter revisions and NC
    if rev in REV_ORDER:
        return REV_ORDER.index(rev)

    # Unknown revision gets lowest priority
    return 999


# ----------------------
# Find latest revision PDF in a folder
# ----------------------
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
# Open file or folder if it exists
# ----------------------
def open_if_exists(path, description):
    if path and os.path.exists(path):
        print(f"Opening {description}: {path}")
        os.startfile(path)
    else:
        print(f"{description} NOT FOUND")


# ----------------------
# Continuous program loop
# ----------------------
while True:
    part = input("\nEnter part number (or type EXIT to quit): ").strip()

    if part.lower() == "exit":
        break

    first_three = part[:3]

    # Construct folder paths
    drawing_subfolder = os.path.join(DRAWING_DIR, first_three)
    eo_subfolder = os.path.join(EO_DIR, first_three)
    pattern_folder = os.path.join(PATTERN_DIR, part)

    # Find files
    drawing_file = find_latest_revision_pdf(drawing_subfolder, part)
    eo_file = find_latest_revision_pdf(eo_subfolder, part)

    # Open results
    open_if_exists(drawing_file, "Drawing PDF")
    open_if_exists(eo_file, "EO PDF")
    open_if_exists(pattern_folder, "Pattern Folder")

print("Program closed.")