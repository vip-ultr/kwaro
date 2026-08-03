import os

REPO = os.path.join(os.path.dirname(__file__), "vuln-repo")


def write(path, content):
    full = os.path.join(REPO, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)


# Python: hardcoded secret + SQL concat injection + md5 hash
write("app.py", '''DB_PASSWORD = "S3cretP@ssw0rd99"

def login(user_input):
    q = "SELECT * FROM users WHERE name = " + user_input
    cursor.execute(q)

import hashlib
def weak_hash(pw):
    return hashlib.md5(pw.encode()).hexdigest()
''')

# JS: XSS via innerHTML with request input + command concat
write("static/bundle.js", '''function show(name){
  document.getElementById("out").innerHTML = "Hi " + name;
}
const cmd = "echo " + userSupplied;
''')

# Solidity-ish: reentrancy risk (caught by auth/injection rules loosely; profile gates)
write("contract.sol", '''function withdraw(uint amt) public {
    msg.sender.call.value(amt)("");
}
''')

# Go: path traversal
write("server.go", '''func serve(req *http.Request) {
    data, _ := os.ReadFile(req.URL.Query().Get("file"))
    w.Write(data)
}
''')
