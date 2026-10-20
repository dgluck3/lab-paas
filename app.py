import os
import platform
import sys
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

STARTED = datetime.now(timezone.utc)
VERSION = "3.0"

PAGE = """<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lab PaaS · Railway</title>
  <style>
    :root {
      --bg1: #0b0b1a;
      --bg2: #1a1040;
      --card: rgba(255, 255, 255, 0.06);
      --border: rgba(255, 255, 255, 0.12);
      --text: #f3f1ff;
      --muted: #a9a4cf;
      --accent: #a78bfa;
      --accent2: #5eead4;
      --ok: #4ade80;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: var(--text);
      background:
        radial-gradient(900px 500px at 15% 10%, rgba(167, 139, 250, 0.25), transparent 60%),
        radial-gradient(800px 500px at 90% 90%, rgba(94, 234, 212, 0.18), transparent 60%),
        linear-gradient(160deg, var(--bg1), var(--bg2));
      background-attachment: fixed;
    }
    .wrap { max-width: 920px; margin: 0 auto; padding: 56px 20px 72px; }
    .badge {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 6px 14px; border-radius: 999px;
      background: var(--card); border: 1px solid var(--border);
      font-size: 13px; color: var(--muted);
    }
    .dot {
      width: 8px; height: 8px; border-radius: 50%;
      background: var(--ok); box-shadow: 0 0 0 0 rgba(74, 222, 128, .7);
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      70% { box-shadow: 0 0 0 10px rgba(74, 222, 128, 0); }
      100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
    }
    h1 {
      font-size: clamp(34px, 6vw, 60px);
      line-height: 1.05; margin: 22px 0 12px; letter-spacing: -0.02em;
    }
    h1 span {
      background: linear-gradient(90deg, var(--accent), var(--accent2));
      -webkit-background-clip: text; background-clip: text; color: transparent;
    }
    .lead { font-size: 18px; color: var(--muted); max-width: 640px; margin: 0 0 36px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
    .card {
      background: var(--card); border: 1px solid var(--border);
      border-radius: 18px; padding: 20px 22px;
      backdrop-filter: blur(10px);
      transition: transform .2s ease, border-color .2s ease;
    }
    .card:hover { transform: translateY(-3px); border-color: rgba(167, 139, 250, .5); }
    .card h3 { margin: 0 0 10px; font-size: 13px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
    .big { font-size: 28px; font-weight: 700; }
    .mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 14px; word-break: break-all; }
    h2 { margin: 48px 0 16px; font-size: 22px; }
    .steps { display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); counter-reset: s; }
    .step {
      counter-increment: s; position: relative;
      background: var(--card); border: 1px solid var(--border);
      border-radius: 16px; padding: 18px 16px 16px 16px;
    }
    .step::before {
      content: counter(s);
      display: inline-grid; place-items: center;
      width: 28px; height: 28px; border-radius: 50%;
      background: linear-gradient(135deg, var(--accent), var(--accent2));
      color: #0b0b1a; font-weight: 700; font-size: 14px; margin-bottom: 10px;
    }
    .step b { display: block; margin-bottom: 4px; }
    .step small { color: var(--muted); }
    .cmp { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
    .bar { display: flex; gap: 6px; margin: 10px 0 8px; }
    .bar i {
      flex: 1; height: 14px; border-radius: 6px;
      background: linear-gradient(90deg, var(--accent), var(--accent2));
    }
    .bar.agile i { flex: 0 0 calc(25% - 5px); opacity: .9; }
    footer { margin-top: 56px; text-align: center; color: var(--muted); font-size: 13px; }
  </style>
</head>
<body>
  <div class="wrap">
    <span class="badge"><span class="dot"></span> Online · Railway · {{ env }}</span>
    <h1>Лабораторная работа:<br><span>PaaS и деплой</span></h1>
    <p class="lead">{{ greeting }}. Это приложение на Flask развернуто на Railway и обновляется автоматически после каждого <code>git push</code>.</p>

    <div class="grid">
      <div class="card"><h3>Версия</h3><div class="big">v{{ version }}</div></div>
      <div class="card"><h3>Аптайм процесса</h3><div class="big" id="uptime">…</div></div>
      <div class="card"><h3>Время сервера (UTC)</h3><div class="big" id="clock">…</div></div>
      <div class="card"><h3>Коммит</h3><div class="mono">{{ sha }}</div><div style="color:var(--muted);margin-top:6px">{{ commit_msg }}</div></div>
      <div class="card"><h3>Ветка</h3><div class="mono">{{ branch }}</div></div>
      <div class="card"><h3>Окружение</h3><div class="mono">Python {{ py }}<br>{{ os_name }}</div></div>
    </div>

    <h2>Как код попадает в интернет</h2>
    <div class="steps">
      <div class="step"><b>Правим код</b><small>VS Code на Mac</small></div>
      <div class="step"><b>git commit</b><small>снимок в истории</small></div>
      <div class="step"><b>git push</b><small>отправка на GitHub</small></div>
      <div class="step"><b>Railway build</b><small>сборка и запуск gunicorn</small></div>
      <div class="step"><b>Готово</b><small>новая версия онлайн</small></div>
    </div>

    <h2>Waterfall и Agile</h2>
    <div class="cmp">
      <div class="card">
        <h3>Каскадная модель</h3>
        <div class="bar"><i></i><i></i><i></i><i></i></div>
        <small style="color:var(--muted)">Стадии идут строго друг за другом, результат виден только в конце.</small>
      </div>
      <div class="card">
        <h3>Agile</h3>
        <div class="bar agile"><i></i><i></i><i></i></div>
        <small style="color:var(--muted)">Короткие итерации, после каждой новая версия на Railway.</small>
      </div>
    </div>

    <footer>JSON с данными о приложении: <a href="/api/info" style="color:var(--accent2)">/api/info</a> · Health: <a href="/health" style="color:var(--accent2)">/health</a></footer>
  </div>

  <script>
    const started = new Date("{{ started }}").getTime();
    const pad = n => String(n).padStart(2, "0");
    function tick() {
      const now = new Date();
      const s = Math.max(0, Math.floor((now.getTime() - started) / 1000));
      const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60);
      document.getElementById("uptime").textContent = pad(h) + ":" + pad(m) + ":" + pad(s % 60);
      document.getElementById("clock").textContent =
        pad(now.getUTCHours()) + ":" + pad(now.getUTCMinutes()) + ":" + pad(now.getUTCSeconds());
    }
    tick(); setInterval(tick, 1000);
  </script>
</body>
</html>
"""


def info():
    sha = os.environ.get("RAILWAY_GIT_COMMIT_SHA", "локальный запуск")
    return {
        "version": VERSION,
        "greeting": os.environ.get("GREETING", "Привет из облака"),
        "env": os.environ.get("RAILWAY_ENVIRONMENT_NAME", "local"),
        "sha": sha[:7] if sha != "локальный запуск" else sha,
        "commit_msg": os.environ.get("RAILWAY_GIT_COMMIT_MESSAGE", "нет данных"),
        "branch": os.environ.get("RAILWAY_GIT_BRANCH", "local"),
        "py": platform.python_version(),
        "os_name": platform.system(),
        "started": STARTED.isoformat(),
    }


@app.route("/")
def index():
    return render_template_string(PAGE, **info())


@app.route("/api/info")
def api_info():
    return jsonify(info())


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)