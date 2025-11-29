"""
scoring.py

Provides compute_score() and analyze_tasks_list() to produce a numerical score for
each task based on:
- urgency (due date, overdue, due soon)
- importance weight
- bonus for fast tasks
- penalties for unmet dependencies
The scoring values and weights are documented here and used by the views.
"""

from datetime import date, timedelta
from typing import List, Dict, Any

# Configuration: weights and thresholds (tweakable)
IMPORTANCE_WEIGHT = 3.0      # multiplier for importance (importance assumed 1..10)
URGENCY_OVERDUE_BONUS = 50.0
URGENCY_DUE_SOON_BONUS = 20.0
DUE_SOON_DAYS = 3            # due within N days considered "due soon"
FAST_TASK_HOURS_THRESHOLD = 1
FAST_TASK_BONUS = 5.0
DEPENDENCY_PENALTY = 15.0    # penalty if dependencies are not completed
MAX_SCORE_BASE = 100.0

def _parse_date(value):
    # Accepts ISO 'YYYY-MM-DD' or a date object; returns a date or None
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except Exception:
        return None

def compute_score(task: Dict[str, Any], all_tasks: List[Dict[str, Any]]) -> float:
    """
    Compute a score for a single task dict.
    Expected fields in task:
      - title (str)
      - due_date (str YYYY-MM-DD or None)
      - importance (int)
      - estimated_hours (int)
      - dependencies (list of titles) - optional
      - done (bool) - optional (if True, we give near-zero score)
    The function returns a float score (higher == higher priority).
    """
    title = task.get('title', '<untitled>')
    done = bool(task.get('done', False))
    if done:
        # Completed tasks should have minimal priority
        return 0.0

    # Defaults and safe parsing
    importance = _safe_int(task.get('importance'), 1)
    importance = max(0, importance)
    estimated = _safe_int(task.get('estimated_hours'), 1)
    estimated = max(0, estimated)
    due_date = _parse_date(task.get('due_date'))

    score = 0.0

    # Base from importance
    score += importance * IMPORTANCE_WEIGHT

    # Urgency calculation
    today = date.today()
    if due_date:
        if due_date < today:
            # overdue => big bonus
            score += URGENCY_OVERDUE_BONUS
        else:
            days_left = (due_date - today).days
            if days_left <= DUE_SOON_DAYS:
                score += URGENCY_DUE_SOON_BONUS
            # small additional urgency as due date approaches:
            # linear decay: closer date => slightly higher score
            if days_left >= 0:
                # inverse relation
                score += max(0, (DUE_SOON_DAYS - days_left) * 2.0)

    # Bonus for small tasks (fast wins)
    if estimated <= FAST_TASK_HOURS_THRESHOLD:
        score += FAST_TASK_BONUS
    else:
        # slight penalty for very large tasks
        score -= min(estimated * 0.5, 10.0)

    # Dependencies: if there are unmet dependencies, penalize.
    deps = task.get('dependencies') or []
    if isinstance(deps, dict):
        # if dependencies provided as mapping, convert to list of values
        try:
            deps = list(deps.values())
        except Exception:
            deps = []
    # Determine if dependency tasks exist in all_tasks and are marked done.
    unmet_dependencies = 0
    dep_titles = []
    for dep in deps:
        dep_title = str(dep)
        dep_titles.append(dep_title)
        # find matching task in all_tasks (by title)
        matches = [t for t in all_tasks if str(t.get('title')).strip().lower() == dep_title.strip().lower()]
        if not matches:
            # If dependency isn't present in the provided list, treat as unmet (external dependency)
            unmet_dependencies += 1
        else:
            # if any match is not done, it's unmet
            if not any(bool(m.get('done', False)) for m in matches):
                unmet_dependencies += 1

    if unmet_dependencies > 0:
        # reduce score proportional to number of unmet dependencies
        score -= DEPENDENCY_PENALTY * unmet_dependencies

    # Ensure score is not negative
    if score < 0:
        score = 0.0

    # Cap score at a reasonable upper bound (not strictly necessary)
    return float(round(score, 3))

def _safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default

def analyze_tasks_list(tasks: List[Dict[str, Any]]):
    """
    Given a list of task dicts, compute scores for each and return a new list
    sorted by score descending, and with score included.
    """
    # Defensive copy and normalize
    all_tasks = [dict(t) for t in tasks]
    for t in all_tasks:
        # normalize fields
        if 'dependencies' not in t or t.get('dependencies') is None:
            t['dependencies'] = []
        if 'importance' not in t or t.get('importance') is None:
            t['importance'] = 1
        if 'estimated_hours' not in t or t.get('estimated_hours') is None:
            t['estimated_hours'] = 1

    scored = []
    for t in all_tasks:
        score = compute_score(t, all_tasks)
        t_copy = dict(t)
        t_copy['score'] = score
        scored.append(t_copy)

    # Sort by score descending, then by importance desc, then earliest due date
    def sort_key(x):
        # handle due_date safely
        d = _parse_date(x.get('due_date'))
        due_ts = d.toordinal() if d else float('inf')
        return (-x.get('score', 0.0), -int(x.get('importance', 0)), due_ts)

    scored.sort(key=sort_key)
    return scored
