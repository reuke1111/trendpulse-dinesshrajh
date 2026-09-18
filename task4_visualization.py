"""
TrendPulse — Task 4: Visualizations
Loads the analysed CSV from Task 3 and produces 3 charts plus
a combined dashboard, saving everything as PNG files.

Pipeline: Task 1 → Task 2 → Task 3 → Task 4 (this, final step)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ─── Step 1: Setup ────────────────────────────────────────────────────────────

INPUT_CSV  = os.path.join("data", "trends_analysed.csv")
OUTPUT_DIR = "outputs"

# Create outputs/ folder if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the analysed CSV from Task 3
df = pd.read_csv(INPUT_CSV)

# is_popular was saved as True/False strings in CSV — ensure it's boolean
df["is_popular"] = df["is_popular"].astype(bool)

print(f"Loaded {len(df)} rows from {INPUT_CSV}")
print(f"Saving charts to '{OUTPUT_DIR}/'")
print()

# One colour per category — used in Chart 2 and the dashboard
CATEGORY_COLOURS = {
    "technology":    "#4C9BE8",
    "worldnews":     "#E8784C",
    "sports":        "#4CE87A",
    "science":       "#C44CE8",
    "entertainment": "#E8D44C",
}

# ─── Helper ───────────────────────────────────────────────────────────────────

def shorten(title: str, max_len: int = 50) -> str:
    """Trim a story title to max_len characters and append '…' if truncated."""
    return title if len(title) <= max_len else title[:max_len].rstrip() + "…"


# ─── Chart 1: Top 10 Stories by Score ────────────────────────────────────────

# Sort descending, take top 10, then reverse so highest score is at the top
top10 = df.nlargest(10, "score").iloc[::-1].reset_index(drop=True)

# Shorten long titles so they fit on the y-axis without overlapping
top10["short_title"] = top10["title"].apply(shorten)

fig1, ax1 = plt.subplots(figsize=(10, 6))

# Horizontal bar chart — barh() takes y=labels, width=values
bars = ax1.barh(top10["short_title"], top10["score"], color="#4C9BE8", edgecolor="white")

# Add the score value just to the right of each bar for quick reading
for bar, score in zip(bars, top10["score"]):
    ax1.text(bar.get_width() + 50, bar.get_y() + bar.get_height() / 2,
             f"{score:,}", va="center", fontsize=8)

ax1.set_title("Top 10 Stories by Score", fontsize=14, fontweight="bold", pad=12)
ax1.set_xlabel("Score (upvotes)")
ax1.set_ylabel("Story Title")
ax1.spines["top"].set_visible(False)      # cleaner look — remove top spine
ax1.spines["right"].set_visible(False)

plt.tight_layout()

# savefig BEFORE show — otherwise show() clears the figure first
chart1_path = os.path.join(OUTPUT_DIR, "chart1_top_stories.png")
plt.savefig(chart1_path, dpi=150, bbox_inches="tight")
plt.close(fig1)   # close to free memory before next chart
print(f"Saved {chart1_path}")


# ─── Chart 2: Stories per Category ───────────────────────────────────────────

# Count how many stories belong to each category
cat_counts = df["category"].value_counts()

# Map each category name to its colour; default grey for any unexpected category
colours = [CATEGORY_COLOURS.get(cat, "#AAAAAA") for cat in cat_counts.index]

fig2, ax2 = plt.subplots(figsize=(8, 5))

bars2 = ax2.bar(cat_counts.index, cat_counts.values, color=colours, edgecolor="white", width=0.6)

# Label each bar with its count above the bar
for bar, count in zip(bars2, cat_counts.values):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
             str(count), ha="center", va="bottom", fontsize=10, fontweight="bold")

ax2.set_title("Stories per Category", fontsize=14, fontweight="bold", pad=12)
ax2.set_xlabel("Category")
ax2.set_ylabel("Number of Stories")
ax2.set_ylim(0, cat_counts.max() + 3)    # a little headroom above the tallest bar
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

plt.tight_layout()

chart2_path = os.path.join(OUTPUT_DIR, "chart2_categories.png")
plt.savefig(chart2_path, dpi=150, bbox_inches="tight")
plt.close(fig2)
print(f"Saved {chart2_path}")


# ─── Chart 3: Score vs Comments (Scatter) ────────────────────────────────────

# Split the DataFrame into popular and non-popular groups for two-colour scatter
popular     = df[df["is_popular"] == True]
not_popular = df[df["is_popular"] == False]

fig3, ax3 = plt.subplots(figsize=(8, 6))

# Plot non-popular first (bottom layer) so popular dots appear on top
ax3.scatter(not_popular["score"], not_popular["num_comments"],
            color="#AAAAAA", alpha=0.6, s=50, label="Not Popular")

ax3.scatter(popular["score"], popular["num_comments"],
            color="#E8784C", alpha=0.8, s=70, label="Popular (above avg score)")

ax3.set_title("Score vs Number of Comments", fontsize=14, fontweight="bold", pad=12)
ax3.set_xlabel("Score (upvotes)")
ax3.set_ylabel("Number of Comments")
ax3.legend(loc="upper left")
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)

plt.tight_layout()

chart3_path = os.path.join(OUTPUT_DIR, "chart3_scatter.png")
plt.savefig(chart3_path, dpi=150, bbox_inches="tight")
plt.close(fig3)
print(f"Saved {chart3_path}")


# ─── Bonus: Dashboard (all 3 charts in one figure) ────────────────────────────

# 1 row × 3 columns layout; wider figure to give each panel breathing room
fig_dash, (d1, d2, d3) = plt.subplots(1, 3, figsize=(20, 6))

# ── Panel 1: Top 10 horizontal bar ──
d1.barh(top10["short_title"], top10["score"], color="#4C9BE8", edgecolor="white")
d1.set_title("Top 10 by Score", fontsize=11, fontweight="bold")
d1.set_xlabel("Score")
d1.spines["top"].set_visible(False)
d1.spines["right"].set_visible(False)
# Tighten font size for the cramped panel width
d1.tick_params(axis="y", labelsize=7)

# ── Panel 2: Category bar chart ──
d2.bar(cat_counts.index, cat_counts.values, color=colours, edgecolor="white", width=0.6)
d2.set_title("Stories per Category", fontsize=11, fontweight="bold")
d2.set_xlabel("Category")
d2.set_ylabel("Count")
d2.tick_params(axis="x", labelsize=8, rotation=15)
d2.spines["top"].set_visible(False)
d2.spines["right"].set_visible(False)

# ── Panel 3: Scatter plot ──
d3.scatter(not_popular["score"], not_popular["num_comments"],
           color="#AAAAAA", alpha=0.6, s=30, label="Not Popular")
d3.scatter(popular["score"], popular["num_comments"],
           color="#E8784C", alpha=0.8, s=50, label="Popular")
d3.set_title("Score vs Comments", fontsize=11, fontweight="bold")
d3.set_xlabel("Score")
d3.set_ylabel("Comments")
d3.legend(fontsize=8)
d3.spines["top"].set_visible(False)
d3.spines["right"].set_visible(False)

# Overall dashboard title sitting above all three panels
fig_dash.suptitle("TrendPulse Dashboard", fontsize=16, fontweight="bold", y=1.02)

plt.tight_layout()

dashboard_path = os.path.join(OUTPUT_DIR, "dashboard.png")
plt.savefig(dashboard_path, dpi=150, bbox_inches="tight")
plt.close(fig_dash)
print(f"Saved {dashboard_path}")

print()
print("All charts saved. Pipeline complete!")
