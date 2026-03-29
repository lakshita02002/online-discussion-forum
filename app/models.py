"""Data-access layer — thin model helpers that keep SQL out of route functions."""

from .database import query_db, execute_db
from werkzeug.security import generate_password_hash, check_password_hash


class User:
    @staticmethod
    def create(username: str, email: str, password: str) -> int:
        """Insert a new user and return the new id.

        Uses pbkdf2:sha256 explicitly — Werkzeug 3.x defaults to scrypt, which
        requires OpenSSL scrypt support absent in some Python builds (e.g. macOS
        system Python). pbkdf2:sha256 is equally secure and universally available.
        """
        pw_hash = generate_password_hash(password, method="pbkdf2:sha256")
        return execute_db(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username.strip(), email.strip().lower(), pw_hash),
        )

    @staticmethod
    def get_by_id(user_id: int):
        return query_db("SELECT * FROM users WHERE id = ?", (user_id,), one=True)

    @staticmethod
    def get_by_username(username: str):
        return query_db(
            "SELECT * FROM users WHERE username = ?", (username.strip(),), one=True
        )

    @staticmethod
    def get_by_email(email: str):
        return query_db(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),), one=True
        )

    @staticmethod
    def verify_password(user_row, password: str) -> bool:
        return check_password_hash(user_row["password_hash"], password)

    @staticmethod
    def update_bio(user_id: int, bio: str):
        execute_db("UPDATE users SET bio = ? WHERE id = ?", (bio.strip(), user_id))


class Post:
    @staticmethod
    def create(title: str, content: str, author_id: int) -> int:
        return execute_db(
            "INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
            (title.strip(), content.strip(), author_id),
        )

    @staticmethod
    def get_all(limit: int = 50, offset: int = 0):
        """Return posts newest-first, joined with author username and comment count.

        The comment_count column lets the home feed display activity indicators
        without a second round-trip to the database.
        """
        return query_db(
            """
            SELECT p.*,
                   u.username AS author_name,
                   (SELECT COUNT(*) FROM comments WHERE post_id = p.id) AS comment_count
            FROM   posts p
            JOIN   users u ON u.id = p.author_id
            ORDER  BY p.created_at DESC
            LIMIT  ? OFFSET ?
            """,
            (limit, offset),
        )

    @staticmethod
    def get_by_id(post_id: int):
        return query_db(
            """
            SELECT p.*, u.username AS author_name
            FROM   posts p
            JOIN   users u ON u.id = p.author_id
            WHERE  p.id = ?
            """,
            (post_id,),
            one=True,
        )

    @staticmethod
    def update(post_id: int, title: str, content: str):
        execute_db(
            "UPDATE posts SET title = ?, content = ? WHERE id = ?",
            (title.strip(), content.strip(), post_id),
        )

    @staticmethod
    def delete(post_id: int):
        execute_db("DELETE FROM posts WHERE id = ?", (post_id,))

    @staticmethod
    def count() -> int:
        row = query_db("SELECT COUNT(*) AS n FROM posts", one=True)
        return row["n"] if row else 0


class Comment:

    @staticmethod
    def create(content: str, author_id: int, post_id: int) -> int:
        return execute_db(
            "INSERT INTO comments (content, author_id, post_id) VALUES (?, ?, ?)",
            (content.strip(), author_id, post_id),
        )

    @staticmethod
    def get_for_post(post_id: int):
        return query_db(
            """
            SELECT c.*, u.username AS author_name
            FROM   comments c
            JOIN   users u ON u.id = c.author_id
            WHERE  c.post_id = ?
            ORDER  BY c.created_at ASC
            """,
            (post_id,),
        )

    @staticmethod
    def delete(comment_id: int):
        execute_db("DELETE FROM comments WHERE id = ?", (comment_id,))

