from supabase import create_client, Client
from flask import current_app

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Return the shared Supabase client (service role), created once per process.

    The service role key bypasses RLS — access control is enforced in
    Flask route handlers via session["user_id"] checks instead.
    """
    global _supabase_client
    if _supabase_client is None:
        url = current_app.config["SUPABASE_URL"]
        key = current_app.config["SUPABASE_SERVICE_KEY"]
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in the environment."
            )
        _supabase_client = create_client(url, key)
    return _supabase_client

