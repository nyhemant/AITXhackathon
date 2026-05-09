"""Tiny local web chat adapter for the BusyParent Kitchen Agent."""

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
    <title>BusyParent Kitchen Agent</title>
    <style>
      :root {
        color: #2b2118;
        background: #fff7ed;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      * { box-sizing: border-box; }
      body { margin: 0; min-height: 100vh; padding: 24px; background: linear-gradient(135deg, #fff7ed, #fef3c7 58%, #e7f3df); }
      main { width: min(920px, 100%); margin: 0 auto; }
      header { margin-bottom: 18px; }
      h1 { margin: 0 0 6px; font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1; }
      .subhead { margin: 0; max-width: 680px; color: #6b5f55; line-height: 1.5; }
      .shell { overflow: hidden; border: 1px solid #fed7aa; border-radius: 24px; background: rgba(255,255,255,.86); box-shadow: 0 24px 70px rgba(124,45,18,.14); }
      .tabs { display: flex; gap: 8px; padding: 14px 14px 0; background: #fffaf5; }
      .tab { background: #fff7ed; color: #7c2d12; border: 1px solid #fed7aa; }
      .tab.active { background: #7c2d12; color: white; }
      .toolbar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; padding: 14px; border-bottom: 1px solid #fed7aa; background: #fffaf5; }
      .hidden { display: none; }
      button { border: 0; border-radius: 999px; padding: 10px 14px; background: #ffedd5; color: #7c2d12; font-weight: 800; cursor: pointer; }
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
        .bubble { max-width: 92%; }
        form { grid-template-columns: 1fr; }
      }
    </style>
  </head>
  <body>
    <main>
      <header>
        <h1>BusyParent Kitchen Agent / HomePlate AI</h1>
        <p class="subhead">BusyParent reduces evening decision load with one practical default at a time.</p>
        <p class="story"><span>Dinner handled</span><span>Bedtime book handled</span></p>
      </header>
      <section class="shell">
        <div class="tabs" role="tablist" aria-label="BusyParent workflows">
          <button class="tab active" data-tab="dinner" type="button">Dinner</button>
          <button class="tab" data-tab="book" type="button">Bedtime Book</button>
        </div>
        <div class="toolbar" data-panel="dinner">
          <button data-scenario="dinner">Dinner now</button>
          <button data-scenario="lunch">Plan at lunch</button>
          <button data-scenario="guest">Guest child</button>
        </div>
        <div class="toolbar hidden" data-panel="book">
          <button data-scenario="book">Pick tonight's book</button>
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
      const hints = {
        dinner: "Try: “Not feeling that. Anything else?” then “Let’s do Egg Fried Rice.”",
        book: "Try the Bedtime Book scenario for one mocked Epic-style read-aloud pick."
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
          const data = await postJson("/api/scenario", { scenario: button.dataset.scenario });
          sessionId = data.session_id;
          data.responses.forEach(renderResponse);
        });
      });

      document.querySelectorAll("[data-tab]").forEach((button) => {
        button.addEventListener("click", () => {
          const active = button.dataset.tab;
          activeMode = active === "book" ? "book" : "dinner";
          sessionId = null;
          document.querySelectorAll("[data-tab]").forEach((tab) => {
            tab.classList.toggle("active", tab.dataset.tab === active);
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
