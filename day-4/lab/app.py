import os

from flask import Flask, jsonify
import psycopg


app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "appdb")
DB_USER = os.getenv("DB_USER", "appuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "apppassword")


def database_url():
    return (
        f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
        f"user={DB_USER} password={DB_PASSWORD} connect_timeout=2"
    )


def database_check():
    with psycopg.connect(database_url()) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS health_checks (
                    id SERIAL PRIMARY KEY,
                    checked_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
            cursor.execute("INSERT INTO health_checks DEFAULT VALUES")
            cursor.execute("SELECT 1")
            cursor.fetchone()
        connection.commit()


def database_status():
    try:
        database_check()
        return jsonify(status="ok", database="ok"), 200
    except Exception as error:
        app.logger.exception("Database health check failed")
        return (
            jsonify(status="error", database="unavailable", error=str(error)),
            500,
        )


@app.get("/")
def index():
    try:
        database_check()
        return (
            jsonify(
                application="flask-health-probes",
                status="running",
                database_connected=True,
            ),
            200,
        )
    except Exception as error:
        app.logger.exception("Database check failed")
        return (
            jsonify(
                application="flask-health-probes",
                status="error",
                database_connected=False,
                database_error=str(error),
            ),
            500,
        )


@app.get("/healthz")
def health():
    return database_status()


@app.get("/readyz")
def ready():
    response, status_code = database_status()
    if status_code != 200:
        return response, 503
    return response, status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
