# 🌿 OneThing
> **Calm, Single-Task Focus for Overwhelmed College Students**  
> *Built for HackUMBC — Health & Wellness Track & Best Use of Gemini API*  
> 🔗 **Live Cloud Run URL**: [https://onething-608695314407.us-east4.run.app](https://onething-608695314407.us-east4.run.app)

---

## 💡 What is OneThing?
College students frequently experience **executive dysfunction, ADHD paralysis, and cognitive overload** when juggling assignments, emails, deadlines, and chores all at once. Traditional to-do apps worsen this anxiety by displaying exhaustive, intimidating lists with red overdue badges and ticking timers.

**OneThing** takes the opposite approach:
1. **Unburden**: The student dumps everything racing through their mind into a single input box.
2. **Deconstruct**: Google Gemini transforms the messy thoughts into small, concrete, approachable micro-tasks (5–25 minutes each) with soothing, compassionate microcopy.
3. **Contextual ML Prioritization**: Custom Machine Learning models predict the optimal **time of day** and **location** for each task, ranking the tasks so the one that fits *right now* appears first.
4. **One Thing at a Time**: The interface surfaces **only ONE task**, hiding the rest of the mountain.
5. **Too Much? Make It Smaller**: If the student still freezes up, Gemini slices the task into 2–3 microscopic physical actions (e.g., *"Step 1: Open laptop and title a blank document · Takes 20 seconds"*).
6. **Celebrate & Rest**: Completing a step triggers a gentle confetti burst and records quiet wins into an **End of Day Summary** with zero guilt.

---

## 🧠 AI & Machine Learning Architecture

```
                    ┌────────────────────────┐
                    │   Student Brain Dump   │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  Gemini 3.8 Flash API  │
                    │   (Structured JSON)    │
                    └───────────┬────────────┘
                                │ Friendly micro-tasks
                                ▼
                    ┌────────────────────────┐
                    │ Custom MS-LaTTE Models │
                    │ TF-IDF + Logistic Reg  │
                    └───────────┬────────────┘
                                │ Tags: Time, Location, Confidences
                                ▼
                    ┌────────────────────────┐
                    │  Context Hour Ranking  │
                    │ (Matches local hour)   │
                    └───────────┬────────────┘
                                │ Top single task
                                ▼
                    ┌────────────────────────┐
                    │  One Task Focus Screen │
                    │  "Right now, just this"│
                    └────────────────────────┘
```

### 1. Generative AI: Google Gemini 3.8 Flash
- Uses the official `google-genai` Python SDK with structured JSON mode (`response_mime_type="application/json"`).
- Deconstructs overwhelming projects into gentle starting footsteps with encouraging, anti-anxiety phrasing.
- Powers `/api/breakdown` (brain dump $\rightarrow$ micro-tasks) and `/api/smaller` (task $\rightarrow$ 2–3 micro-actions).

### 2. Custom ML Classifiers: MS-LaTTE Dataset
Trained on Microsoft's **MS-LaTTE** dataset (10,101 crowdsourced tasks with multi-annotator votes):
- **Data Cleaning**: Stripped `Known == 'no'`, split multi-labels, stripped weekday/weekend prefixes (`wd-`, `we-`), and consolidated time votes into 4 core buckets: `morning`, `afternoon`, `evening`, and `night`. Resolved consensus via majority voting.
- **Model Architecture**: `FeatureUnion` combining word-level TF-IDF (1–2 n-grams) and character-level TF-IDF within word boundaries (3–4 n-grams), followed by `LogisticRegression(class_weight='balanced')`.
- **Handling Class Imbalance**: In the raw dataset, `home` (68.8%) and `evening` (45.0%) dominate. Using `class_weight='balanced'` ensures minority classes like `work` (Campus) and `night` achieve high recall.

#### 📊 Performance vs. Majority Baseline (Judge Presentation Metrics)

| Model | Model Accuracy | Most-Common Baseline | Accuracy Gain | Model Macro F1 | Baseline Macro F1 |
|---|---|---|---|---|---|
| **Location Classifier** (`home`, `campus`, `public`) | **72.59%** | 68.78% (guessing *home*) | **+3.81%** | **0.660** | 0.272 |
| **Time-of-Day Classifier** (`morning`, `afternoon`, `evening`, `night`) | **48.32%** | 45.00% (guessing *evening*) | **+3.32%** | **0.398** | 0.155 |

> **Why Macro F1 Matters**: A naive baseline that always guesses "evening" achieves 45% accuracy but has a **0.00 recall** on mornings, afternoons, and nights. Our model's **Macro F1 of 0.398 vs 0.155** demonstrates real contextual intelligence that surfaces daytime campus tasks during the day and winding-down tasks at night.

---

## 🎨 Design System: Restorative Companion
Designed using Google Stitch export specifications:
- **Palette**: Soft Sage (`#4A6B5D`), Steamed Cream (`#FAF8F5`), Dusky Lavender (`#7B7295`), and Oatmeal Linen (`#F5F1EB`).
- **Typography**: `Quicksand` for rounded headers and tactile chips; `Nunito Sans` for open, relaxed readability.
- **Tone**: A supportive friend, not a rigid productivity tool. Zero countdown timers, zero red alerts, zero overdue pressure.

---

## 🚀 Quickstart & Setup

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation
```bash
# Clone the repository and enter directory
cd OneThing

# Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
PORT=5001
```

### 4. Train the ML Models
```bash
python train_model.py
```
*Trains both pipelines, prints baseline comparisons and sanity check predictions, and saves models to `models/`.*

### 5. Run the Application
```bash
python app.py
```
Open your browser to: [**http://127.0.0.1:5001/**](http://127.0.0.1:5001/)

### 6. Run Automated Verification Tests
```bash
python test_api.py
```

### 7. Test Locally with Gunicorn & Deploy to Google Cloud Run

#### Test locally with Gunicorn (matching production):
```bash
PORT=5001 gunicorn -b :$PORT app:app
```
Open [http://127.0.0.1:5001/](http://127.0.0.1:5001/) to verify.

#### Deploy to Google Cloud Run:
```bash
gcloud run deploy onething \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY="your_actual_gemini_api_key",GEMINI_MODEL="gemini-3.8-flash"
```
The `.gcloudignore` will automatically keep your `.env`, `.venv`, and `data/` private and lightweight while packaging your trained ML `models/`, `templates/`, and `static/` bundle.

---

## 🎬 How to Demo for Judges

1. **Pre-filled Stressed Dump**:
   - The Brain Dump screen comes pre-filled with authentic student racing thoughts (lab report, Prof. Davis extension, laundry pile, exam formulas).
   - Click **"Pre-fill demo"** anytime to reset.
2. **Contextual Time Ranking**:
   - In the **Time** selector next to *Quick triggers*, switch between:
     - **Morning (9 AM)**: Surfaces study and campus tasks (`Best around morning · Campus`).
     - **Night (11 PM)**: Surfaces wind-down and bedtime tasks (`Best for late night · Home`).
   - Notice how the greeting dynamically updates (`Good morning` $\leftrightarrow$ `Hey night owl`).
3. **Anti-Freeze ("Make it smaller")**:
   - Click **"Too much? Make it smaller 🪄"** to show Gemini deconstructing the task into 3 effortless micro-actions.
   - Choose Step 1 and click **"Start with Step 1 →"**.
4. **Action Shortcuts**:
   - When a task has a clear digital action (e.g. emailing a professor, picking up an errand, or scheduling a study session), a subtle circular shortcut button appears below the task text (`✉️ Open draft`, `📍 Directions`, or `📅 Add to calendar`).
   - Rest suggestions and screen-away tasks never display digital actions.
5. **Celebration & Quiet Wins**:
   - Click **"Done ✓"** to trigger the pastel confetti burst and view your growing sprout plant.
   - Click **"I want to rest for a bit"** to review your completed wins in the End of Day summary.
6. **Offline & Slow Internet Resilience**:
   - If Wi-Fi is slow or API quotas spike, OneThing automatically falls back to local pre-parsed tasks and uses the local ML models for ranking so your demo never fails on stage.

---

## 📚 Datasets & Acknowledgments
- **Dataset**: [MS-LaTTE: Microsoft Large Task dataset with Time and Location Estimates](https://www.microsoft.com/en-us/research/publication/ms-latte-a-large-scale-dataset-for-implicit-task-duration-time-and-location-estimation/), Microsoft Research.
- **Visual Design**: Google Stitch Restorative Companion specifications.
- **Celebration Effects**: `canvas-confetti` via CDN.
