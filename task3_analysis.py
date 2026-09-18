"""
TrendPulse — Task 3: Analysis with Pandas & NumPy
Loads the cleaned CSV from Task 2, explores it, computes statistics
using NumPy, adds two derived columns, and saves the result for Task 4.

Pipeline: Task 1 (fetch) → Task 2 (clean CSV) → Task 3 (this) → Task 4 (visualise)
"""

import pandas as pd
import numpy as np
import os

# ─── Configuration ────────────────────────────────────────────────────────────

INPUT_CSV  = os.path.join("data", "trends_clean.csv")
OUTPUT_CSV = os.path.join("data", "trends_analysed.csv")

# ─── Step 1: Load and Explore ─────────────────────────────────────────────────

# Load the cleaned CSV produced by Task 2
df = pd.read_csv(INPUT_CSV)

# Shape tells us (rows, columns) at a glance
print(f"Loaded data: {df.shape}")
print()

# First 5 rows give a quick sanity check that columns look right
print("First 5 rows:")
print(df.head())
print()

# Basic averages across the whole dataset using Pandas mean()
avg_score    = df["score"].mean()
avg_comments = df["num_comments"].mean()

# Format with commas for readability (matching expected output style)
print(f"Average score   : {avg_score:,.0f}")
print(f"Average comments: {avg_comments:,.0f}")
print()

# ─── Step 2: NumPy Statistics ─────────────────────────────────────────────────

# Pull score column as a NumPy array so we can use np.* functions directly
scores = df["score"].to_numpy()

print("--- NumPy Stats ---")

# Mean, median, std — the three core descriptive stats
mean_score   = np.mean(scores)
median_score = np.median(scores)
std_score    = np.std(scores)      # population std (NumPy default)

print(f"Mean score   : {mean_score:,.0f}")
print(f"Median score : {median_score:,.0f}")
print(f"Std deviation: {std_score:,.0f}")

# np.max / np.min find the extremes of the distribution
max_score = np.max(scores)
min_score = np.min(scores)

print(f"Max score    : {max_score:,}")
print(f"Min score    : {min_score:,}")
print()

# Which category appears most often? value_counts() sorts descending by default.
category_counts = df["category"].value_counts()
top_category    = category_counts.index[0]       # first entry = most frequent
top_count       = category_counts.iloc[0]

print(f"Most stories in: {top_category} ({top_count} stories)")
print()

# Story with the highest num_comments — idxmax() returns its row index
most_commented_idx   = df["num_comments"].idxmax()
most_commented_row   = df.loc[most_commented_idx]

print(f'Most commented story: "{most_commented_row["title"]}"'
      f'  — {most_commented_row["num_comments"]:,} comments')
print()

# ─── Step 3: Add New Columns ──────────────────────────────────────────────────

# engagement: comments per upvote — +1 avoids division-by-zero on score=0 edge case
# A higher value means the story sparked a lot of discussion relative to its score
df["engagement"] = df["num_comments"] / (df["score"] + 1)

# Round to 4 decimal places to keep the CSV readable
df["engagement"] = df["engagement"].round(4)

# is_popular: True if a story's score beats the dataset average
# avg_score was computed above using Pandas — consistent with the load/explore step
df["is_popular"] = df["score"] > avg_score

# ─── Step 4: Save the Result ──────────────────────────────────────────────────

# Ensure data/ folder exists (should already, but defensive is good)
os.makedirs("data", exist_ok=True)

# Save without the Pandas row index — keeps the CSV clean for Task 4
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"Saved to {OUTPUT_CSV}")
