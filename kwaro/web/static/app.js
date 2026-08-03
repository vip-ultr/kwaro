// kwaro web UI - vanilla JS, no framework (L11). Talks to the FastAPI backend.
(function () {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const activity = $("activity");
  const findingsEl = $("findings");
  const chatLog = $("chatLog");

  function logActivity(msg, kind) {
    const d = document.createElement("div");
    d.className = "line" + (kind ? " " + kind : "");
    d.textContent = msg;
    activity.appendChild(d);
    activity.scrollTop = activity.scrollHeight;
  }

  function chatLine(who, text) {
    const d = document.createElement("div");
    d.className = who === "you" ? "you" : "kwaro";
    d.textContent = (who === "you" ? "you> " : "kwaro> ") + text;
    chatLog.appendChild(d);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function renderFindings(findings) {
    findingsEl.innerHTML = "";
    if (!findings || !findings.length) {
      findingsEl.innerHTML = '<div class="empty">No findings yet. Run a scan.</div>';
      return;
    }
    let crit = 0, high = 0, med = 0, low = 0, info = 0;
    for (const f of findings) {
      const se = (f.severity || "info").toLowerCase();
      if (se === "critical") crit++; else if (se === "high") high++;
      else if (se === "medium") med++; else if (se === "low") low++; else info++;
    }
    $("counts").textContent = `(C:${crit} H:${high} M:${med} L:${low} I:${info})`;

    for (const f of findings) {
      const card = document.createElement("div");
      card.className = "card " + (f.severity || "info").toLowerCase();
      const post = typeof f.posterior === "number" ? f.posterior.toFixed(3) : "0.050";
      const comp = typeof f.compositeConfidence === "number" ? f.compositeConfidence.toFixed(3) : "-";
      card.innerHTML =
        `<div class="title">${(f.title || f.rule_id || "finding")}</div>` +
        `<div class="meta">${f.severity || ""} | ${f.cwe || ""} | ${f.rule_id || ""} ` +
        `@ ${f.file || ""}:${f.line_start || ""}</div>` +
        `<div class="math">posterior=${post} sprt=${f.sprt_decision || "none"} ` +
        `compositeConf=${comp} poc=${f.poc_state || "none"}</div>` +
        (f.snippet ? `<div class="snippet">${escapeHtml(f.snippet)}</div>` : "") +
        (f.description ? `<div class="meta">${escapeHtml(f.description)}</div>` : "");
      findingsEl.appendChild(card);
    }
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  async function doScan() {
    const target = $("target").value.trim();
    if (!target) { logActivity("enter a target first", "warn"); return; }
    const profile = $("profile").value;
    const pocs = $("pocs").checked;
    const rescan = $("rescan").checked;
    const fmt = $("fmt").value;
    const body = { target, profile, pocs, rescan, format: fmt };
    logActivity(`scan ${target} (profile=${profile})`);
    findingsEl.innerHTML = '<div class="empty">scanning...</div>';
    try {
      const resp = await fetch("/api/scan", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await resp.json();
      if (data.report) {
        logActivity("scan complete", "ok");
        renderFindings(data.findings || []);
      } else if (data.export_path) {
        logActivity(`wrote ${data.export_path}`, "ok");
        renderFindings([]);
      } else {
        logActivity(data.error || "scan failed", "warn");
      }
    } catch (e) {
      logActivity("request error: " + e.message, "warn");
    }
  }

  async function doChat() {
    const text = $("chatInput").value.trim();
    if (!text) return;
    chatLine("you", text);
    $("chatInput").value = "";
    const target = $("target").value.trim();
    try {
      const resp = await fetch("/api/chat", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target, message: text }),
      });
      const data = await resp.json();
      chatLine("kwaro", data.reply || data.error || "(no response)");
    } catch (e) {
      chatLine("kwaro", "error: " + e.message);
    }
  }

  $("scanBtn").addEventListener("click", doScan);
  $("chatBtn").addEventListener("click", doChat);
  $("chatInput").addEventListener("keydown", (e) => { if (e.key === "Enter") doChat(); });

  // initial state
  renderFindings([]);
  logActivity("ready. kwaro runs local models with zero cost by default.");
})();
