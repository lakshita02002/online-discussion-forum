"""Entry point. Set FLASK_ENV to control the config (defaults to 'development')."""

import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

env = os.environ.get("FLASK_ENV", "development")
app = create_app(env)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config.get("DEBUG", False))

