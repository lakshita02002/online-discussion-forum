# Nexus Forum – Online Discussion Forum

A clean, modular **Online Discussion Forum** built with **Python (Flask)**, **SQLite**, **HTML5**, and **CSS3**.


---

## Environment Setup

### Prerequisites

- Python **3.9 or newer**
- `pip` (bundled with Python)

### 1 – Clone / navigate to the project

```bash
cd OnlineDiscussionForum
```

### 2 – Create & activate a virtual environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3 – Install dependencies

```bash
pip install flask werkzeug
```

> **Note:** `sqlite3` and `markupsafe` ship with Python/Flask – no extra install needed.

### 4 – (Optional) Set environment variables

```bash
# Use a strong random secret in any non-development environment
export SECRET_KEY="replace-with-a-long-random-string"
export FLASK_ENV="development"   # or production
```

---

## Running the Application

### Option A – Direct Python

```bash
python run.py
```

### Option B – Flask CLI

```bash
flask --app run run --debug
```

The database (`instance/forum.db`) is **created and migrated automatically** the first time the app starts.
To reset it manually:

```bash
flask --app run init-db
```

Then open **http://localhost:5000** in your browser.
