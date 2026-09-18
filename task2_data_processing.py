"""
TrendPulse — Task 2: Data Cleaning & CSV Export
Loads the raw JSON from Task 1, cleans it up step by step,
and saves a tidy CSV ready for Task 3 (NumPy/Pandas analysis).

Pipeline: Task 1 (fetch JSON) → Task 2 (this) → Task 3 (analyse) → Task 4 (visualise)
"""

import pandas as pd
import glob
import os

# ─── Configuration ────────────────────────────────────────────────────────────

DATA_DIR      = "data"
OUTPUT_CSV    = os.path.join(DATA_DIR, "trends_clean.csv")

# Minimum score a story must have to be considered good quality
MIN_SCORE = 5

# ─── Step 1: Load the JSON file ───────────────────────────────────────────────

# Task 1 saves the file with today's date in the name (trends_YYYYMMDD.json).
# Instead of hard-coding the date, we use glob to find whichever file is there.
json_files = glob.glob(os.path.join(DATA_DIR, "trends_*.json"))

# Exclude the clean CSV if it somehow matches (it won't, but good to be safe)
json_files = [f for f in json_files if "clean" not in f]

if not json_files:
    print(f"[ERROR] No trends JSON file found in '{DATA_DIR}/'. Run Task 1 first.")
    exit(1)

# If multiple date-stamped files exist, pick the most recent one
json_path = sorted(json_files)[-1]

# Load JSON directly into a Pandas DataFrame — each dict in the list becomes a row
df = pd.read_json(json_path)

print(f"Loaded {len(df)} stories from {json_path}")
print()   # blank line to match expected output style

# ─── Step 2: Clean the data ───────────────────────────────────────────────────

# --- 2a: Remove duplicate stories (same post_id = same HN story fetched twice) ---
before = len(df)
df = df.drop_duplicates(subset="post_id")
print(f"After removing duplicates: {len(df)}")

# --- 2b: Drop rows missing critical fields ---
# A story without post_id, title, or score can't be analysed or displayed usefully.
# 'how="any"' drops a row if ANY of these columns is NaN.
df = df.dropna(subset=["post_id", "title", "score"])
print(f"After removing nulls: {len(df)}")

# --- 2c: Fix data types ---
# JSON numbers are sometimes read as floats (e.g. 42.0) — cast to int.
# 'num_comments' may also be NaN on stories with no comments; fill with 0 first.
df["num_comments"] = df["num_comments"].fillna(0).astype(int)
df["score"]        = df["score"].astype(int)
df["post_id"]      = df["post_id"].astype(int)

# --- 2d: Remove low-quality stories (score below threshold) ---
df = df[df["score"] >= MIN_SCORE]
print(f"After removing low scores: {len(df)}")
print()

# --- 2e: Strip extra whitespace from titles ---
# Handles leading/trailing spaces that can sneak in from the API response
df["title"] = df["title"].str.strip()

# ─── Step 3: Save as CSV ──────────────────────────────────────────────────────

# Make sure the data/ folder exists (it should, but just in case)
os.makedirs(DATA_DIR, exist_ok=True)

# Save without the Pandas default index column (cleaner for Task 3 to load)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"Saved {len(df)} rows to {OUTPUT_CSV}")
print()

# --- Print per-category story count as a quick sanity check ---
print("Stories per category:")
category_counts = df["category"].value_counts()
for category, count in category_counts.items():
    # Left-align category name in a 16-char field so the numbers line up
    print(f"  {category:<16} {count}")
