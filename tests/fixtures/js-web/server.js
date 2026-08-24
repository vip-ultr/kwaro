// Seeded Node fixture for the Phase B taint eval.
// VULN 1: req.query.name -> res.innerHTML-style write (document.write)
// VULN 2: req.params.code -> eval
// CLEAN: req.query.id -> parseInt -> element.textContent (no sink match)

const express = require("express");
const app = express();

app.get("/greet", (req, res) => {
  const name = req.query.name;
  document.write("<h1>" + name + "</h1>"); // VULN 1: tainted DOM write
});

app.get("/eval", (req, res) => {
  const code = req.params.code;
  eval(code); // VULN 2: tainted code execution
});

app.get("/safe", (req, res) => {
  const id = parseInt(req.query.id, 10);
  console.log(id); // CLEAN: parseInt sanitizer, no dangerous sink
});
