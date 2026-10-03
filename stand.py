#imports
import uvicorn
import sqlite3

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

DB_NAME = "lab.db"
app = FastAPI(title="Corporate Portal V2")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "secret")
        )

    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
async def root():
    return {"message": "Welcome! Log in only for authorized personnel"}

@app.get("/admin_login", response_class=HTMLResponse)
async def admin_login_form():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Admin Login</title>
    </head>
    <body>
        <h1>Admin Panel Corporate Admin</h1>

        <form action="/admin_login" method="post">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required>

            <br><br>

            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required>

            <br><br>

            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """


@app.get("/.env", response_class=PlainTextResponse)
async def get_env():
    return """DB_ENGINE=postgresql
    DB_USER=postgres
    DB_PASS=super_secret_dev_pass_2026
    DB_HOST=127.0.0.1"""

@app.get("/.git/config", response_class=PlainTextResponse)
async def get_git_config():
    return """[core]
    repositoryformatversion = 0
    filemode = true
    [remote "origin"]
    url = git@github.com:SecretCorp/backend-api.git"""

if __name__ == "__main__":
    print("[*] Launching vulnerable standalone on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")