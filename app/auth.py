"""
Authentication blueprint — backed by Supabase Auth.

GET  /register  – Show registration form
POST /register  – Create account via Supabase Auth + insert profile row
GET  /login     – Show login form
POST /login     – Sign in via Supabase Auth; store user in Flask session
POST /logout    – Sign out from Supabase Auth + clear Flask session
"""

import re
from urllib.parse import urlparse, urljoin
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash
)
from .database import get_supabase

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_safe_url(target: str) -> bool:
    ref  = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc


def _validate_registration(username: str, email: str, password: str, confirm: str):
    errors = []
    if not username:
        errors.append("Username is required.")
    elif len(username) < 3:
        errors.append("Username must be at least 3 characters.")
    elif len(username) > 30:
        errors.append("Username must be 30 characters or fewer.")
    elif not re.match(r"^[A-Za-z0-9_]+$", username):
        errors.append("Username may only contain letters, digits, and underscores.")
    if not email or not EMAIL_RE.match(email):
        errors.append("Please enter a valid email address.")
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    elif password != confirm:
        errors.append("Passwords do not match.")
    return errors


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("posts.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        errors = _validate_registration(username, email, password, confirm)

        if not errors:
            sb = get_supabase()
            existing = (
                sb.table("profiles")
                .select("id")
                .ilike("username", username)
                .limit(1)
                .execute()
            )
            if existing.data:
                errors.append("Username is already taken.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("auth/register.html", username=username, email=email)

        try:
            sb = get_supabase()
            result = sb.auth.sign_up({"email": email, "password": password})
            user = result.user
            if user is None:
                raise ValueError("Sign-up failed — no user returned.")

            sb.table("profiles").insert(
                {"id": user.id, "username": username, "bio": ""}
            ).execute()

            session.clear()
            session["user_id"]  = user.id
            session["username"] = username
            flash("Welcome to the forum, {}! 🎉".format(username), "success")
            return redirect(url_for("posts.index"))

        except Exception as exc:
            flash("Registration failed: {}".format(str(exc)), "error")
            return render_template("auth/register.html", username=username, email=email)

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("posts.index"))

    if request.method == "POST":
        email    = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        next_url = request.form.get("next", "").strip()

        if not email or not password:
            flash("Please enter your email address and password.", "error")
            return render_template("auth/login.html", identifier=email, next=next_url)

        try:
            sb = get_supabase()
            result = sb.auth.sign_in_with_password({"email": email, "password": password})
            user = result.user

            profile = sb.table("profiles").select("username").eq("id", user.id).maybe_single().execute()
            username = profile.data.get("username", email) if profile.data else email

            session.clear()
            session["user_id"]  = user.id
            session["username"] = username
            flash("Welcome back, {}!".format(username), "success")

            if next_url and _is_safe_url(next_url):
                return redirect(next_url)
            return redirect(url_for("posts.index"))

        except Exception:
            flash("Invalid credentials. Please try again.", "error")
            return render_template("auth/login.html", identifier=email, next=next_url)

    next_url = request.args.get("next", "")
    return render_template("auth/login.html", next=next_url)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    username = session.get("username", "")
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    session.clear()
    flash("You've been logged out. See you soon, {}!".format(username), "info")
    return redirect(url_for("posts.index"))

