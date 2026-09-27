import os
import re
import json
import uuid
import time
from collections import defaultdict
from functools import wraps
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import joblib
import numpy as np

# Load environment variables from .env
load_dotenv()

# Determine environment (production on Cloud Run or when explicitly set)
IS_PRODUCTION = bool(
    os.getenv("K_SERVICE") or 
    os.getenv("ENVIRONMENT", "").lower() == "production" or 
    os.getenv("FLASK_ENV", "").lower() == "production"
)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["DEBUG"] = False if IS_PRODUCTION else (os.getenv("DEBUG", "true").lower() in ("true", "1"))

# Rate Limiting: Gentle in-memory sliding-window per IP
RATE_LIMIT_STORE = defaultdict(list)
RATE_LIMIT_BREAKDOWN = int(os.getenv("RATE_LIMIT_BREAKDOWN", 10))
RATE_LIMIT_SMALLER = int(os.getenv("RATE_LIMIT_SMALLER", 15))


def get_client_ip() -> str:
    """Returns the client's real IP address, handling proxies and Cloud Run headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "127.0.0.1"


def rate_limit(requests_per_minute: int = 10):
    """
    Gentle sliding-window rate limiter per client IP.
    Protects public Gemini API quotas from abuse without heavy external dependencies.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = get_client_ip()
            now = time.time()
            window = 60.0  # 1-minute window

            # Clean timestamps older than window
            timestamps = [t for t in RATE_LIMIT_STORE[ip] if now - t < window]
            RATE_LIMIT_STORE[ip] = timestamps

            if len(timestamps) >= requests_per_minute:
                retry_after = int(window - (now - timestamps[0])) + 1
                return jsonify({
                    "error": f"Taking a gentle pause: Rate limit reached ({requests_per_minute} requests/minute). Please wait {retry_after} seconds before trying again.",
                    "retry_after_seconds": max(1, retry_after)
                }), 429

            RATE_LIMIT_STORE[ip].append(now)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Load ML Models with graceful fallback
LOCATION_MODEL_PATH = os.path.join("models", "location_model.joblib")
TIME_MODEL_PATH = os.path.join("models", "time_model.joblib")

loc_model = None
time_model = None

try:
    if os.path.exists(LOCATION_MODEL_PATH) and os.path.exists(TIME_MODEL_PATH):
        loc_model = joblib.load(LOCATION_MODEL_PATH)
        time_model = joblib.load(TIME_MODEL_PATH)
        print("🌿 OneThing ML Models (Location & Time-of-Day) successfully loaded.")
    else:
        print("⚠️ OneThing ML Models not found in models/. Will use natural Gemini ordering as fallback.")
except Exception as e:
    print(f"⚠️ Warning loading ML models: {e}. Falling back to Gemini ordering.")
    loc_model = None
    time_model = None


TIME_BUCKET_ORDER = ["morning", "afternoon", "evening", "night"]

# Realistic college student fallback tasks for demo or offline resilience
DEFAULT_STUDENT_TASKS = [
    {
        "id": "task_psych",
        "title": "Review chapter 4 definitions for psychology quiz",
        "description": "Only look at the first 5 flashcards. Small consistent touches beat frantic cramming.",
        "estimated_minutes": 15,
        "default_time_hint": "morning",
        "default_location_hint": "work",
        "action": {
            "type": "calendar",
            "title": "Psychology Quiz Review"
        }
    },
    {
        "id": "task_bio",
        "title": "Open biology lab spreadsheet and complete just problem 1",
        "description": "You don't need to finish the full report today. Entering data for one row breaks the freeze.",
        "estimated_minutes": 15,
        "default_time_hint": "afternoon",
        "default_location_hint": "work",
        "action": None
    },
    {
        "id": "task_prof",
        "title": "Draft a 2-sentence email to Prof. Davis requesting an extension",
        "description": "Keep it polite and brief. Professors get these every week and appreciate early notices.",
        "estimated_minutes": 5,
        "default_time_hint": "afternoon",
        "default_location_hint": "work",
        "action": {
            "type": "email",
            "subject": "Question regarding assignment extension - Prof. Davis",
            "body": "Dear Professor Davis,\n\nI hope your week is going well. I am working on the assignment and wanted to ask if a brief 24-hour extension might be possible. Thank you so much for your time and understanding.\n\nBest regards,\n[Your Name]"
        }
    },
    {
        "id": "task_rx",
        "title": "Pick up allergy prescription at the campus pharmacy",
        "description": "It takes 4 minutes on your walk back from class, and you will feel so relieved.",
        "estimated_minutes": 10,
        "default_time_hint": "afternoon",
        "default_location_hint": "public",
        "action": {
            "type": "maps",
            "query": "campus pharmacy"
        }
    },
    {
        "id": "task_laundry",
        "title": "Toss just 1 load of clothes from the floor into the laundry hamper",
        "description": "Ignore folding for now. Just clear the floor path to give your eyes some breathing room.",
        "estimated_minutes": 8,
        "default_time_hint": "evening",
        "default_location_hint": "home",
        "action": None
    },
    {
        "id": "task_mom",
        "title": "Send a warm quick text to Mom",
        "description": "A 10-second 'Thinking of you, crazy week but calling Sunday!' lifts that heavy guilt instantly.",
        "estimated_minutes": 5,
        "default_time_hint": "evening",
        "default_location_hint": "home",
        "action": None
    },
    {
        "id": "task_sleep",
        "title": "Put phone across the room and read 5 pages in bed",
        "description": "Close all open browser tabs in your brain. Tomorrow is a brand new clean slate.",
        "estimated_minutes": 10,
        "default_time_hint": "night",
        "default_location_hint": "home",
        "is_rest_suggestion": True,
        "action": None
    }
]


def hour_to_bucket(hour: int) -> str:
    """
    Converts 24-hour integer (0-23) to time bucket:
    - 5 to 11 -> morning
    - 12 to 16 -> afternoon
    - 17 to 21 -> evening
    - 22 to 23 or 0 to 4 -> night
    """
    hour = int(hour) % 24
    if 5 <= hour <= 11:
        return "morning"
    elif 12 <= hour <= 16:
        return "afternoon"
    elif 17 <= hour <= 21:
        return "evening"
    else:
        return "night"


def calculate_time_fit_score(predicted_time: str, current_bucket: str, confidence: float) -> float:
    """
    Computes a contextual fit score:
    - Exact match gets highest base score (3.0) + confidence boost
    - Adjacent buckets (distance 1) get base score (2.0)
    - Distant buckets (distance 2) get base score (1.0)
    """
    if predicted_time not in TIME_BUCKET_ORDER or current_bucket not in TIME_BUCKET_ORDER:
        return 1.0

    idx_pred = TIME_BUCKET_ORDER.index(predicted_time)
    idx_curr = TIME_BUCKET_ORDER.index(current_bucket)

    diff = abs(idx_pred - idx_curr)
    dist = min(diff, 4 - diff)

    if dist == 0:
        base = 3.0
    elif dist == 1:
        base = 2.0
    else:
        base = 1.0

    return base + (confidence * 0.5)


def format_display_location(location: str) -> str:
    """
    Maps dataset 'work' to 'Campus' for student context,
    and capitalizes 'Home' or 'Public'.
    """
    loc_clean = (location or "home").strip().lower()
    if loc_clean == "work":
        return "Campus"
    return loc_clean.capitalize()


def format_display_time_tag(time_bucket: str, current_bucket: str = "") -> str:
    """
    Generates soft, comforting pill tag text that clearly states the ideal time window
    without confusing mismatches:
    e.g. 'Best around morning', 'Best around afternoon', 'Best around evening', 'Best for late night'
    """
    mapping = {
        "morning": "Best around morning",
        "afternoon": "Best around afternoon",
        "evening": "Best around evening",
        "night": "Best for late night"
    }
    return mapping.get(time_bucket, f"Best around {time_bucket}")


def tag_and_rank_tasks(tasks, local_hour=None):
    """
    Tags tasks with ML predictions (time, location, confidences)
    and sorts them so tasks matching the current local hour come first.
    If models are missing, falls back to Gemini's natural order.
    """
    if local_hour is None:
        local_hour = datetime.now().hour
    try:
        local_hour = int(local_hour) % 24
    except (ValueError, TypeError):
        local_hour = datetime.now().hour

    current_bucket = hour_to_bucket(local_hour)

    if loc_model is not None and time_model is not None:
        for task in tasks:
            title = task.get("title", "")

            # Predict Location
            try:
                loc_pred = loc_model.predict([title])[0]
                loc_proba = float(np.max(loc_model.predict_proba([title])[0]))
            except Exception:
                loc_pred = task.get("default_location_hint", "home")
                loc_proba = 0.50

            # Predict Time
            try:
                time_pred = time_model.predict([title])[0]
                time_proba = float(np.max(time_model.predict_proba([title])[0]))
            except Exception:
                time_pred = task.get("default_time_hint", "evening")
                time_proba = 0.50

            task["predicted_location"] = loc_pred
            task["location_confidence"] = round(loc_proba, 2)
            task["display_location"] = format_display_location(loc_pred)

            task["predicted_time"] = time_pred
            task["time_confidence"] = round(time_proba, 2)

            # If task is a rest suggestion (e.g. night wind-down), label clearly
            title_lower = title.lower()
            is_rest = task.get("is_rest_suggestion", False) or (
                time_pred == "night" and any(w in title_lower for w in ["sleep", "wind down", "read before bed", "put phone", "bedtime"])
            )
            if is_rest:
                task["is_rest_suggestion"] = True
                task["display_time_tag"] = "Rest suggestion"
                task["action"] = None
            else:
                task["display_time_tag"] = format_display_time_tag(time_pred, current_bucket)

            if any(w in title_lower for w in ["sleep", "wind down", "read before bed", "put phone", "bedtime", "rest", "breathe", "walk", "stretch", "unwind"]):
                task["action"] = None

            task["fit_score"] = round(calculate_time_fit_score(time_pred, current_bucket, time_proba), 3)

        # Sort tasks: highest fit_score first
        tasks.sort(key=lambda t: t.get("fit_score", 0), reverse=True)
    else:
        # Fallback to Gemini order when ML models missing
        for task in tasks:
            loc = task.get("default_location_hint", "home")
            t_bucket = task.get("default_time_hint", "evening")
            task["predicted_location"] = loc
            task["location_confidence"] = 0.50
            task["display_location"] = format_display_location(loc)
            task["predicted_time"] = t_bucket
            task["time_confidence"] = 0.50
            title_lower = task.get("title", "").lower()
            is_rest = task.get("is_rest_suggestion", False) or (
                t_bucket == "night" and any(w in title_lower for w in ["sleep", "wind down", "read before bed", "put phone", "bedtime", "rest"])
            )
            if is_rest:
                task["is_rest_suggestion"] = True
                task["display_time_tag"] = "Rest suggestion"
                task["action"] = None
            else:
                task["display_time_tag"] = format_display_time_tag(t_bucket, current_bucket)

            if any(w in title_lower for w in ["sleep", "wind down", "read before bed", "put phone", "bedtime", "rest", "breathe", "walk", "stretch", "unwind"]):
                task["action"] = None

            task["fit_score"] = 1.0

    return tasks, current_bucket, local_hour


def get_gemini_client():
    """Initializes and returns the Google Gen AI client."""
    if not GEMINI_API_KEY or GEMINI_API_KEY in ("your_api_key_here", "your_gemini_api_key_here"):
        raise ValueError(
            "GEMINI_API_KEY is not configured or is using a placeholder. "
            "Please update your .env file with a valid Gemini API key from Google AI Studio."
        )
    from google import genai
    return genai.Client(api_key=GEMINI_API_KEY)


def extract_json_safely(raw_text: str):
    """
    Strips markdown code fences (```json ... ```) and safely parses JSON.
    Handles trailing commas or common formatting quirks gracefully.
    """
    cleaned = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        cleaned = match.group(1).strip()
    return json.loads(cleaned)


@app.route("/")
def index():
    """Serves the OneThing calm single-page application."""
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint to verify server, Gemini, and ML model configuration."""
    has_key = bool(GEMINI_API_KEY and GEMINI_API_KEY not in ("your_api_key_here", "your_gemini_api_key_here"))
    models_ready = bool(loc_model is not None and time_model is not None)
    return jsonify({
        "status": "healthy",
        "gemini_api_key_configured": has_key,
        "default_model": GEMINI_MODEL,
        "ml_models_loaded": models_ready,
        "models": {
            "location_model": bool(loc_model is not None),
            "time_model": bool(time_model is not None)
        }
    })


@app.route("/api/breakdown", methods=["POST"])
@rate_limit(requests_per_minute=RATE_LIMIT_BREAKDOWN)
def api_breakdown():
    """
    POST /api/breakdown
    Takes raw brain dump text and user's local hour.
    Returns a JSON list of micro-tasks tagged with ML predicted time/place
    and ranked so tasks that fit right now come first.
    """
    # Extract requested hour (supports local_hour or hour in body or query param)
    data = request.get_json(force=True, silent=True) or {}
    brain_dump = data.get("text", "").strip() or data.get("dump", "").strip()
    demo_mode = data.get("demo", False)

    local_hour = data.get("local_hour")
    if local_hour is None:
        local_hour = data.get("hour")
    if local_hour is None:
        local_hour = request.args.get("hour")
    if local_hour is not None:
        try:
            local_hour = int(local_hour) % 24
        except (ValueError, TypeError):
            local_hour = None

    if not brain_dump and not demo_mode:
        return jsonify({
            "error": "Please provide your thoughts in the 'text' or 'dump' field."
        }), 400

    # Demo mode fallback for rapid offline presentations
    if demo_mode or GEMINI_API_KEY in ("your_api_key_here", "your_gemini_api_key_here", ""):
        ranked_tasks, active_bucket, hour_used = tag_and_rank_tasks(DEFAULT_STUDENT_TASKS.copy(), local_hour)
        return jsonify({
            "tasks": ranked_tasks,
            "count": len(ranked_tasks),
            "current_time_bucket": active_bucket,
            "local_hour_used": hour_used,
            "ml_models_applied": bool(loc_model is not None and time_model is not None),
            "demo_notice": "Showing realistic student demo tasks sorted by ML."
        })

    # Call Gemini API with offline resilience
    try:
        from google.genai import types
        client = get_gemini_client()

        system_instruction = (
            "You are OneThing, an anti-anxiety, supportive companion for overwhelmed college students "
            "struggling with cognitive overload, executive dysfunction, and ADHD paralysis.\n"
            "Your mission: Transform a messy brain dump of racing thoughts, assignments, and errands into "
            "a calm, structured list of small, concrete, approachable micro-tasks.\n"
            "Guidelines:\n"
            "- Each task should be doable in 5 to 25 minutes.\n"
            "- Reframe daunting projects into their gentle initial footstep (e.g. instead of 'Study for exam', "
            "  use 'Review lecture 4 summary slides').\n"
            "- Use a warm, calming, non-judgmental tone. Never use alarmist or guilt-inducing words.\n"
            "- Include reassuring microcopy in 'description' explaining why this step is light and doable.\n"
            "- For each task, estimate 'estimated_minutes' (5-25), 'default_time_hint' ('morning'|'afternoon'|'evening'|'night'), "
            "  and 'default_location_hint' ('home'|'work'|'public').\n"
            "- Optional Action Shortcut: If and only if a task clearly benefits from an immediate digital action shortcut, "
            "  include an 'action' field with one of three types:\n"
            "    1. 'email' -> {\"type\": \"email\", \"subject\": \"polite subject line\", \"body\": \"short, polite draft body\"} "
            "       (for emailing professors, advisors, group members, or services)\n"
            "    2. 'maps' -> {\"type\": \"maps\", \"query\": \"physical search destination (e.g. campus pharmacy, library)\"}\n"
            "    3. 'calendar' -> {\"type\": \"calendar\", \"title\": \"calendar event title (e.g. Psychology Quiz Review)\"}\n"
            "  * Most tasks should have NO action ('action': null or omitted).\n"
            "  * NEVER add an action to rest suggestions, wind-down tasks, or tasks about stepping away from screens.\n"
            "- Return STRICT JSON matching this format:\n"
            "[\n"
            "  {\n"
            "    \"title\": \"Draft 2-sentence email to Prof. Davis\",\n"
            "    \"description\": \"Asking early is responsible and respectful.\",\n"
            "    \"estimated_minutes\": 5,\n"
            "    \"default_time_hint\": \"afternoon\",\n"
            "    \"default_location_hint\": \"work\",\n"
            "    \"action\": {\n"
            "      \"type\": \"email\",\n"
            "      \"subject\": \"Extension Request - Prof. Davis\",\n"
            "      \"body\": \"Dear Professor Davis,\\n\\nI hope your week is going well...\"\n"
            "    }\n"
            "  },\n"
            "  {\n"
            "    \"title\": \"Put phone across the room and read 5 pages in bed\",\n"
            "    \"description\": \"Tomorrow is a brand new clean slate.\",\n"
            "    \"estimated_minutes\": 10,\n"
            "    \"default_time_hint\": \"night\",\n"
            "    \"default_location_hint\": \"home\",\n"
            "    \"action\": null\n"
            "  }\n"
            "]"
        )

        prompt = f"Here is the student's messy brain dump. Please unpack it gently into small, concrete tasks:\n\n{brain_dump}"

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.3
            )
        )

        parsed_tasks = extract_json_safely(response.text)

        # Standardize array
        if isinstance(parsed_tasks, dict):
            for key in ["tasks", "items", "data", "todo"]:
                if key in parsed_tasks and isinstance(parsed_tasks[key], list):
                    parsed_tasks = parsed_tasks[key]
                    break
            else:
                parsed_tasks = [parsed_tasks]

        if not isinstance(parsed_tasks, list):
            raise ValueError("Expected a JSON array of tasks from model output.")

        formatted_tasks = []
        for i, item in enumerate(parsed_tasks):
            if not isinstance(item, dict):
                continue
            title = item.get("title") or item.get("task") or "Gentle step"
            desc = item.get("description") or item.get("microcopy") or "Take it one step at a time."
            mins = item.get("estimated_minutes") or item.get("duration") or 15
            try:
                mins = max(5, min(30, int(mins)))
            except (ValueError, TypeError):
                mins = 15

            # Optional Action Shortcut parsing & safety checks
            raw_action = item.get("action")
            action = None
            if isinstance(raw_action, dict):
                act_type = str(raw_action.get("type", "")).strip().lower()
                if act_type == "email":
                    action = {
                        "type": "email",
                        "subject": str(raw_action.get("subject", "Hello")).strip(),
                        "body": str(raw_action.get("body", "")).strip()
                    }
                elif act_type == "maps":
                    action = {
                        "type": "maps",
                        "query": str(raw_action.get("query", title)).strip()
                    }
                elif act_type == "calendar":
                    action = {
                        "type": "calendar",
                        "title": str(raw_action.get("title", title)).strip()
                    }

            # Never add action to rest suggestions or tasks about stepping away from screens
            title_lower = title.lower()
            if any(w in title_lower for w in ["sleep", "wind down", "read before bed", "put phone", "bedtime", "rest", "breathe", "walk", "stretch", "unwind", "nap"]):
                action = None

            formatted_tasks.append({
                "id": str(uuid.uuid4())[:8],
                "title": title,
                "description": desc,
                "estimated_minutes": mins,
                "default_time_hint": item.get("default_time_hint", "evening"),
                "default_location_hint": item.get("default_location_hint", "home"),
                "action": action
            })

        # If late night and user has no rest-related micro-task, offer a gentle rest suggestion
        if hour_to_bucket(local_hour) == "night":
            has_rest = any(
                t.get("is_rest_suggestion", False) or
                any(w in t.get("title", "").lower() for w in ["sleep", "wind down", "read before bed", "put phone", "bedtime", "rest"])
                for t in formatted_tasks
            )
            if not has_rest and len(formatted_tasks) > 0:
                formatted_tasks.append({
                    "id": str(uuid.uuid4())[:8],
                    "title": "Put phone across the room and read 5 pages in bed",
                    "description": "Close all open browser tabs in your brain. Tomorrow is a brand new clean slate.",
                    "estimated_minutes": 10,
                    "default_time_hint": "night",
                    "default_location_hint": "home",
                    "is_rest_suggestion": True,
                    "action": None
                })

        # Apply ML Tagging and Contextual Hour Ranking
        ranked_tasks, active_bucket, hour_used = tag_and_rank_tasks(formatted_tasks, local_hour)

        return jsonify({
            "tasks": ranked_tasks,
            "count": len(ranked_tasks),
            "current_time_bucket": active_bucket,
            "local_hour_used": hour_used,
            "ml_models_applied": bool(loc_model is not None and time_model is not None)
        })

    except Exception as e:
        # Fallback to local demo tasks if network or Gemini is slow/down
        print(f"⚠️ Notice: Gemini API encounter ({e}). Gracefully falling back to pre-parsed student tasks.")
        ranked_tasks, active_bucket, hour_used = tag_and_rank_tasks(DEFAULT_STUDENT_TASKS.copy(), local_hour)
        return jsonify({
            "tasks": ranked_tasks,
            "count": len(ranked_tasks),
            "current_time_bucket": active_bucket,
            "local_hour_used": hour_used,
            "ml_models_applied": bool(loc_model is not None and time_model is not None),
            "fallback_notice": "Offline companion active: Gemini is resting, so our trained ML models sorted these tasks."
        })


@app.route("/api/smaller", methods=["POST"])
@rate_limit(requests_per_minute=RATE_LIMIT_SMALLER)
def api_smaller():
    """
    POST /api/smaller
    Breaks a single overwhelming task into 2-3 microscopic steps requiring
    minimal executive function.
    """
    data = request.get_json(force=True, silent=True) or {}
    task_title = data.get("task", "").strip() or data.get("title", "").strip()
    demo_mode = data.get("demo", False)

    fallback_steps = [
        {
            "step": 1,
            "title": f"Open workspace and title a blank page for {task_title[:32]}",
            "subtitle": "Takes 20 seconds · Zero brain power needed",
            "tag": "Do this first"
        },
        {
            "step": 2,
            "title": "Paste the prompt or write 1 messy sentence",
            "subtitle": "Just copy & paste · Spelling doesn't count",
            "tag": ""
        },
        {
            "step": 3,
            "title": "Set a gentle 5-minute timer and stop whenever it rings",
            "subtitle": "No pressure to finish · Any step breaks the freeze",
            "tag": ""
        }
    ]

    if not task_title and not demo_mode:
        return jsonify({
            "error": "Please provide a task to make smaller in the 'task' or 'title' field."
        }), 400

    if demo_mode or GEMINI_API_KEY in ("your_api_key_here", "your_gemini_api_key_here", ""):
        return jsonify({
            "original_task": task_title or "Write opening sentence for Sociology reflection",
            "encouragement": "No problem at all! Let's slice this into even tinier pieces. Which of these feels easiest right now?",
            "steps": fallback_steps
        })

    try:
        from google.genai import types
        client = get_gemini_client()

        system_instruction = (
            "You are OneThing, an anti-anxiety companion for overwhelmed college students. "
            "A student feels frozen or overwhelmed by a task ('Too much? Make it smaller').\n"
            "Your mission: Deconstruct this single task into 2 or 3 micro-steps that require "
            "almost zero cognitive friction to start.\n"
            "Guidelines:\n"
            "- Step 1 should be ridiculously easy (e.g. 'Open laptop and title blank doc', 'Pick 3 shirts from floor').\n"
            "- Give step 1 the tag 'Do this first'.\n"
            "- Provide a comforting subtitle for each step (e.g. 'Takes 30 seconds · No brain power needed', "
            "  'Just copy & paste', 'Spelling doesn't count').\n"
            "- Include an encouraging companion message in 'encouragement'.\n"
            "- Return STRICT JSON matching this format:\n"
            "{\n"
            "  \"original_task\": \"task name\",\n"
            "  \"encouragement\": \"No problem at all! Let's slice this into even tinier pieces. Which of these feels easiest right now?\",\n"
            "  \"steps\": [\n"
            "    {\n"
            "      \"step\": 1,\n"
            "      \"title\": \"Open laptop and title a blank doc\",\n"
            "      \"subtitle\": \"Takes 30 seconds · No brain power needed\",\n"
            "      \"tag\": \"Do this first\"\n"
            "    },\n"
            "    {\n"
            "      \"step\": 2,\n"
            "      \"title\": \"Paste the prompt at the top\",\n"
            "      \"subtitle\": \"Just copy & paste\",\n"
            "      \"tag\": \"\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )

        prompt = f"Break this overwhelming task down into 2-3 microscopic steps:\n\n{task_title}"

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.3
            )
        )

        parsed_data = extract_json_safely(response.text)

        if not isinstance(parsed_data, dict):
            raise ValueError("Expected JSON object from Gemini response.")

        steps = parsed_data.get("steps", [])
        if not isinstance(steps, list) or len(steps) == 0:
            raise ValueError("No steps found in the breakdown response.")

        return jsonify({
            "original_task": parsed_data.get("original_task", task_title),
            "encouragement": parsed_data.get(
                "encouragement",
                "No problem at all! Let's slice this into even tinier pieces. Which of these feels easiest right now?"
            ),
            "steps": steps
        })

    except Exception as e:
        print(f"⚠️ Notice: Smaller endpoint fallback ({e}).")
        return jsonify({
            "original_task": task_title or "Write opening sentence for Sociology reflection",
            "encouragement": "No problem at all! Let's slice this into even tinier pieces. Which of these feels easiest right now?",
            "steps": fallback_steps
        })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    debug = False if IS_PRODUCTION else (os.getenv("DEBUG", "true").lower() in ("true", "1"))
    print(f"🌿 OneThing backend running at http://127.0.0.1:{port} (production={IS_PRODUCTION}, debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
