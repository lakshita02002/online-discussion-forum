"""
Posts blueprint — CRUD for threads and comments.

GET  /                    – Paginated post list
GET  /post/<id>           – Post detail + comments
GET  /post/new            – Create form
POST /post/new            – Submit new post
GET  /post/<id>/edit      – Edit form (author only)
POST /post/<id>/edit      – Save edits
POST /post/<id>/delete    – Delete post (author only)
POST /post/<id>/comment   – Add a comment
POST /comment/<id>/delete – Delete a comment (author only)
"""

from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, abort, current_app
)
from .models import Post, Comment
from .database import query_db

posts_bp = Blueprint("posts", __name__)


def login_required(f):
    """Redirect unauthenticated users to login, carrying the intended URL as ?next=."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to perform that action.", "error")
            return redirect(url_for("auth.login", next=request.url))
        return f(*args, **kwargs)

    return decorated


def _validate_post(title: str, content: str):
    errors = []
    if not title or len(title.strip()) < 5:
        errors.append("Title must be at least 5 characters.")
    if len(title) > 200:
        errors.append("Title must be 200 characters or fewer.")
    if not content or len(content.strip()) < 10:
        errors.append("Post body must be at least 10 characters.")
    return errors


@posts_bp.route("/")
def index():
    page      = max(1, request.args.get("page", 1, type=int))
    per_page  = current_app.config.get("POSTS_PER_PAGE", 10)
    offset    = (page - 1) * per_page
    total     = Post.count()
    posts     = Post.get_all(limit=per_page, offset=offset)
    has_next  = (offset + per_page) < total
    has_prev  = page > 1
    return render_template(
        "index.html",
        posts=posts, page=page,
        has_next=has_next, has_prev=has_prev,
        total=total,
    )


@posts_bp.route("/post/<int:post_id>")
def detail(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        abort(404)
    comments = Comment.get_for_post(post_id)
    return render_template("posts/detail.html", post=post, comments=comments)


@posts_bp.route("/post/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title   = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        errors  = _validate_post(title, content)

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("posts/create.html", title=title, content=content)

        post_id = Post.create(title, content, session["user_id"])
        flash("Post published successfully!", "success")
        return redirect(url_for("posts.detail", post_id=post_id))

    return render_template("posts/create.html")


@posts_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        abort(404)
    if post["author_id"] != session["user_id"]:
        abort(403)

    if request.method == "POST":
        title   = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        errors  = _validate_post(title, content)

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("posts/edit.html", post=post, title=title, content=content)

        Post.update(post_id, title, content)
        flash("Post updated.", "success")
        return redirect(url_for("posts.detail", post_id=post_id))

    return render_template("posts/edit.html", post=post)


@posts_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        abort(404)
    if post["author_id"] != session["user_id"]:
        abort(403)
    Post.delete(post_id)
    flash("Post deleted.", "info")
    return redirect(url_for("posts.index"))


@posts_bp.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.get_by_id(post_id)
    if post is None:
        abort(404)
    content = request.form.get("content", "").strip()
    if not content or len(content) < 2:
        flash("Comment must be at least 2 characters.", "error")
    else:
        Comment.create(content, session["user_id"], post_id)
        flash("Comment added.", "success")
    return redirect(url_for("posts.detail", post_id=post_id))


@posts_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    row = query_db("SELECT * FROM comments WHERE id = ?", (comment_id,), one=True)
    if row is None:
        abort(404)
    if row["author_id"] != session["user_id"]:
        abort(403)
    post_id = row["post_id"]
    Comment.delete(comment_id)
    flash("Comment removed.", "info")
    return redirect(url_for("posts.detail", post_id=post_id))


@posts_bp.app_errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@posts_bp.app_errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403

