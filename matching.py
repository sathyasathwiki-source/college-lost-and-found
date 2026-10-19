"""
matching.py
===========
Automatic matching algorithm for the College Lost-and-Found system.

Compares active lost-item reports against active found-item reports to
identify possible matches. The algorithm uses keyword-based text comparison
— no machine learning or AI is involved.

Time Complexity of the matching algorithm:
  Let L = number of active lost items, F = number of active found items.
  Let W = average number of words in an item's name + description + location.

  - Outer loop: O(L)
  - Inner loop: O(F)
  - Word tokenization per item: O(W)
  - Word intersection: O(W) with set operations

  Total: O(L × F × W)

  For typical campus usage (L, F < 500; W < 50), this is fast enough
  without an index. For larger datasets, a full-text-search index (e.g.,
  SQLite FTS5) would be more appropriate.
"""

import re


# ===========================================================================
# CONSTANTS
# ===========================================================================

# Scores awarded for each matching criterion
SCORE_NAME_EXACT    = 60    # Category + name exact match
SCORE_NAME_WORD     = 30    # Shared word in item name
SCORE_CATEGORY      = 20    # Same category
SCORE_DESC_WORD     = 5     # Each shared word in description
SCORE_LOCATION_WORD = 8     # Each shared word in location

# Minimum total score required to surface a match to the user
MIN_MATCH_SCORE = 30

# Common English stop-words to exclude from keyword comparison
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
    'for', 'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were',
    'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
    'it', 'its', 'my', 'i', 'me', 'we', 'our', 'you', 'your', 'he',
    'she', 'they', 'this', 'that', 'some', 'any', 'found', 'lost',
    'item', 'near', 'inside', 'outside', 'above', 'below',
}


# ===========================================================================
# HELPER FUNCTIONS
# ===========================================================================

def _normalize(text):
    """
    Normalize text for comparison:
      1. Casefold (locale-aware lowercase).
      2. Remove punctuation.
      3. Collapse multiple spaces.

    Returns a clean lowercase string.
    """
    if not text:
        return ""
    text = text.casefold()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _keywords(text):
    """
    Tokenize text into a set of meaningful keywords.
    Removes stop-words and single-character tokens.

    Returns a set of keyword strings.
    """
    words = _normalize(text).split()
    return {w for w in words if w not in STOP_WORDS and len(w) > 1}


# ===========================================================================
# MAIN MATCHING FUNCTION
# ===========================================================================

def find_matches(lost_item, found_items):
    """
    Compare a single lost item against a list of found items.

    Parameters:
      lost_item   — dict with keys: id, name, category, description, location
      found_items — list of dicts (same keys)

    Returns:
      A list of match dicts, sorted by score descending, filtered by
      MIN_MATCH_SCORE. Each dict contains:
        - found_item  : the found-item dict
        - score       : integer relevance score
        - reasons     : list of human-readable strings explaining the match
    """
    results = []

    # Pre-compute keyword sets for the lost item
    lost_name_kw  = _keywords(lost_item.get('name', ''))
    lost_cat      = _normalize(lost_item.get('category', ''))
    lost_desc_kw  = _keywords(lost_item.get('description', ''))
    lost_loc_kw   = _keywords(lost_item.get('location', ''))
    lost_name_norm = _normalize(lost_item.get('name', ''))

    for found in found_items:
        # Skip if same item (shouldn't happen, but guard anyway)
        if found.get('id') == lost_item.get('id'):
            continue

        score = 0
        reasons = []

        found_name_norm = _normalize(found.get('name', ''))
        found_name_kw   = _keywords(found.get('name', ''))
        found_cat       = _normalize(found.get('category', ''))
        found_desc_kw   = _keywords(found.get('description', ''))
        found_loc_kw    = _keywords(found.get('location', ''))

        # ---- Criterion 1: Exact name + category match ----
        if lost_name_norm == found_name_norm and lost_cat == found_cat:
            score += SCORE_NAME_EXACT
            reasons.append(
                f"Item name and category match exactly: '{found['name']}'"
            )

        # ---- Criterion 2: Shared words in name ----
        shared_name = lost_name_kw & found_name_kw
        if shared_name and not (lost_name_norm == found_name_norm and lost_cat == found_cat):
            points = len(shared_name) * SCORE_NAME_WORD
            score += points
            reasons.append(
                f"Shared keyword(s) in name: {', '.join(sorted(shared_name))}"
            )

        # ---- Criterion 3: Same category ----
        if lost_cat and found_cat and lost_cat == found_cat:
            if not (lost_name_norm == found_name_norm):
                score += SCORE_CATEGORY
                reasons.append(f"Same category: '{found['category']}'")

        # ---- Criterion 4: Shared words in description ----
        shared_desc = lost_desc_kw & found_desc_kw
        if shared_desc:
            points = min(len(shared_desc) * SCORE_DESC_WORD, 25)
            score += points
            reasons.append(
                f"Shared keyword(s) in description: "
                f"{', '.join(sorted(shared_desc)[:5])}"
            )

        # ---- Criterion 5: Shared words in location ----
        shared_loc = lost_loc_kw & found_loc_kw
        if shared_loc:
            points = min(len(shared_loc) * SCORE_LOCATION_WORD, 16)
            score += points
            reasons.append(
                f"Found near a similar location: "
                f"{', '.join(sorted(shared_loc))}"
            )

        # Only surface if score meets threshold
        if score >= MIN_MATCH_SCORE:
            results.append({
                'found_item': found,
                'score': score,
                'reasons': reasons,
            })

    # Sort by score descending (best match first)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_all_matches(lost_items, found_items):
    """
    Run the matching algorithm across all active lost items.

    Parameters:
      lost_items  — list of active lost-item dicts
      found_items — list of active found-item dicts

    Returns:
      A list of match-group dicts:
        {
          'lost_item'  : dict,
          'matches'    : [{'found_item': dict, 'score': int, 'reasons': [...]}]
        }
      Only groups with at least one match are included.

    Time complexity: O(L × F × W)  — see module docstring.
    """
    all_matches = []

    for lost in lost_items:
        matches = find_matches(lost, found_items)
        if matches:
            all_matches.append({
                'lost_item': lost,
                'matches': matches,
            })

    return all_matches


def get_match_label(score):
    """
    Return a human-readable confidence label based on score.
    These labels are estimates — not guaranteed accuracy.
    """
    if score >= 80:
        return 'Strong possible match'
    elif score >= 50:
        return 'Moderate possible match'
    else:
        return 'Weak possible match'
