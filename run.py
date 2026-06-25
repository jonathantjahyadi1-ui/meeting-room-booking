from dotenv import load_dotenv
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH, override=True)

print("FILE ENV YANG DIBACA:", ENV_PATH)
print("DATABASE_URL DARI ENV:", os.environ.get("DATABASE_URL"))

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)