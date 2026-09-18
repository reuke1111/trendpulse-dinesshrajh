"""
TrendPulse — Task 1: Data Collection
Fetches trending stories from the HackerNews API and groups them
into 5 categories based on keyword matching in story titles.

Pipeline: Task 1 (this) → Task 2 (clean CSV) → Task 3 (NumPy/Pandas) → Task 4 (Visualise)
"""

import requests
import json
import os
import time
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────

# HackerNews Firebase API endpoints
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL        = "https://hacker-news.firebaseio.com/v0/item/{id}.json"

# Identify our client in requests — good practice, required by the spec
HEADERS = {"User-Agent": "TrendPulse/1.0"}

# How many story IDs to pull from the top-stories list
MAX_IDS = 500

# Max stories to collect per category before moving on
MAX_PER_CATEGORY = 25

# Seconds to pause between finishing one category and starting the next
SLEEP_BETWEEN_CATEGORIES = 2

# Keywords that map a story title → category (checked case-insensitively)
CATEGORY_KEYWORDS = {
    "technology":    ["AI", "software", "tech", "code", "computer", "data", "cloud", "API", "GPU", "LLM"],
    "worldnews":     ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":        ["NFL", "NBA", "FIFA", "sport", "game", "team", "player", "league", "championship"],
    "science":       ["research", "study", "space", "physics", "biology", "discovery", "NASA", "genome"],
    "entertainment": ["movie", "film", "music", "Netflix", "game", "book", "show", "award", "streaming"],
}

# Output folder and filename (date-stamped so runs don't overwrite each other)
OUTPUT_DIR  = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"trends_{datetime.now().strftime('%Y%m%d')}.json")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def assign_category(title: str) -> str | None:
    """
    Check the story title against each category's keyword list.
    Returns the first matching category name, or None if nothing matches.
    Comparison is case-insensitive so 'AI', 'ai', 'Ai' all hit 'technology'.
    """
    title_lower = title.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in title_lower:
                return category
    return None   # story doesn't fit any category — we'll skip it


def fetch_top_story_ids() -> list[int]:
    """
    Step 1: Hit the top-stories endpoint and return the first MAX_IDS IDs.
    Returns an empty list if the request fails, so the rest of the script
    can still run (just with nothing to process).
    """
    try:
        response = requests.get(TOP_STORIES_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()          # raises HTTPError on 4xx/5xx
        ids = response.json()
        print(f"Fetched {len(ids)} story IDs. Using first {MAX_IDS}.")
        return ids[:MAX_IDS]
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch top story IDs: {e}")
        return []


def fetch_story(story_id: int) -> dict | None:
    """
    Step 2: Fetch a single story by its ID.
    Returns the parsed JSON dict, or None on any network/HTTP error.
    """
    try:
        url = ITEM_URL.format(id=story_id)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Don't crash — just warn and skip this story
        print(f"  [WARN] Could not fetch story {story_id}: {e}")
        return None


def extract_fields(raw: dict, category: str) -> dict:
    """
    Pull only the 7 required fields out of the raw HackerNews item dict.
    'descendants' (comment count) may be absent on stories with 0 comments,
    so we default to 0. Same for 'score' and 'by' just to be safe.
    """
    return {
        "post_id":       raw.get("id"),
        "title":         raw.get("title", ""),
        "category":      category,
        "score":         raw.get("score", 0),
        "num_comments":  raw.get("descendants", 0),   # 'descendants' = comment count
        "author":        raw.get("by", "unknown"),
        "collected_at":  datetime.now().isoformat(),   # ISO-8601 timestamp added by us
    }


# ─── Main pipeline ────────────────────────────────────────────────────────────

def main():
    # Grab the pool of story IDs we'll work through
    all_ids = fetch_top_story_ids()
    if not all_ids:
        print("No story IDs retrieved. Exiting.")
        return

    # Pre-fetch every story detail in one pass so we only hit the API once per ID.
    # This is more efficient than looping per-category and re-fetching shared stories.
    print(f"\nFetching details for up to {len(all_ids)} stories …")
    raw_stories = []
    for story_id in all_ids:
        story = fetch_story(story_id)
        if story and story.get("type") == "story" and story.get("title"):
            raw_stories.append(story)

    print(f"Retrieved {len(raw_stories)} valid story objects.\n")

    # Now assign categories and collect up to MAX_PER_CATEGORY per bucket.
    # The sleep(2) fires once per category, as specified.
    collected: list[dict] = []
    category_counts: dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for idx, category in enumerate(CATEGORY_KEYWORDS.keys()):
        print(f"[{category.upper()}] Categorising stories …")

        for raw in raw_stories:
            if category_counts[category] >= MAX_PER_CATEGORY:
                break   # bucket is full — move on

            assigned = assign_category(raw.get("title", ""))
            if assigned == category:
                collected.append(extract_fields(raw, category))
                category_counts[category] += 1

        print(f"  → {category_counts[category]} stories collected for '{category}'")

        # Pause between categories (not between individual fetches — we pre-fetched)
        if idx < len(CATEGORY_KEYWORDS) - 1:   # no sleep after the last category
            print(f"  Sleeping {SLEEP_BETWEEN_CATEGORIES}s before next category …")
            time.sleep(SLEEP_BETWEEN_CATEGORIES)

    # ─── Save to JSON ─────────────────────────────────────────────────────────

    # Create the output folder if it doesn't exist yet
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(collected, f, indent=2, ensure_ascii=False)

    total = len(collected)
    print(f"\nCollected {total} stories. Saved to {OUTPUT_FILE}")

    # Friendly summary per category
    print("\nBreakdown:")
    for cat, count in category_counts.items():
        print(f"  {cat:<15} {count} stories")


if __name__ == "__main__":
    main()
