from fastapi import FastAPI, HTTPException
import psycopg2
import os
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response

app = FastAPI()

REQUEST_COUNT = Counter('app_requests_total', 'Total requests')
TRACK_PLAY_COUNT = Counter('track_play_total', 'Track play count', ['track_id'])

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "music")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )


@app.get("/")
def root():
    REQUEST_COUNT.inc()
    return {"service": "Music API", "status": "running"}


@app.get("/tracks")
def get_tracks():
    REQUEST_COUNT.inc()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, title, artist, genre, plays FROM tracks ORDER BY plays DESC;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "artist": r[2],
            "genre": r[3],
            "plays": r[4],
        }
        for r in rows
    ]


@app.get("/search")
def search(q: str):
    REQUEST_COUNT.inc()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, artist, genre, plays
        FROM tracks
        WHERE title ILIKE %s OR artist ILIKE %s;
    """, (f"%{q}%", f"%{q}%"))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "artist": r[2],
            "genre": r[3],
            "plays": r[4],
        }
        for r in rows
    ]


@app.post("/tracks/{track_id}/play")
def play_track(track_id: int):
    REQUEST_COUNT.inc()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM tracks WHERE id = %s;", (track_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Track not found")

    cur.execute("UPDATE tracks SET plays = plays + 1 WHERE id = %s;", (track_id,))
    conn.commit()

    TRACK_PLAY_COUNT.labels(track_id=str(track_id)).inc()

    cur.close()
    conn.close()

    return {"status": "played", "track_id": track_id}


@app.get("/top")
def top_tracks(limit: int = 5):
    REQUEST_COUNT.inc()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, artist, plays
        FROM tracks
        ORDER BY plays DESC
        LIMIT %s;
    """, (limit,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "artist": r[2],
            "plays": r[3],
        }
        for r in rows
    ]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
