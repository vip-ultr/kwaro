"""Seeded Python web app fixture for the Phase B taint eval.

Vulnerable flows (each must be FOUND):
  1. request.args.get -> cursor.execute          (SQL injection)
  2. os.environ["CMD"] -> subprocess.run         (shell injection)
  3. req.body name -> eval                       (code injection)

Clean flow (must NOT be flagged):
  4. request.args id -> int() -> execute (parameterized)  - sanitized
"""
from flask import Flask, request
import os
import subprocess

app = Flask(__name__)


@app.route("/user")
def get_user():
    uid = request.args.get("id")
    cur.execute("SELECT * FROM users WHERE id = '" + uid + "'")  # VULN 1
    return cur.fetchone()


@app.route("/run")
def run_job():
    cmd = os.environ["CMD"]
    subprocess.run(cmd, shell=True)  # VULN 2
    return "ok"


@app.route("/calc")
def calc():
    expr = request.form.get("expr", "")
    result = eval(expr)  # VULN 3
    return str(result)


@app.route("/safe")
def safe_lookup():
    uid = int(request.args.get("id", "0"))
    cur.execute("SELECT * FROM users WHERE id = ?", (uid,))  # CLEAN: int() + placeholder
    return cur.fetchone()
