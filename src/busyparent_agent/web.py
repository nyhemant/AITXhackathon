"""Tiny local web chat adapter for BusyParent Agent."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
from uuid import uuid4

from busyparent_agent.service import APP_TITLE, create_session, parse_now, run_book_scenario, run_scenario


SESSIONS = {}
BOOK_SESSIONS = {}


HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>BusyParent Agent</title>
    <style>
      :root {
        color: #2b2118;
        background: #fff7ed;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      * { box-sizing: border-box; }
      body { margin: 0; min-height: 100vh; padding: 24px; background: linear-gradient(135deg, #fff7ed, #fef3c7 58%, #e7f3df); transition: background .22s ease; }
      body[data-mode="dinner"] { background: linear-gradient(135deg, #fff7ed, #fef3c7 58%, #e7f3df); }
      body[data-mode="book"] { background: linear-gradient(135deg, #eef2ff, #f5f3ff 58%, #fdf2f8); }
      main { width: min(920px, 100%); margin: 0 auto; }
      header { margin-bottom: 18px; }
      h1 { margin: 0 0 6px; font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1; }
      .subhead { margin: 0; max-width: 680px; color: #6b5f55; line-height: 1.5; }
      .shell { overflow: hidden; border: 1px solid #fed7aa; border-radius: 24px; background: rgba(255,255,255,.86); box-shadow: 0 24px 70px rgba(124,45,18,.14); }
      .room-switch { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 14px; background: #fffaf5; border-bottom: 1px solid #fed7aa; }
      .room-card { display: grid; gap: 4px; min-height: 104px; border: 2px solid #fed7aa; border-radius: 8px; padding: 14px; background: white; color: #4b3425; text-align: left; box-shadow: none; }
      .room-card strong { display: block; font-size: 1.25rem; line-height: 1.1; }
      .room-card span { display: block; font-size: .9rem; line-height: 1.35; font-weight: 700; }
      .room-card .room-kicker { font-size: .75rem; letter-spacing: 0; text-transform: uppercase; color: #8a5a2f; }
      .room-card.active { border: 2px solid #c2410c; background: #fff7ed; }
      .book-room { border-color: #c7d2fe; }
      .book-room .room-kicker { color: #4338ca; }
      .book-room.active { border-color: #4f46e5; background: #eef2ff; }
      .toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; padding: 12px 14px; border-bottom: 1px solid #fed7aa; background: #fffaf5; }
      .hidden { display: none; }
      button { border: 0; border-radius: 999px; padding: 10px 14px; background: #ffedd5; color: #7c2d12; font-weight: 800; cursor: pointer; }
      .scenario-chip { min-height: 34px; padding: 8px 12px; background: #fff7ed; border: 1px solid #fed7aa; color: #7c2d12; font-size: .92rem; }
      .book-panel .scenario-chip { background: #eef2ff; border-color: #c7d2fe; color: #3730a3; }
      button.primary { background: #ea580c; color: white; }
      label { display: inline-flex; align-items: center; gap: 8px; color: #6b5f55; font-weight: 700; }
      .chat { display: grid; gap: 12px; min-height: 380px; max-height: 58vh; overflow-y: auto; padding: 18px; }
      .bubble { max-width: 78%; border-radius: 18px; padding: 12px 14px; line-height: 1.45; white-space: pre-wrap; }
      .parent { justify-self: end; background: #ea580c; color: white; border-bottom-right-radius: 6px; }
      .agent { justify-self: start; background: #f8fafc; border: 1px solid #e2e8f0; border-bottom-left-radius: 6px; }
      .trace { justify-self: stretch; display: none; border-left: 4px solid #f97316; border-radius: 12px; padding: 10px 12px; background: #fff7ed; color: #7c2d12; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .85rem; white-space: pre-wrap; }
      .show-trace .trace { display: block; }
      form { display: grid; grid-template-columns: 1fr auto; gap: 10px; padding: 14px; border-top: 1px solid #fed7aa; background: white; }
      input[type="text"] { min-width: 0; border: 1px solid #fed7aa; border-radius: 999px; padding: 12px 14px; font: inherit; }
      .story { margin: 12px 0 0; display: flex; flex-wrap: wrap; gap: 8px; }
      .story span { display: inline-flex; align-items: center; min-height: 32px; border: 1px solid #fed7aa; border-radius: 999px; padding: 6px 10px; background: #fffaf5; color: #7c2d12; font-weight: 800; font-size: .9rem; }
      .hint { margin: 14px 2px 0; color: #6b5f55; font-size: .92rem; }
      @media (max-width: 640px) {
        body { padding: 16px; }
        .room-switch { grid-template-columns: 1fr; }
        .bubble { max-width: 92%; }
        form { grid-template-columns: 1fr; }
      }
    </style>
  </head>
  <body data-mode="dinner">
    <main>
      <header>
        <h1 id="roomTitle">BusyParent Agent / Dinner Planner</h1>
        <p class="subhead">BusyParent Agent reduces evening decision load with one practical default at a time.</p>
        <p class="story"><span>Dinner handled</span><span>Bedtime book handled</span></p>
      </header>
      <section class="shell">
        <div class="room-switch" role="tablist" aria-label="BusyParent rooms">
          <button class="room-card dinner-room active" data-room-control="dinner" data-tab="dinner" type="button" aria-pressed="true">
            <span class="room-kicker">Dinner room</span>
            <strong>Dinner Planner</strong>
            <span>Plan tonight's meal and grocery gaps.</span>
          </button>
          <button class="room-card book-room" data-room-control="book" data-tab="book" type="button" aria-pressed="false">
            <span class="room-kicker">Bedtime book room</span>
            <strong>Story Picker</strong>
            <span>Pick one kid-right book for bedtime.</span>
          </button>
        </div>
        <div class="toolbar dinner-panel" data-panel="dinner">
          <button class="scenario-chip" data-scenario="dinner">Dinner now</button>
          <button class="scenario-chip" data-scenario="lunch">Plan at lunch</button>
          <button class="scenario-chip" data-scenario="guest">Guest child</button>
        </div>
        <div class="toolbar book-panel hidden" data-panel="book">
          <button class="scenario-chip" data-scenario="book">Pick tonight's book</button>
        </div>
        <div class="toolbar">
          <button id="clear" type="button">Clear</button>
          <label><input id="traceToggle" type="checkbox" checked /> Show trace</label>
        </div>
        <div id="chat" class="chat show-trace" aria-live="polite"></div>
        <form id="form">
          <input id="message" type="text" autocomplete="off" placeholder="Ask: What should I make for dinner tonight?" />
          <button class="primary" type="submit">Send</button>
        </form>
      </section>
      <p class="hint">Try: “Not feeling that. Anything else?” then “Let’s do Egg Fried Rice.”</p>
    </main>
    <script>
      let sessionId = null;
      let activeMode = "dinner";
      const chat = document.querySelector("#chat");
      const form = document.querySelector("#form");
      const input = document.querySelector("#message");
      const traceToggle = document.querySelector("#traceToggle");
      const roomTitle = document.querySelector("#roomTitle");
      const titles = {
        dinner: "BusyParent Agent / Dinner Planner",
        book: "BusyParent Agent / Story Picker"
      };
      const hints = {
        dinner: "Try: “Not feeling that. Anything else?” then “Let’s do Egg Fried Rice.”",
        book: "Try the Story Picker scenario for one mocked Epic-style read-aloud pick."
      };

      function addBubble(role, text) {
        const div = document.createElement("div");
        div.className = `bubble ${role}`;
        div.textContent = text;
        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
      }

      function addTrace(lines) {
        if (!lines || !lines.length) return;
        const div = document.createElement("div");
        div.className = "trace";
        div.textContent = lines.join("\\n");
        chat.appendChild(div);
      }

      function renderResponse(response) {
        if (response.context) addBubble("agent", `Context: ${response.context}`);
        addTrace(response.trace);
        addBubble("parent", response.parent_message);
        addBubble("agent", response.message);
      }

      async function postJson(path, payload) {
        const res = await fetch(path, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(await res.text());
        return res.json();
      }

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const message = input.value.trim();
        if (!message) return;
        input.value = "";
        const data = await postJson("/api/chat", { session_id: sessionId, message, mode: activeMode });
        sessionId = data.session_id;
        renderResponse(data.response);
      });

      document.querySelectorAll("[data-scenario]").forEach((button) => {
        button.addEventListener("click", async () => {
          chat.innerHTML = "";
          activeMode = button.dataset.scenario === "book" ? "book" : "dinner";
          document.body.dataset.mode = activeMode;
          roomTitle.textContent = titles[activeMode];
          const data = await postJson("/api/scenario", { scenario: button.dataset.scenario });
          sessionId = data.session_id;
          data.responses.forEach(renderResponse);
        });
      });

      document.querySelectorAll("[data-tab]").forEach((button) => {
        button.addEventListener("click", () => {
          const active = button.dataset.tab;
          activeMode = active === "book" ? "book" : "dinner";
          document.body.dataset.mode = activeMode;
          roomTitle.textContent = titles[activeMode];
          sessionId = null;
          document.querySelectorAll("[data-tab]").forEach((tab) => {
            tab.classList.toggle("active", tab.dataset.tab === active);
            tab.setAttribute("aria-pressed", String(tab.dataset.tab === active));
          });
          document.querySelectorAll("[data-panel]").forEach((panel) => {
            panel.classList.toggle("hidden", panel.dataset.panel !== active);
          });
          document.querySelector(".hint").textContent = hints[active];
        });
      });

      document.querySelector("#clear").addEventListener("click", () => {
        sessionId = null;
        chat.innerHTML = "";
      });

      traceToggle.addEventListener("change", () => {
        chat.classList.toggle("show-trace", traceToggle.checked);
      });
    </script>
  </body>
</html>
"""


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        self._send_text(HTML, "text/html; charset=utf-8")

    def do_POST(self) -> None:
        if self.path == "/api/chat":
            self._handle_chat()
            return
        if self.path == "/api/scenario":
            self._handle_scenario()
            return
        self.send_error(404)

    def _handle_chat(self) -> None:
        payload = self._read_json()
        mode = payload.get("mode") or payload.get("scenario")
        if mode == "book":
            session_id = payload.get("session_id") or str(uuid4())
            state = BOOK_SESSIONS.setdefault(session_id, {})
            response = run_book_scenario(
                trace=True,
                parent_message=payload.get("message") or "What should I read tonight?",
                exclude_book_ids=[state["last_book_id"]] if state.get("last_book_id") else None,
            )
            state["last_book_id"] = response["metadata"]["book_id"]
            self._send_json({"session_id": session_id, "response": response})
            return

        session_id = payload.get("session_id") or self._new_session()
        session = SESSIONS[session_id]
        response = session.send(payload.get("message", ""))
        self._send_json({"session_id": session_id, "response": response})

    def _handle_scenario(self) -> None:
        payload = self._read_json()
        scenario = payload.get("scenario")
        if scenario not in {"dinner", "lunch", "guest", "book"}:
            self.send_error(400, "Unknown scenario")
            return
        if scenario == "book":
            session_id = str(uuid4())
            response = run_book_scenario(trace=True)
            BOOK_SESSIONS[session_id] = {"last_book_id": response["metadata"]["book_id"]}
            self._send_json({"session_id": session_id, "responses": [response]})
            return

        session_id = self._new_session(scenario)
        responses = run_scenario(SESSIONS[session_id], scenario)
        self._send_json({"session_id": session_id, "responses": responses})

    def _new_session(self, scenario: str | None = None) -> str:
        session_id = str(uuid4())
        SESSIONS[session_id] = create_session(
            parse_now(None, scenario=scenario),
            trace=True,
            scenario=scenario,
            locked_time_context=scenario is not None,
        )
        return session_id

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_text(self, text: str, content_type: str) -> None:
        body = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Run the local web chat for {APP_TITLE}.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), WebHandler)
    url = f"http://{args.host}:{args.port}"
    print(f"{APP_TITLE}")
    print(f"Local web chat running at {url}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
