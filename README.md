# Nexus Forum – Online Discussion Forum

A clean, modular **Online Discussion Forum** built with **Python (Flask)**, **Supabase (PostgreSQL + Auth)**, **HTML5**, and **CSS3**.

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Tech Stack](#tech-stack)
3. [Feature Overview](#feature-overview)
4. [Architecture & Data Flow](#architecture--data-flow)
5. [Database Schema](#database-schema)
6. [Environment Setup](#environment-setup)
7. [Running the Application](#running-the-application)
8. [Route Reference](#route-reference)
9. [Code Quality Notes](#code-quality-notes)

---

## Project Structure

```
OnlineDiscussionForum/
├── app/
│   ├── __init__.py        # App factory (create_app), Jinja2 filters
│   ├── auth.py            # Blueprint: registration, login, logout (Supabase Auth)
│   ├── posts.py           # Blueprint: CRUD for posts + comments
│   ├── database.py        # Supabase client singleton (get_supabase)
│   ├── models.py          # Data-access layer (User, Post, Comment)
│   ├── static/
│   │   ├── css/style.css  # Full responsive stylesheet (CSS custom props)
│   │   └── js/main.js     # Progressive-enhancement JS
│   └── templates/
│       ├── base.html          # Shared layout (nav, flash, footer)
│       ├── index.html         # Home feed with pagination
│       ├── auth/
│       │   ├── login.html
│       │   └── register.html
│       ├── posts/
│       │   ├── create.html
│       │   ├── detail.html    # Post + comments + reply form
│       │   └── edit.html      # Edit + danger-zone delete
│       └── errors/
│           ├── 403.html
│           └── 404.html
├── config.py              # DevelopmentConfig / TestingConfig / ProductionConfig
├── supabase_schema.sql    # PostgreSQL DDL to run in Supabase Dashboard
├── run.py                 # Entry point  →  python run.py
└── README.md
```

---

## Tech Stack

| Layer      | Technology                                      |
|------------|-------------------------------------------------|
| Backend    | Python 3.9+, Flask 3.x                          |
| Database   | Supabase (PostgreSQL)                            |
| Templating | Jinja2 (bundled with Flask)                      |
| Frontend   | HTML5, CSS3 (Custom Properties, Flexbox, Grid)   |
| Auth       | Supabase Auth (email/password, JWT)              |
| Fonts      | Inter via Google Fonts                           |

---

## Feature Overview

| Feature                          | Details                                                   |
|----------------------------------|-----------------------------------------------------------|
| **User Registration**            | Username (unique, 3–30 chars), email, password (≥8 chars) |
| **User Login / Logout**          | Supabase Auth; login with email; Flask session            |
| **Create Post**                  | Title (5–200 chars) + body (≥10 chars); author-locked     |
| **Read / Browse Posts**          | Paginated home feed; full detail view with metadata       |
| **Update Post**                  | Edit title & body (author only); `updated_at` tracked     |
| **Delete Post**                  | Cascades to all comments (author only)                    |
| **Add Comment**                  | Any logged-in user can reply to any post                  |
| **Delete Comment**               | Author of each comment can remove their own               |
| **Input Validation**             | Server-side on all forms; friendly flash error messages   |
| **Error Pages**                  | Custom 403 & 404 pages                                    |
| **Responsive UI**                | Mobile hamburger nav; fluid grid; works on all viewports  |

---

## Architecture & Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT  (Browser)                        │
│   HTML5 + CSS3 UI  ◄──── Jinja2 Rendered Templates         │
│   JS enhancements (main.js – progressive enhancement)       │
└─────────────┬───────────────────────────────────┬───────────┘
              │  HTTP Request (GET / POST)         │  HTML Response
              ▼                                   │
┌─────────────────────────────────────────────────┘
│              FLASK APPLICATION SERVER                       │
│                                                             │
│  run.py  ──►  create_app()  ──►  config.py                 │
│                    │                                        │
│         ┌──────────┴───────────┐                           │
│         ▼                      ▼                           │
│    auth Blueprint         posts Blueprint                   │
│  /auth/register          /          (index)                 │
│  /auth/login             /post/new  (create)                │
│  /auth/logout            /post/<id> (detail)                │
│         │                /post/<id>/edit                    │
│         │                /post/<id>/delete                  │
│         │                /post/<id>/comment                 │
│         └──────────┬───────────┘                           │
│                    ▼                                        │
│             models.py  (User · Post · Comment)              │
│                    │                                        │
│                    ▼                                        │
│             database.py (get_supabase)                      │
│                    │                                        │
└────────────────────┼────────────────────────────────────────┘
                     │  Supabase REST API (service role)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Supabase  (PostgreSQL)                           │
│                                                             │
│  ┌──────────┐   FK author_id   ┌──────────┐               │
│  │ profiles │ ────────────────► │  posts   │               │
│  │ (UUID)   │                   │ (UUID)   │               │
│  │ username │   FK author_id   │ title    │               │
│  │ bio      │ ──────────┐      │ content  │               │
│  └──────────┘            │      │ author_id│               │
│                           │      └────┬─────┘               │
│  ┌──────────┐             │          │ FK post_id           │
│  │auth.users│             ▼          ▼                      │
│  │(Supabase │        ┌──────────────────┐                  │
│  │  Auth)   │        │    comments      │                  │
│  └──────────┘        │ id · content     │                  │
│       ▲               │ author_id        │                  │
│       │ FK id         │ post_id          │                  │
│  profiles.id ─────►  └──────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### Request Lifecycle (example: POST /post/new)

1. User fills the "New Post" form and clicks **Publish**.
2. Browser sends `POST /post/new` with form data.
3. `posts.py → create()` runs server-side validation (`_validate_post`).
4. On success, `Post.create()` (models.py) calls `get_supabase().table("posts").insert(...)`.
5. Supabase inserts the row into PostgreSQL and returns the new UUID.
6. Flask redirects to `GET /post/<new_id>`.
7. `posts.py → detail()` calls `Post.get_by_id()` + `Comment.get_for_post()`.
8. Jinja2 renders `posts/detail.html` extending `base.html`.
9. HTML response is sent to the browser.

---

## Database Schema

The schema lives in `supabase_schema.sql` — run it once in the Supabase Dashboard → SQL Editor.

```sql
-- profiles: extends Supabase auth.users with a display name and bio
CREATE TABLE profiles (
    id          UUID        PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username    TEXT        NOT NULL UNIQUE,
    bio         TEXT        NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE posts (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT        NOT NULL,
    content     TEXT        NOT NULL,
    author_id   UUID        NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE comments (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    content     TEXT        NOT NULL,
    author_id   UUID        NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    post_id     UUID        NOT NULL REFERENCES posts(id)    ON DELETE CASCADE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

Indexes on `posts(author_id)`, `comments(post_id)`, `comments(author_id)` keep joins fast.
A `BEFORE UPDATE` trigger on `posts` keeps `updated_at` current automatically.
Row Level Security (RLS) is enabled on all tables as a defence-in-depth layer.

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

---

## Code Quality Notes

- **Modular blueprints** – auth and posts are fully independent; adding new blueprints (e.g., `search`, `profile`) requires zero changes to existing code.
- **Supabase data layer** – all DB access goes through `supabase-py`; queries are explicit and easy to follow in `models.py`.
- **Server-side validation** – every form field is validated before any DB write; errors surface as flash messages with category styling.
- **Password security** – handled entirely by Supabase Auth; plaintext passwords are never stored or seen by the application.
- **CSRF basics** – all state-changing routes require `POST`; session cookies are `HttpOnly` by default in Flask.
- **Cascade deletes** – `ON DELETE CASCADE` ensures referential integrity at the DB level; deleting a user removes their posts and comments automatically.
