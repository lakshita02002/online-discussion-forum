"""
Authentication blueprint.

GET  /register  – Show registration form
POST /register  – Validate & create new account
GET  /login     – Show login form
POST /login     – Validate credentials & start session
POST /logout    – Destroy session & redirect home
"""

import re
from urllib.parse import urlparse, urljoin
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash
)
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_safe_url(target: str) -> bool:
    """Return True only when *target* resolves to the same host as the app.

    Prevents open-redirect attacks when using a `next` query parameter.
    """
    ref  = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc


def _validate_registration(username: str, email: str, password: str, confirm: str):
    """Return a list of error strings (empty = valid).

    Fields use cascaded elif so a blank value produces only one error, not several.
    """
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
            if User.get_by_username(username):
                errors.append("Username is already taken.")
            if User.get_by_email(email):
                errors.append("An account with that email already exists.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template(
                "auth/register.html",
                username=username, email=email
            )

        user_id = User.create(username, email, password)
        session.clear()
        session["user_id"] = user_id
        session["username"] = username
        flash("Welcome to the forum, {}! 🎉".format(username), "success")
        return redirect(url_for("posts.index"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("posts.index"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password   = request.form.get("password", "")
        next_url   = request.form.get("next", "").strip()

        if not identifier or not password:
            flash("Please enter your username/email and password.", "error")
            return render_template("auth/login.html",
                                   identifier=identifier, next=next_url)

        user = User.get_by_username(identifier) or User.get_by_email(identifier)

        if user is None or not User.verify_password(user, password):
            flash("Invalid credentials. Please try again.", "error")
            return render_template("auth/login.html",
                                   identifier=identifier, next=next_url)

        session.clear()
        session["user_id"]  = user["id"]
        session["username"] = user["username"]
        flash("Welcome back, {}!".format(user["username"]), "success")

        if next_url and _is_safe_url(next_url):
            return redirect(next_url)
        return redirect(url_for("posts.index"))

    next_url = request.args.get("next", "")
    return render_template("auth/login.html", next=next_url)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Sign the user out.

    Using POST (via a small nav form) prevents CSRF-triggered logout – a
    malicious page cannot force a GET to /auth/logout in the background.
    """
    username = session.get("username", "")
    session.clear()
    flash("You've been logged out. See you soon, {}!".format(username), "info")
    return redirect(url_for("posts.index"))

