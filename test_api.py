"""
Test script for OneThing API endpoints.
Runs direct tests against Flask's test client to verify:
1. Health & ML model load status
2. ML tagging (time, location, confidence, display pill tag)
3. Hour-based contextual ranking (Morning vs Night order changes)
4. Live Gemini breakdown and smaller task endpoints
"""
import sys
import json
from app import app

SAMPLE_BRAIN_DUMP = (
    "biology lab report due Friday at 5pm and I haven't opened spreadsheet yet\n"
    "need to email Prof. Davis to ask if a 24h extension is realistic\n"
    "room feels upside down, laundry is overflowing from basket\n"
    "add psychology exam review session to calendar\n"
    "pick up allergy prescription from campus pharmacy\n"
    "forgot to call mom back yesterday"
)

def test_health():
    client = app.test_client()
    res = client.get("/api/health")
    print(f"\n1. GET /api/health -> Status {res.status_code}")
    data = res.get_json()
    print(json.dumps(data, indent=2))
    assert res.status_code == 200
    assert data.get("ml_models_loaded") is True, "ML models should be loaded"

def test_hour_ranking_and_ml_tagging():
    client = app.test_client()
    
    # Test Morning (Hour 9)
    res_morning = client.post("/api/breakdown", json={"text": SAMPLE_BRAIN_DUMP, "hour": 9})
    assert res_morning.status_code == 200
    m_data = res_morning.get_json()
    morning_top = m_data["tasks"][0]
    
    # Test Night (Hour 23)
    res_night = client.post("/api/breakdown", json={"text": SAMPLE_BRAIN_DUMP, "hour": 23})
    assert res_night.status_code == 200
    n_data = res_night.get_json()
    night_top = n_data["tasks"][0]

    print("\n2. ML Tagging & Contextual Hour Ranking Verification:")
    print(f"   ► Morning (Hour 9) Top Task: '{morning_top['title']}'")
    print(f"     Tag: '{morning_top['display_time_tag']} · {morning_top['display_location']}' "
          f"(Time Conf: {morning_top['time_confidence']:.0%}, Loc Conf: {morning_top['location_confidence']:.0%})")
    
    print(f"   ► Night (Hour 23) Top Task:   '{night_top['title']}'")
    print(f"     Tag: '{night_top['display_time_tag']} · {night_top['display_location']}' "
          f"(Time Conf: {night_top['time_confidence']:.0%}, Loc Conf: {night_top['location_confidence']:.0%})")

    assert morning_top["title"] != night_top["title"], "Top task should change based on the current hour!"
    assert "predicted_time" in morning_top
    assert "predicted_location" in morning_top
    assert morning_top["display_location"] in ["Campus", "Home", "Public"]
    print("   ✅ Hour-based ranking successfully reorders tasks based on time of day!")

def test_smaller_demo():
    client = app.test_client()
    payload = {
        "task": "Write just the opening sentence for your reflection paper"
    }
    res = client.post("/api/smaller", json=payload)
    print(f"\n3. POST /api/smaller -> Status {res.status_code}")
    data = res.get_json()
    print(json.dumps(data, indent=2))
    assert res.status_code == 200
    assert "steps" in data
    assert len(data["steps"]) > 0

def test_action_shortcuts():
    client = app.test_client()
    res = client.post("/api/breakdown", json={"text": SAMPLE_BRAIN_DUMP, "hour": 14})
    assert res.status_code == 200
    tasks = res.get_json()["tasks"]
    
    print("\n4. Action Shortcuts Verification:")
    tasks_with_action = [t for t in tasks if t.get("action")]
    tasks_without_action = [t for t in tasks if not t.get("action")]
    
    # Check that most tasks have no action
    print(f"   Tasks with action: {len(tasks_with_action)} / {len(tasks)}")
    print(f"   Tasks without action: {len(tasks_without_action)} / {len(tasks)}")
    assert len(tasks_without_action) >= len(tasks_with_action), "Most tasks should have no action"
    
    # Check specific action types
    email_tasks = [t for t in tasks_with_action if t["action"]["type"] == "email"]
    maps_tasks = [t for t in tasks_with_action if t["action"]["type"] == "maps"]
    cal_tasks = [t for t in tasks_with_action if t["action"]["type"] == "calendar"]
    
    if email_tasks:
        assert "subject" in email_tasks[0]["action"] and "body" in email_tasks[0]["action"]
        print(f"   ✅ Email action: '{email_tasks[0]['title'][:40]}...' -> Subject: '{email_tasks[0]['action']['subject']}'")

    if maps_tasks:
        assert "query" in maps_tasks[0]["action"]
        print(f"   ✅ Maps action: '{maps_tasks[0]['title'][:40]}...' -> Query: '{maps_tasks[0]['action']['query']}'")

    if cal_tasks:
        assert "title" in cal_tasks[0]["action"]
        print(f"   ✅ Calendar action: '{cal_tasks[0]['title'][:40]}...' -> Title: '{cal_tasks[0]['action']['title']}'")
    
    # Check that rest suggestion has NO action
    rest_tasks = [t for t in tasks if t.get("is_rest_suggestion")]
    for rt in rest_tasks:
        assert rt.get("action") is None, f"Rest suggestion '{rt['title']}' must never have an action"
    print("   ✅ Rest suggestions confirmed to have no digital action attached.")

    # Check frontend HTML contains action container and button
    html_res = client.get("/")
    assert html_res.status_code == 200
    html = html_res.get_data(as_text=True)
    assert "focusTaskActionContainer" in html
    assert "focusTaskActionBtn" in html
    assert "✉️ Open draft" in html
    assert "📍 Directions" in html
    assert "📅 Add to calendar" in html
    print("   ✅ Front-end template properly includes subtle action shortcut button structure.")


def test_live_gemini():
    client = app.test_client()
    health_res = client.get("/api/health").get_json()
    if not health_res.get("gemini_api_key_configured"):
        print("\n[!] Note: GEMINI_API_KEY is not yet set in .env. Skipping live Gemini call.")
        return

    print("\n5. Live Gemini + ML Tagging Pipeline Test:")
    payload = {
        "text": "finish biology lab, return book at library, clean desk, sleep early",
        "hour": 14  # Afternoon
    }
    res = client.post("/api/breakdown", json=payload)
    print(f"   POST /api/breakdown -> Status {res.status_code}")
    data = res.get_json()
    tasks = data.get("tasks", [])
    print(f"   Returned {len(tasks)} ranked tasks for afternoon (hour 14):")
    for idx, t in enumerate(tasks):
        action_desc = f"Action: {t['action']['type']}" if t.get("action") else "No action"
        print(f"   [{idx+1}] {t['title']} | Tag: {t.get('display_time_tag')} · {t.get('display_location')} | {action_desc}")

def test_rate_limiting():
    client = app.test_client()
    test_ip = "192.0.2.42"
    headers = {"X-Forwarded-For": test_ip}
    
    print("\n6. Rate Limiting Verification:")
    hit_429 = False
    for i in range(15):
        res = client.post("/api/breakdown", json={}, headers=headers)
        if res.status_code == 429:
            hit_429 = True
            data = res.get_json()
            print(f"   ✅ Request {i+1} triggered 429 Too Many Requests: '{data.get('error')}'")
            break
    assert hit_429 is True, "Rate limiter should return 429 when threshold exceeded"
    print("   ✅ Rate limiting successfully protects endpoints against quota exhaustion.")


if __name__ == "__main__":
    print("=" * 65)
    print("🌿 Testing OneThing Complete Integration")
    print("=" * 65)
    test_health()
    test_hour_ranking_and_ml_tagging()
    test_smaller_demo()
    test_action_shortcuts()
    test_rate_limiting()
    test_live_gemini()
    print("\n✨ All tests passed! ML models, ranking, action shortcuts, rate limiting, and UI are fully integrated.")
