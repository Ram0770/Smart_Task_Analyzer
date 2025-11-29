import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .scoring import analyze_tasks_list, compute_score
from .models import Task
from datetime import datetime

@csrf_exempt
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/
    Body JSON: { "tasks": [ {title, due_date, importance, estimated_hours, dependencies, done?}, ... ], "save": false }
    Returns: { "status": "ok", "tasks": [ { ... , score }, ... ] }
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Malformed JSON."}, status=400)

    tasks = payload.get('tasks')
    if tasks is None:
        return JsonResponse({"error": "Missing 'tasks' in request body."}, status=400)
    if not isinstance(tasks, list):
        return JsonResponse({"error": "'tasks' must be a list."}, status=400)

    # Validate task items and sanitize
    sanitized = []
    errors = []
    for i, t in enumerate(tasks):
        if not isinstance(t, dict):
            errors.append(f"Task at index {i} is not an object.")
            continue
        title = t.get('title') or f'Untitled {i+1}'
        # basic validation for numeric fields
        importance = _safe_int(t.get('importance'), 1)
        estimated_hours = _safe_int(t.get('estimated_hours'), 1)
        due_date = t.get('due_date')
        # due_date validation (optional)
        if due_date:
            try:
                # Accept date string YYYY-MM-DD; if invalid, error but continue
                datetime.fromisoformat(due_date)
            except Exception:
                errors.append(f"Task '{title}': invalid due_date '{due_date}', expected YYYY-MM-DD.")
                # set to None (no due date)
                due_date = None
        dependencies = t.get('dependencies') or []
        if not isinstance(dependencies, list):
            # trying to coerce simple strings into list
            if isinstance(dependencies, str):
                dependencies = [dependencies]
            else:
                dependencies = []
        done = bool(t.get('done', False))

        sanitized.append({
            'title': title,
            'due_date': due_date,
            'importance': importance,
            'estimated_hours': estimated_hours,
            'dependencies': dependencies,
            'done': done
        })

    if errors:
        # return warnings with a 400 if errors are severe
        return JsonResponse({"error": "Validation errors", "details": errors}, status=400)

    # analyze scores
    scored = analyze_tasks_list(sanitized)

    # optional: save to DB if requested
    save_flag = bool(payload.get('save', False))
    if save_flag:
        for s in scored:
            try:
                Task.objects.create(
                    title=s.get('title', 'Untitled'),
                    due_date=s.get('due_date') or None,
                    importance=int(s.get('importance', 1)),
                    estimated_hours=int(s.get('estimated_hours', 1)),
                    dependencies=s.get('dependencies') or []
                )
            except Exception:
                # non-fatal: continue saving rest
                continue

    return JsonResponse({"status": "ok", "tasks": scored}, status=200)


@csrf_exempt
def suggest_tasks(request):
    """
    GET or POST /api/tasks/suggest/
    Returns top 3 tasks + textual explanation for why they were chosen.
    If POST with tasks similar to analyze, will use them; otherwise uses last tasks saved in DB (up to 50).
    """
    # Accept both GET and POST
    tasks_input = None
    if request.method == 'POST':
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({"error": "Malformed JSON."}, status=400)
        tasks_input = payload.get('tasks')

    # If tasks provided, validate & analyze same as analyze_tasks
    if tasks_input and isinstance(tasks_input, list):
        # reuse the analyze logic (lightweight): call analyze_tasks_list after sanitization
        sanitized = []
        for i, t in enumerate(tasks_input):
            if not isinstance(t, dict):
                continue
            title = t.get('title') or f'Untitled {i+1}'
            importance = _safe_int(t.get('importance'), 1)
            estimated_hours = _safe_int(t.get('estimated_hours'), 1)
            due_date = t.get('due_date')
            dependencies = t.get('dependencies') or []
            if not isinstance(dependencies, list):
                if isinstance(dependencies, str):
                    dependencies = [dependencies]
                else:
                    dependencies = []
            done = bool(t.get('done', False))
            sanitized.append({
                'title': title,
                'due_date': due_date,
                'importance': importance,
                'estimated_hours': estimated_hours,
                'dependencies': dependencies,
                'done': done
            })
        scored = analyze_tasks_list(sanitized)
    else:
        # Fallback: use tasks stored in DB (if any)
        qs = Task.objects.all().order_by('-created_at')[:50]
        if not qs.exists():
            return JsonResponse({"error": "No tasks provided and no stored tasks available."}, status=400)
        db_tasks = []
        for obj in qs:
            db_tasks.append({
                'title': obj.title,
                'due_date': obj.due_date.isoformat() if obj.due_date else None,
                'importance': obj.importance,
                'estimated_hours': obj.estimated_hours,
                'dependencies': obj.dependencies or [],
                'done': False
            })
        scored = analyze_tasks_list(db_tasks)

    # top 3 suggestions
    top3 = scored[:3]
    explanation = _build_explanation(top3)

    return JsonResponse({"status": "ok", "suggestions": top3, "explanation": explanation}, status=200)


def _build_explanation(top_tasks):
    """
    Build a simple textual explanation for the top tasks chosen.
    """
    reasons = []
    for t in top_tasks:
        parts = []
        title = t.get('title')
        parts.append(f"'{title}'")
        # reasons: overdue or due soon
        due_date = t.get('due_date')
        if due_date:
            try:
                d = datetime.fromisoformat(due_date).date()
                today = datetime.utcnow().date()
                if d < today:
                    parts.append("is overdue")
                elif (d - today).days <= 3:
                    parts.append(f"is due soon ({d.isoformat()})")
            except Exception:
                pass
        importance = t.get('importance', 0)
        if importance >= 7:
            parts.append("has high importance")
        estimated = t.get('estimated_hours', 0)
        if estimated <= 1:
            parts.append("quick to finish (low estimated hours)")
        deps = t.get('dependencies') or []
        if deps:
            parts.append(f"has {len(deps)} dependency(ies) to consider")
        reasons.append(", ".join(parts))
    return " | ".join(reasons)


def _safe_int(val, default=0):
    try:
        return int(val)
    except Exception:
        return default
