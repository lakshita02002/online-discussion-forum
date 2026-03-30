"""Data-access layer — thin model helpers backed by Supabase (PostgreSQL)."""

from .database import get_supabase


class User:
    @staticmethod
    def get_by_id(user_id: str):
        sb = get_supabase()
        res = sb.table("profiles").select("*").eq("id", user_id).maybe_single().execute()
        return res.data

    @staticmethod
    def get_by_username(username: str):
        sb = get_supabase()
        res = (
            sb.table("profiles")
            .select("*")
            .ilike("username", username.strip())
            .limit(1)
            .execute()
        )
        return res.data[0] if res.data else None

    @staticmethod
    def update_bio(user_id: str, bio: str):
        sb = get_supabase()
        sb.table("profiles").update({"bio": bio.strip()}).eq("id", user_id).execute()


class Post:
    @staticmethod
    def create(title: str, content: str, author_id: str) -> str:
        sb = get_supabase()
        res = (
            sb.table("posts")
            .insert({"title": title.strip(), "content": content.strip(), "author_id": author_id})
            .execute()
        )
        return res.data[0]["id"]

    @staticmethod
    def get_all(limit: int = 10, offset: int = 0):
        """Return posts newest-first with author username and comment count."""
        sb = get_supabase()
        res = (
            sb.table("posts")
            .select("*, profiles(username), comments(count)")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        rows = []
        for row in res.data:
            profile = row.pop("profiles", {}) or {}
            comments_agg = row.pop("comments", []) or []
            row["author_name"] = profile.get("username", "unknown")
            row["comment_count"] = int(comments_agg[0].get("count", 0)) if comments_agg else 0
            rows.append(row)
        return rows

    @staticmethod
    def get_by_id(post_id: str):
        sb = get_supabase()
        res = (
            sb.table("posts")
            .select("*, profiles(username)")
            .eq("id", post_id)
            .maybe_single()
            .execute()
        )
        if not res.data:
            return None
        row = res.data
        profile = row.pop("profiles", {}) or {}
        row["author_name"] = profile.get("username", "unknown")
        return row

    @staticmethod
    def update(post_id: str, title: str, content: str):
        sb = get_supabase()
        sb.table("posts").update(
            {"title": title.strip(), "content": content.strip()}
        ).eq("id", post_id).execute()

    @staticmethod
    def delete(post_id: str):
        sb = get_supabase()
        sb.table("posts").delete().eq("id", post_id).execute()

    @staticmethod
    def count() -> int:
        sb = get_supabase()
        res = sb.table("posts").select("id", count="exact").execute()
        return res.count or 0


class Comment:
    @staticmethod
    def create(content: str, author_id: str, post_id: str) -> str:
        sb = get_supabase()
        res = (
            sb.table("comments")
            .insert({"content": content.strip(), "author_id": author_id, "post_id": post_id})
            .execute()
        )
        return res.data[0]["id"]

    @staticmethod
    def get_for_post(post_id: str):
        sb = get_supabase()
        res = (
            sb.table("comments")
            .select("*, profiles(username)")
            .eq("post_id", post_id)
            .order("created_at", desc=False)
            .execute()
        )
        rows = []
        for row in res.data:
            profile = row.pop("profiles", {}) or {}
            row["author_name"] = profile.get("username", "unknown")
            rows.append(row)
        return rows

    @staticmethod
    def get_by_id(comment_id: str):
        sb = get_supabase()
        res = sb.table("comments").select("*").eq("id", comment_id).maybe_single().execute()
        return res.data

    @staticmethod
    def delete(comment_id: str):
        sb = get_supabase()
        sb.table("comments").delete().eq("id", comment_id).execute()

