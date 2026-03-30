# Nexus Forum – Online Discussion Forum

A clean, modular **Online Discussion Forum** built with **Python (Flask)**, **Supabase (PostgreSQL + Auth)**, **HTML5**, and **CSS3**.

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
pip install flask werkzeug supabase
```

### 4 – Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and create a free project.
2. Open the **SQL Editor** in the Supabase Dashboard and run `supabase_schema.sql`.
3. Go to **Settings → API** and copy your project URL and **service_role** key.

### 5 – Set environment variables

```bash
export SECRET_KEY="replace-with-a-long-random-string"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_KEY="your-service-role-key"
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

Then open <http://localhost:5000> in your browser.

---

## Route Reference

| Method | URL                           | Auth required | Description                        |
|--------|-------------------------------|---------------|------------------------------------|
| GET    | `/`                           | No            | Home – paginated post list         |
| GET    | `/post/<id>`                  | No            | Post detail + comments             |
| GET    | `/post/new`                   | Yes           | New post form                      |
| POST   | `/post/new`                   | Yes           | Submit new post                    |
| GET    | `/post/<id>/edit`             | Yes (owner)   | Edit post form                     |
| POST   | `/post/<id>/edit`             | Yes (owner)   | Save post edits                    |
| POST   | `/post/<id>/delete`           | Yes (owner)   | Delete post (+ cascaded comments)  |
| POST   | `/post/<id>/comment`          | Yes           | Add a comment                      |
| POST   | `/comment/<id>/delete`        | Yes (owner)   | Delete own comment                 |
| GET    | `/auth/register`              | No            | Registration form                  |
| POST   | `/auth/register`              | No            | Create account                     |
| GET    | `/auth/login`                 | No            | Login form                         |
| POST   | `/auth/login`                 | No            | Authenticate & start session       |
| POST   | `/auth/logout`                | Yes           | Destroy session & redirect         |

