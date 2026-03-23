from fastapi import FastAPI
import psycopg2
import os
from prometheus_client import Counter, generate_latest
from fastapi.responses import Response

app = FastAPI()

REQUEST_COUNT = Counter('app_requests_total', 'Total requests')

DB_HOST = os.getenv("DB_HOST", "localhost")

def get_connection():
    return psycopg2.connect(
        dbname="tasks",
        user="postgres",
        password="postgres",
        host=DB_HOST
    )

@app.get("/")
def read_root():
    REQUEST_COUNT.inc()
    return {"message": "Hello DevOps!"}

@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks;")
    rows = cur.fetchall()
    return rows

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")