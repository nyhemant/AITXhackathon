"""Tiny local web chat adapter for 1Less."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
from uuid import uuid4

from busyparent_agent.service import APP_TITLE, create_dinner_decision_session


SESSIONS = {}


class RequestTooLarge(ValueError):
    """Raised when a public demo request body exceeds the small alpha limit."""


LOGO_FILENAME = "BMLogo.svg"
LOGO_PATH = Path(__file__).resolve().parents[2] / LOGO_FILENAME
MAX_REQUEST_BYTES = 24_000
SECURITY_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' https://www.google-analytics.com https://www.googletagmanager.com; "
        "font-src 'self'; "
        "base-uri 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    ),
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=(), bluetooth=()",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


HTML = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>1Less</title>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-6ZSEMN130R"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-6ZSEMN130R');
    </script>
    <style>
      :root {
        color: #27211d;
        background: #fff7ed;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      * { box-sizing: border-box; }
      body {
        --accent: #c2410c;
        --accent-dark: #7c2d12;
        --accent-soft: #fff7ed;
        --accent-line: #fed7aa;
        --page-a: #fff8f0;
        --page-b: #f7ead9;
        --page-c: #eaf3e4;
        --shadow: rgba(124, 45, 18, .13);
        margin: 0;
        min-height: 100vh;
        padding: 30px;
        background:
          radial-gradient(circle at 14% 12%, rgba(255,255,255,.86), transparent 28%),
          linear-gradient(135deg, var(--page-a), var(--page-b) 56%, var(--page-c));
        transition: background .24s ease, color .24s ease;
      }
      body[data-mode="dinner"] {
        --accent: #c2410c;
        --accent-dark: #7c2d12;
        --accent-soft: #fff7ed;
        --accent-line: #fed7aa;
        --page-a: #fff8f0;
        --page-b: #f7ead9;
        --page-c: #eaf3e4;
        --shadow: rgba(124, 45, 18, .13);
      }
      main { width: min(1080px, 100%); margin: 0 auto; }
      .hero { display: grid; gap: 22px; align-items: end; margin-bottom: 22px; }
      .brand-lockup { display: flex; gap: 18px; align-items: center; }
      .brand-logo { display: grid; place-items: center; width: 168px; height: 168px; flex: 0 0 auto; border: 1px solid rgba(194,65,12,.22); border-radius: 8px; background: linear-gradient(135deg, #fff7ed, #eef2ff); color: #0f3f72; font-size: 3.2rem; font-weight: 950; letter-spacing: 0; box-shadow: 0 18px 40px rgba(39,33,29,.12); }
      .brand-copy { min-width: 0; align-self: center; }
      .tagline { margin: 0 0 10px; color: #2f2924; font-size: clamp(1.5rem, 3.2vw, 2.25rem); font-weight: 620; line-height: 1.02; }
      .subhead { margin: 0; max-width: 710px; color: #665b52; line-height: 1.55; font-size: 1.03rem; }
      .alpha-note { display: inline-flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 14px; padding: 9px 12px; border: 1px solid rgba(194,65,12,.2); border-radius: 999px; background: rgba(255,255,255,.72); color: #5f554d; font-size: .9rem; line-height: 1.35; }
      .alpha-note strong { color: #7c2d12; }
      .shell { overflow: hidden; border: 1px solid rgba(255,255,255,.66); border-radius: 8px; background: rgba(255,255,255,.78); box-shadow: 0 30px 90px var(--shadow); backdrop-filter: blur(18px); }
      .mode-tabs { display: flex; gap: 6px; align-items: end; padding: 18px 18px 0; background: rgba(255,255,255,.52); border-bottom: 1px solid rgba(102,91,82,.16); }
      .mode-tab { position: relative; min-width: 220px; border: 1px solid rgba(102,91,82,.16); border-bottom: 0; border-radius: 8px 8px 0 0; padding: 17px 24px 18px; color: #51463f; text-align: left; font-size: 1.14rem; font-weight: 920; box-shadow: none; }
      #dinner-tab { background: #fff7ed; border-color: rgba(194,65,12,.22); color: #7c2d12; }
      .mode-tab:hover { transform: none; filter: saturate(1.04) brightness(1.01); }
      .mode-tab.active { margin-bottom: -1px; border-color: rgba(102,91,82,.22); background: rgba(255,255,255,.96); color: var(--accent-dark); box-shadow: 0 -8px 22px rgba(39,33,29,.07); }
      #dinner-tab.active { background: #fffaf5; border-color: rgba(194,65,12,.3); }
      .mode-tab.active::before { content: ""; position: absolute; left: 18px; right: 18px; top: 0; height: 4px; border-radius: 999px; background: var(--accent); }
      .mode-tab.active::after { content: ""; position: absolute; left: 0; right: 0; bottom: -1px; height: 2px; background: rgba(255,255,255,.96); }
      .tab-panel { background: rgba(255,255,255,.9); }
      .hidden { display: none; }
      button { border: 0; border-radius: 999px; padding: 10px 14px; background: #ffedd5; color: var(--accent-dark); font-weight: 850; cursor: pointer; transition: transform .15s ease, box-shadow .15s ease, background .15s ease; }
      button:hover { transform: translateY(-1px); }
      button.primary { align-self: start; min-height: 46px; border: 1px solid rgba(102,91,82,.18); border-radius: 10px; padding: 0 18px; background: rgba(255,255,255,.92); color: #51463f; box-shadow: none; font-size: 1rem; line-height: 1; }
      button.primary:hover { background: #f8fafc; }
      label { display: inline-flex; align-items: center; gap: 8px; color: #665b52; font-weight: 760; }
      .room-context { display: grid; gap: 10px; padding: 22px 24px; border-bottom: 1px solid rgba(102,91,82,.1); background: linear-gradient(135deg, rgba(255,255,255,.82), rgba(255,255,255,.48)); }
      .room-heading-row { display: flex; gap: 18px; align-items: baseline; justify-content: space-between; }
      .room-context h2 { flex: 0 0 auto; margin: 0; font-size: clamp(1.35rem, 3vw, 2rem); line-height: 1.08; letter-spacing: 0; white-space: nowrap; }
      .room-context p { margin: 0; max-width: 720px; color: #665b52; line-height: 1.55; }
      .proof-line { flex: 1 1 auto; min-width: 0; display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 12px; padding-top: 2px; color: #51463f; font-size: .9rem; font-weight: 760; cursor: default; }
      .proof-prefix { font-weight: 760; }
      .proof-line span { display: inline-flex; align-items: center; gap: 5px; }
      .proof-line span::before { content: "✓"; color: var(--accent); font-weight: 950; }
      .chat { display: grid; gap: 12px; min-height: 300px; max-height: 50vh; overflow-y: auto; overscroll-behavior: contain; scroll-behavior: smooth; scroll-padding: 18px; padding: 20px 24px; background: rgba(255,255,255,.28); }
      .chat[aria-busy="true"] { background: linear-gradient(180deg, rgba(255,255,255,.36), rgba(255,247,237,.44)); }
      .bubble { max-width: 78%; border-radius: 8px; padding: 12px 14px; line-height: 1.48; white-space: pre-wrap; }
      .new-turn { animation: riseIn .34s ease-out both, softPulse 1.2s ease-out; }
      .parent.new-turn { box-shadow: 0 0 0 3px rgba(255,237,213,.95), 0 14px 30px rgba(39,33,29,.16); }
      .thinking { justify-self: stretch; max-width: 100%; border: 1px dashed rgba(194,65,12,.28); border-left: 5px solid var(--accent-line); border-radius: 8px; padding: 13px 15px; background: rgba(255,247,237,.86); color: #665b52; font-weight: 800; }
      .thinking-dots::after { content: ""; display: inline-block; width: 1.4em; text-align: left; animation: dots 1.1s steps(4, end) infinite; }
      .parent { justify-self: end; background: #2f2924; color: white; border-bottom-right-radius: 2px; box-shadow: 0 12px 28px rgba(39,33,29,.12); }
      .agent { justify-self: stretch; max-width: 100%; border: 1px solid rgba(102,91,82,.14); border-left: 5px solid var(--accent); border-radius: 8px; padding: 18px 20px; background: rgba(255,255,255,.9); box-shadow: 0 18px 38px rgba(39,33,29,.08); color: #2d2722; }
      .agent::before { content: "Recommendation"; display: block; margin-bottom: 8px; color: var(--accent-dark); font-size: .74rem; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
      .dinner-card { justify-self: stretch; max-width: 100%; border: 1px solid rgba(124,45,18,.18); border-left: 5px solid var(--accent); border-radius: 14px; padding: 18px; background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(255,247,237,.92)); box-shadow: 0 18px 38px rgba(39,33,29,.08); color: #2d2722; }
      .dinner-card * { text-decoration: none; }
      .dinner-card a { color: #2563eb; font-weight: 850; text-decoration: underline; text-underline-offset: 3px; }
      .dinner-card-header { display: grid; gap: 9px; margin-bottom: 14px; }
      .meal-badge { width: fit-content; border: 1px solid rgba(194,65,12,.22); border-radius: 999px; padding: 5px 9px; background: #ffedd5; color: #7c2d12; font-size: .74rem; font-weight: 950; letter-spacing: .08em; text-transform: uppercase; }
      .meal-title { margin: 0; color: #241b16; font-size: clamp(1.28rem, 2.7vw, 1.72rem); line-height: 1.12; }
      .effort-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 0; padding: 0; list-style: none; }
      .effort-chip { display: inline-flex; align-items: center; gap: 6px; border: 1px solid rgba(102,91,82,.16); border-radius: 999px; padding: 7px 10px; background: rgba(255,255,255,.72); color: #4f453e; font-size: .88rem; font-weight: 820; }
      .dinner-section { margin-top: 14px; }
      .dinner-section h4 { margin: 0 0 8px; color: #7c2d12; font-size: .78rem; font-weight: 950; letter-spacing: .08em; text-transform: uppercase; }
      .plan-list { display: grid; gap: 8px; margin: 0; padding-left: 1.45rem; }
      .plan-list li { padding-left: 2px; line-height: 1.45; }
      .fallback-box, .safety-box { border-radius: 12px; padding: 12px 13px; line-height: 1.45; }
      .fallback-box { border: 1px solid rgba(124,45,18,.14); background: rgba(255,237,213,.72); }
      .safety-box { border: 1px solid rgba(146,64,14,.24); background: #fff7ed; color: #4f2b12; }
      .detail-list { display: grid; gap: 7px; margin: 0; padding: 0; list-style: none; color: #665b52; line-height: 1.45; }
      .detail-list li::before { content: "•"; margin-right: 8px; color: #7c2d12; font-weight: 950; }
      .decision-note { margin: 14px 0 0; color: #5f554d; font-size: .92rem; font-weight: 820; }
      .agent a { color: #2563eb; font-weight: 850; text-decoration: underline; text-underline-offset: 3px; }
      .agent a:visited { color: #4f46e5; }
      .trace { justify-self: stretch; display: none; border-left: 3px solid var(--accent-line); border-radius: 8px; padding: 11px 12px; background: rgba(255,255,255,.56); color: #65564c; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .8rem; white-space: pre-wrap; }
      .show-trace .trace { display: block; }
      form { position: relative; display: grid; grid-template-columns: auto 1fr auto; align-items: start; gap: 10px; padding: 16px; border-top: 1px solid rgba(102,91,82,.1); background: rgba(255,255,255,.82); }
      .input-copy { min-width: 0; display: grid; gap: 6px; }
      input[type="text"] { min-width: 0; width: 100%; border: 1px solid rgba(102,91,82,.18); border-radius: 999px; padding: 13px 15px; font: inherit; background: white; }
      input[type="text"]:focus { outline: 3px solid var(--accent-line); border-color: var(--accent); }
      .input-helper { margin: 0 4px; color: #665b52; font-size: .84rem; font-weight: 760; line-height: 1.32; }
      .input-helper-lead { display: block; color: #3f332b; font-weight: 900; }
      .input-helper-detail { display: block; margin-top: 2px; font-weight: 720; }
      .prompt-control { position: relative; align-self: start; }
      .prompt-trigger { display: inline-flex; flex-direction: column; align-items: center; justify-content: center; gap: 1px; min-height: 46px; min-width: 104px; border: 1px solid rgba(194,65,12,.24); border-radius: 10px; padding: 7px 12px; background: #ff7a00; color: #1f1306; box-shadow: 0 14px 30px rgba(255,122,0,.24); font-size: .95rem; line-height: 1.04; }
      .prompt-trigger span { display: block; }
      .prompt-trigger:hover { background: #ff8f1f; box-shadow: 0 16px 34px rgba(255,122,0,.3); }
      .prompt-trigger[aria-expanded="true"] { border-color: rgba(39,33,29,.28); filter: saturate(1.08); }
      .prompt-menu { position: absolute; left: 0; bottom: calc(100% + 10px); z-index: 20; width: min(430px, calc(100vw - 48px)); max-height: min(540px, 72vh); overflow: auto; border: 1px solid rgba(102,91,82,.18); border-radius: 8px; padding: 12px; background: rgba(255,255,255,.98); box-shadow: 0 24px 70px rgba(39,33,29,.16); }
      .prompt-helper { margin: 0 0 10px; color: #665b52; font-size: .86rem; font-weight: 760; }
      .prompt-list { display: grid; gap: 5px; }
      .prompt-option { width: 100%; border-radius: 6px; padding: 9px 10px; background: transparent; color: #2f2924; text-align: left; font-size: .92rem; font-weight: 750; box-shadow: none; }
      .prompt-option:hover { transform: none; background: var(--accent-soft); }
      .feedback-actions { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 24px 18px; background: rgba(255,255,255,.28); }
      .feedback-action { border: 1px solid rgba(102,91,82,.18); background: rgba(255,255,255,.88); color: #51463f; box-shadow: none; font-size: .88rem; }
      .vision-note { margin: 16px 0 12px; border: 1px solid rgba(102,91,82,.14); border-radius: 8px; padding: 18px 20px; background: rgba(255,255,255,.68); box-shadow: 0 12px 30px rgba(39,33,29,.06); }
      .vision-note h2 { margin: 0 0 7px; color: #7c2d12; font-size: 1rem; letter-spacing: .01em; }
      .vision-note p { margin: 0; max-width: 760px; color: #665b52; line-height: 1.5; }
      .trace-footer { margin: 14px 2px 0; color: #665b52; font-size: .92rem; }
      @keyframes riseIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes softPulse { 0% { outline: 0 solid rgba(255,237,213,0); } 24% { outline: 5px solid rgba(255,237,213,.82); } 100% { outline: 0 solid rgba(255,237,213,0); } }
      @keyframes dots { 0% { content: ""; } 25% { content: "."; } 50% { content: ".."; } 75%, 100% { content: "..."; } }
      @media (prefers-reduced-motion: reduce) {
        .chat { scroll-behavior: auto; }
        .new-turn, .thinking-dots::after { animation: none; }
      }
      @media (max-width: 640px) {
        body { padding: 16px; }
        .brand-lockup { gap: 12px; align-items: center; }
        .brand-logo { width: 124px; height: 124px; font-size: 2.35rem; }
        .mode-tabs { display: grid; grid-template-columns: 1fr; padding: 12px 12px 0; }
        .mode-tab { min-width: 0; padding: 14px 12px 15px; font-size: 1rem; }
        .room-heading-row { display: grid; gap: 10px; }
        .room-context h2 { white-space: normal; }
        .proof-line { justify-content: flex-start; }
        .bubble { max-width: 92%; }
        .agent { max-width: 100%; }
        .dinner-card { padding: 15px; border-radius: 12px; }
        .effort-chip { width: 100%; justify-content: flex-start; }
        form { grid-template-columns: auto 1fr; }
        .primary { grid-column: 1 / -1; justify-self: end; min-width: 88px; }
        .input-copy { grid-column: 2; }
        .input-helper { font-size: .78rem; }
        .prompt-menu { width: calc(100vw - 32px); }
      }
    </style>
  </head>
  <body data-mode="dinner">
    <main>
      <header class="hero">
        <div class="brand-lockup">
          <img class="brand-logo" src="/BMLogo.svg?v=helper" alt="1Less logo" width="1024" height="1024" />
          <div class="brand-copy">
          <p class="tagline">One less decision for busy parents.</p>
          <p class="subhead">Dinner first: a low-burden flow that turns tonight's constraints into one clear meal decision.</p>
          <p class="alpha-note"><strong>Alpha testing</strong></p>
          </div>
        </div>
      </header>
      <section class="shell">
        <div class="mode-tabs" aria-label="1Less public alpha flow">
          <div class="mode-tab active" id="dinner-tab" aria-current="page">
            Dinner
          </div>
        </div>
        <div class="tab-panel" id="active-panel" role="tabpanel" aria-labelledby="dinner-tab">
          <section class="room-context" data-room-context>
            <div class="room-heading-row">
              <h2 id="roomHeadline">Tonight's dinner, decided.</h2>
              <div class="proof-line" id="roomProofLine" aria-label="Dinner plan considers">
                <b class="proof-prefix">Based on</b>
                <span>Time</span>
                <span>Energy</span>
                <span>Fridge/pantry</span>
              </div>
            </div>
            <p id="roomDescription">Busy day? I can help with dinner decision. Just steer me in right direction</p>
          </section>
          <div id="chat" class="chat" aria-live="polite"></div>
          <form id="form">
            <div class="prompt-control" id="promptControl">
              <button class="prompt-trigger" id="promptButton" type="button" aria-label="Sample prompts" aria-haspopup="menu" aria-expanded="false" aria-controls="promptMenu"><span>Sample</span><span>prompts</span></button>
              <div class="prompt-menu hidden" id="promptMenu" role="menu" aria-label="Editable real-life dinner prompts">
                <p class="prompt-helper">Pick one, then edit it to match tonight.</p>
                <div class="prompt-list">
                  <button class="prompt-option" type="button" role="menuitem" data-prompt="It’s 5pm, everyone is hungry, I have 10 minutes and low cooking energy. Make it picky-kid friendly.">Low-energy 10 min</button>
                  <button class="prompt-option" type="button" role="menuitem" data-prompt="I have tortillas, cheese, black beans, rice, and apples. I have 15 minutes and no store run.">Use what we have</button>
                  <button class="prompt-option" type="button" role="menuitem" data-prompt="Vegetarian tonight. I have rice, eggs, frozen peas, and 20 minutes. Normal energy.">Vegetarian quick</button>
                  <button class="prompt-option" type="button" role="menuitem" data-prompt="Avoid peanuts and tree nuts tonight. I have pasta, jarred sauce, frozen peas, and 15 minutes.">Avoid nuts</button>
                  <button class="prompt-option" type="button" role="menuitem" data-prompt="My kid rejects mixed foods. I have chicken, rice, cucumber, yogurt, and 20 minutes. Make it easy to deconstruct.">Picky kid</button>
                  <button class="prompt-option" type="button" role="menuitem" data-prompt="I have a few options but no brain left to decide. We have eggs, toast, fruit, rice, and frozen vegetables. Pick one easy dinner.">Just pick one</button>
                </div>
              </div>
            </div>
            <div class="input-copy">
              <input id="message" type="text" autocomplete="off" aria-describedby="inputHelper" placeholder="What do you have, and what does tonight need?" />
              <p class="input-helper" id="inputHelper"><span class="input-helper-lead">Pick a sample, edit it, or type one messy sentence.</span></p>
            </div>
            <button class="primary" type="submit">Send</button>
          </form>
        </div>
      </section>
      <section class="vision-note" aria-labelledby="why-dinner-first">
        <h2 id="why-dinner-first">Why dinner first?</h2>
        <p>1Less may explore other parent decisions later, but this alpha is dinner-only. Right now we are testing whether one late-day dinner decision can be removed without creating another chore.</p>
      </section>
      <label class="trace-footer"><input id="traceToggle" type="checkbox" /> Show trace</label>
    </main>
    <script>
      let sessionId = null;
      let activeMode = "dinner";
      const chat = document.querySelector("#chat");
      const form = document.querySelector("#form");
      const input = document.querySelector("#message");
      const inputHelper = document.querySelector("#inputHelper");
      const traceToggle = document.querySelector("#traceToggle");
      const roomHeadline = document.querySelector("#roomHeadline");
      const roomDescription = document.querySelector("#roomDescription");
      const roomProofLine = document.querySelector("#roomProofLine");
      const tabPanel = document.querySelector("#active-panel");
      const promptControl = document.querySelector("#promptControl");
      const promptButton = document.querySelector("#promptButton");
      const promptMenu = document.querySelector("#promptMenu");
      const rooms = {
        dinner: {
          title: "Dinner",
          summary: "Tonight's dinner, decided.",
          headline: "Tonight's dinner, decided.",
          description: "Dinner is the current 1Less proof point: share the real-life constraints — time, energy, fridge/pantry options, and what the kids will tolerate.",
          proofLabel: "Dinner plan considers",
          proofPrefix: "Based on",
          proof: ["Time", "Energy", "Avoidances", "Fridge/pantry"]
        }
      };
      const inputCopyByState = {
        start: {
          placeholder: "What do you have, and what does tonight need?",
          helper: "Pick a sample, edit it, or type one messy sentence.",
          mobilePlaceholder: "What does tonight need?",
          mobileHelper: "Pick a sample or type one messy sentence."
        },
        recommendation: {
          placeholder: "Need it easier or more kid-proof?",
          helper: "Try: “too much work,” “kid won’t eat this,” “missing ingredient,” or “give me backup.”",
          mobilePlaceholder: "Need it easier or more kid-proof?",
          mobileHelper: "Try: too much work, kid won’t eat, missing ingredient, backup."
        },
        fallback: {
          placeholder: "Good enough, or one more tweak?",
          helper: "Say what failed — too much cleanup, missing ingredient, picky kid, or no energy.",
          mobilePlaceholder: "Good enough, or one more tweak?",
          mobileHelper: "Say what failed: cleanup, ingredient, picky kid, no energy."
        }
      };
      let inputCopyState = "start";
      const promptGroups = {
        dinner: [
          {
            label: "Low-energy 10 min",
            prompt: "It’s 5pm, everyone is hungry, I have 10 minutes and low cooking energy. Make it picky-kid friendly."
          },
          {
            label: "Use what we have",
            prompt: "I have tortillas, cheese, black beans, rice, and apples. I have 15 minutes and no store run."
          },
          {
            label: "Vegetarian quick",
            prompt: "Vegetarian tonight. I have rice, eggs, frozen peas, and 20 minutes. Normal energy."
          },
          {
            label: "Avoid nuts",
            prompt: "Avoid peanuts and tree nuts tonight. I have pasta, jarred sauce, frozen peas, and 15 minutes."
          },
          {
            label: "Picky kid",
            prompt: "My kid rejects mixed foods. I have chicken, rice, cucumber, yogurt, and 20 minutes. Make it easy to deconstruct."
          },
          {
            label: "Just pick one",
            prompt: "I have a few options but no brain left to decide. We have eggs, toast, fruit, rice, and frozen vegetables. Pick one easy dinner."
          }
        ]
      };

      function setRoom(active) {
        activeMode = "dinner";
        const room = rooms.dinner;
        document.body.dataset.mode = activeMode;
        roomHeadline.textContent = room.headline;
        roomDescription.textContent = room.description;
        roomProofLine.setAttribute("aria-label", room.proofLabel);
        roomProofLine.innerHTML = [
          room.proofPrefix ? `<b class="proof-prefix">${room.proofPrefix}</b>` : "",
          ...room.proof.map((point) => `<span>${point}</span>`)
        ].join("");
        updateInputCopy(inputCopyState);
        renderPromptMenu(activeMode);
        closePromptMenu();
        tabPanel.setAttribute("aria-labelledby", "dinner-tab");
      }

      function isMobileViewport() {
        return window.matchMedia("(max-width: 640px)").matches;
      }

      function updateInputCopy(state) {
        inputCopyState = state;
        const copy = inputCopyByState[state] || inputCopyByState.start;
        const mobile = isMobileViewport();
        input.placeholder = mobile ? copy.mobilePlaceholder : copy.placeholder;
        const helperText = mobile ? copy.mobileHelper : copy.helper;
        const helperDetail = mobile ? copy.mobileHelperDetail : copy.helperDetail;
        inputHelper.replaceChildren();
        const lead = document.createElement("span");
        lead.className = "input-helper-lead";
        lead.textContent = helperText;
        inputHelper.appendChild(lead);
        if (helperDetail) {
          const detail = document.createElement("span");
          detail.className = "input-helper-detail";
          detail.textContent = helperDetail;
          inputHelper.appendChild(detail);
        }
      }

      function inputStateForResponse(response) {
        const message = response.message || "";
        if (message.trim().startsWith("Backup:")) return "fallback";
        return "recommendation";
      }


      function trackEvent(name, params) {
        if (typeof gtag === "function") {
          gtag("event", name, params || {});
        }
      }

      function escapeHtml(text) {
        return text
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;");
      }

      function renderPromptMenu(mode) {
        const groups = promptGroups[mode];
        promptMenu.setAttribute("aria-label", "Editable real-life dinner prompts");
        promptMenu.innerHTML = `
          <p class="prompt-helper">Pick one, then edit it to match tonight.</p>
          <div class="prompt-list">
            ${groups.map((sample) => `
              <button class="prompt-option" type="button" role="menuitem" data-prompt="${escapeHtml(sample.prompt)}">${escapeHtml(sample.label)}</button>
            `).join("")}
          </div>
        `;
      }

      function closePromptMenu() {
        promptMenu.classList.add("hidden");
        promptButton.setAttribute("aria-expanded", "false");
      }

      function togglePromptMenu() {
        const isOpen = !promptMenu.classList.contains("hidden");
        promptMenu.classList.toggle("hidden", isOpen);
        promptButton.setAttribute("aria-expanded", String(!isOpen));
      }

      function placeChatNode(node, replaceNode = null) {
        if (replaceNode && replaceNode.parentNode === chat) {
          chat.replaceChild(node, replaceNode);
        } else {
          chat.appendChild(node);
        }
        return node;
      }

      function scrollTurnIntoView(turnStart, behavior = "smooth") {
        if (!turnStart) {
          chat.scrollTo({ top: chat.scrollHeight, behavior });
          return;
        }
        const targetTop = Math.max(0, turnStart.offsetTop - 16);
        chat.scrollTo({ top: targetTop, behavior });
      }

      function addBubble(role, text, options = {}) {
        const div = document.createElement("div");
        div.className = `bubble ${role}${options.isNewTurn ? " new-turn" : ""}`;
        div.textContent = text;
        placeChatNode(div, options.replaceNode);
        scrollTurnIntoView(options.turnStart || div, options.behavior || "smooth");
        return div;
      }

      function addThinkingBubble(turnStart) {
        const div = document.createElement("div");
        div.className = "thinking new-turn";
        div.setAttribute("role", "status");
        div.setAttribute("aria-live", "polite");
        div.innerHTML = `Deciding dinner<span class="thinking-dots" aria-hidden="true"></span>`;
        placeChatNode(div);
        scrollTurnIntoView(turnStart, "smooth");
        return div;
      }

      function stripTrailingPeriod(text) {
        return text.replace(/[.]$/, "");
      }

      function splitDinnerPlan(planText) {
        const clean = stripTrailingPeriod(planText.trim());
        if (!clean) return [];
        const normalized = clean.replace(/, and /g, ", ").replace(/ and /g, ", ");
        const parts = normalized.split(/,\\s+/).map((part) => part.trim()).filter(Boolean);
        if (parts.length <= 3) return parts;
        return [parts[0], parts[1], parts.slice(2).join(", ")];
      }

      function parseDinnerMessage(message) {
        const parsed = {
          badge: "Dinner",
          title: "Dinner decision",
          why: [],
          effort: "",
          basics: "",
          plan: [],
          fallback: "",
          safety: "",
          note: "",
          details: []
        };
        message.split("\\n").map((line) => line.trim()).filter(Boolean).forEach((line) => {
          if (line.startsWith("Tonight:")) {
            parsed.badge = "Tonight";
            parsed.title = stripTrailingPeriod(line.replace("Tonight:", "").trim());
          } else if (line.startsWith("Backup:")) {
            parsed.badge = "Backup";
            parsed.title = stripTrailingPeriod(line.replace("Backup:", "").trim());
          } else if (line.startsWith("Why this is easier:")) {
            parsed.why.push(line.replace("Why this is easier:", "").trim());
          } else if (line.startsWith("Why it fits:")) {
            parsed.why.push(line.replace("Why it fits:", "").trim());
          } else if (line.startsWith("Time/effort:")) {
            parsed.effort = line.replace("Time/effort:", "").trim();
          } else if (line.startsWith("Constraint heard:")) {
            parsed.details.push(line);
          } else if (line.startsWith("Works with common basics like:")) {
            parsed.basics = line.replace("Works with common basics like:", "").trim();
          } else if (line.startsWith("Simple plan:")) {
            parsed.plan = splitDinnerPlan(line.replace("Simple plan:", "").trim());
          } else if (line.startsWith("Fallback/tweak:")) {
            parsed.fallback = line.replace("Fallback/tweak:", "").trim();
          } else if (line.includes("cannot guarantee allergy safety") || line.includes("Always check labels")) {
            parsed.safety = line;
          } else if (line === "One decision, not a recipe search.") {
            parsed.note = line;
          } else {
            parsed.details.push(line);
          }
        });
        return parsed;
      }

      function effortChips(effortText) {
        if (!effortText) return [];
        const clean = stripTrailingPeriod(effortText);
        const parts = clean.split(",").map((part) => part.trim()).filter(Boolean);
        return parts.map((part, index) => index === 0 ? `⏱ ${part}` : `Energy: ${part}`);
      }

      function renderDinnerCard(response, options = {}) {
        const parsed = parseDinnerMessage(response.message || "");
        const article = document.createElement("article");
        article.className = `dinner-card${options.isNewTurn ? " new-turn" : ""}`;
        article.setAttribute("aria-label", `${parsed.badge} dinner recommendation: ${parsed.title}`);
        const chips = effortChips(parsed.effort);
        article.innerHTML = `
          <header class="dinner-card-header">
            <span class="meal-badge">${escapeHtml(parsed.badge)}</span>
            <h3 class="meal-title">${escapeHtml(parsed.title)}</h3>
            ${chips.length ? `<ul class="effort-chips" aria-label="Time and effort">${chips.map((chip) => `<li class="effort-chip">${escapeHtml(chip)}</li>`).join("")}</ul>` : ""}
          </header>
          ${parsed.plan.length ? `<section class="dinner-section" aria-label="Three-step plan"><h4>3-step plan</h4><ol class="plan-list">${parsed.plan.map((step) => `<li>${escapeHtml(step)}</li>`).join("")}</ol></section>` : ""}
          ${parsed.fallback ? `<section class="dinner-section" aria-label="Fallback or tweak"><h4>Fallback</h4><div class="fallback-box">${escapeHtml(parsed.fallback)}</div></section>` : ""}
          ${(parsed.why.length || parsed.basics || parsed.details.length) ? `<section class="dinner-section" aria-label="Why this fits"><h4>Why this fits</h4><ul class="detail-list">${parsed.why.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}${parsed.basics ? `<li>Works with common basics like: ${escapeHtml(parsed.basics)}</li>` : ""}${parsed.details.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></section>` : ""}
          ${parsed.safety ? `<section class="dinner-section safety-box" role="note" aria-label="Safety caveat"><h4>Safety note</h4><p>${escapeHtml(parsed.safety)}</p></section>` : ""}
          ${parsed.note ? `<p class="decision-note">${escapeHtml(parsed.note)}</p>` : ""}
        `;
        placeChatNode(article, options.replaceNode);
        scrollTurnIntoView(options.turnStart || article, options.behavior || "smooth");
        return article;
      }

      function renderDinnerFeedbackActions() {
        document.querySelectorAll(".feedback-actions").forEach((node) => node.remove());
        if (activeMode !== "dinner") return;
        const actions = [
          ["Good enough", "Good enough"],
          ["Too much work", "Too much work"],
          ["Kid won't eat", "Kid won't eat this"],
          ["Missing ingredient", "Missing ingredient"],
          ["Give me backup", "Give me backup"]
        ];
        const wrap = document.createElement("div");
        wrap.className = "feedback-actions";
        actions.forEach(([label, message]) => {
          const button = document.createElement("button");
          button.className = "feedback-action";
          button.type = "button";
          button.dataset.feedback = message;
          button.textContent = label;
          wrap.appendChild(button);
        });
        chat.insertAdjacentElement("afterend", wrap);
      }

      function addTrace(lines) {
        if (!lines || !lines.length) return;
        const div = document.createElement("div");
        div.className = "trace";
        div.textContent = lines.join("\\n");
        chat.appendChild(div);
      }

      function renderResponse(response, options = {}) {
        const isDinnerDecision = response.metadata && response.metadata.chapter === "chapter_1_dinner_decision";
        const turnStart = options.turnStart || null;
        if (response.context) addBubble("agent", `Context: ${response.context}`, { turnStart });
        const parentBubble = options.skipParent ? turnStart : addBubble("parent", response.parent_message, { isNewTurn: true });
        if (isDinnerDecision) {
          renderDinnerCard(response, { replaceNode: options.replaceNode, turnStart: parentBubble || turnStart, isNewTurn: true });
        } else {
          addBubble("agent", response.message, { replaceNode: options.replaceNode, turnStart: parentBubble || turnStart, isNewTurn: true });
        }
        addTrace(response.trace);
        scrollTurnIntoView(parentBubble || turnStart, "smooth");
        if (isDinnerDecision) {
          updateInputCopy(inputStateForResponse(response));
          renderDinnerFeedbackActions();
        }
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

      async function sendCurrentInput() {
        const message = input.value.trim();
        if (!message) return;
        document.querySelectorAll(".feedback-actions").forEach((node) => node.remove());
        input.value = "";
        chat.setAttribute("aria-busy", "true");
        const parentBubble = addBubble("parent", message, { isNewTurn: true });
        const thinkingBubble = addThinkingBubble(parentBubble);
        try {
          const data = await postJson("/api/chat", { session_id: sessionId, message, mode: activeMode });
          sessionId = data.session_id;
          renderResponse(data.response, { skipParent: true, turnStart: parentBubble, replaceNode: thinkingBubble });
        } catch (error) {
          addBubble("agent", "Something hiccuped. Try Send once more.", { replaceNode: thinkingBubble, turnStart: parentBubble, isNewTurn: true });
          console.error(error);
        } finally {
          chat.setAttribute("aria-busy", "false");
        }
      }

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        await sendCurrentInput();
      });

      document.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-feedback]");
        if (!button) return;
        input.value = button.dataset.feedback;
        await sendCurrentInput();
      });

      promptButton.addEventListener("click", (event) => {
        event.stopPropagation();
        togglePromptMenu();
      });

      promptMenu.addEventListener("click", async (event) => {
        const button = event.target.closest("[data-prompt]");
        if (!button) return;
        input.value = button.dataset.prompt;
        closePromptMenu();
        input.focus();
      });

      document.addEventListener("click", (event) => {
        if (!promptControl.contains(event.target)) closePromptMenu();
      });

      document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") closePromptMenu();
      });

      window.addEventListener("resize", () => updateInputCopy(inputCopyState));

      traceToggle.addEventListener("change", () => {
        chat.classList.toggle("show-trace", traceToggle.checked);
      });
    </script>
  </body>
</html>
"""


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == f"/{LOGO_FILENAME}":
            if not LOGO_PATH.exists():
                self.send_error(404)
                return
            content_type = "image/svg+xml" if LOGO_PATH.suffix == ".svg" else "image/png"
            self._send_binary(LOGO_PATH.read_bytes(), content_type)
            return
        if path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        self._send_text(HTML, "text/html; charset=utf-8")

    def do_HEAD(self) -> None:
        path = urlsplit(self.path).path
        if path not in {"/", "/index.html", f"/{LOGO_FILENAME}"}:
            self.send_error(404)
            return
        content_type = "image/svg+xml" if path == f"/{LOGO_FILENAME}" else "text/html; charset=utf-8"
        length = LOGO_PATH.stat().st_size if path == f"/{LOGO_FILENAME}" and LOGO_PATH.exists() else len(HTML.encode("utf-8"))
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.end_headers()

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/chat":
            self._handle_chat()
            return
        if path == "/api/scenario":
            self._handle_scenario()
            return
        self.send_error(404)

    def _handle_chat(self) -> None:
        try:
            payload = self._read_json()
        except RequestTooLarge:
            self.send_error(413, "Request body too large")
            return
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "Invalid JSON")
            return
        mode = payload.get("mode") or payload.get("scenario")
        if mode == "book":
            self.send_error(404, "Story Picker is not part of the public alpha")
            return

        requested_session_id = payload.get("session_id")
        session_id = requested_session_id if requested_session_id in SESSIONS else self._new_session()
        session = SESSIONS[session_id]
        response = session.send(payload.get("message", ""))
        self._send_json({"session_id": session_id, "response": response})

    def _handle_scenario(self) -> None:
        try:
            payload = self._read_json()
        except RequestTooLarge:
            self.send_error(413, "Request body too large")
            return
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "Invalid JSON")
            return
        scenario = payload.get("scenario")
        if scenario not in {"dinner", "lunch", "guest"}:
            self.send_error(400, "Unknown scenario")
            return

        session_id = self._new_session(scenario)
        scenario_messages = {
            "dinner": "What should I make for dinner tonight?",
            "lunch": "I have 15 minutes and barely cooking energy.",
            "guest": "Avoid peanuts and tree nuts tonight. Make it picky-kid friendly.",
        }
        responses = [SESSIONS[session_id].send(scenario_messages[scenario], scenario=scenario)]
        self._send_json({"session_id": session_id, "responses": responses})

    def _new_session(self, scenario: str | None = None) -> str:
        session_id = str(uuid4())
        SESSIONS[session_id] = create_dinner_decision_session()
        return session_id

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > MAX_REQUEST_BYTES:
            raise RequestTooLarge("Request body too large")
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
        self._send_binary(body, content_type)

    def _send_binary(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self) -> None:
        self._send_security_headers()
        super().end_headers()

    def _send_security_headers(self) -> None:
        for name, value in SECURITY_HEADERS.items():
            self.send_header(name, value)

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
