import os

REPO = os.path.join(os.path.dirname(__file__), "vuln-repo")
os.makedirs(REPO, exist_ok=True)

with open(os.path.join(REPO, "app.py"), "w") as f:
    f.write('DB_PASSWORD = "S3cretP@ssw0rd99"\n')
    f.write('\n')
    f.write('def login(user_input):\n')
    f.write('    q = "SELECT * FROM users WHERE name = " + user_input\n')
    f.write('    cursor.execute(q)\n')
