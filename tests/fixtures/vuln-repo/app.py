DB_PASSWORD = "S3cretP@ssw0rd99"

def login(user_input):
    q = "SELECT * FROM users WHERE name = " + user_input
    cursor.execute(q)

import hashlib
def weak_hash(pw):
    return hashlib.md5(pw.encode()).hexdigest()
