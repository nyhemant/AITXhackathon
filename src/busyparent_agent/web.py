"""Tiny local web chat adapter for 1Less."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid4

from busyparent_agent.service import APP_TITLE, create_dinner_decision_session


SESSIONS = {}


class RequestTooLarge(ValueError):
    """Raised when a public demo request body exceeds the small alpha limit."""


LOGO_FILENAME = "1LessPrimaryLogo.png"
PLAN_B_LOGO_FILENAME = "1LessMark.png"
MOBILE_LOGO_FILENAME = LOGO_FILENAME
REPO_ROOT = Path(__file__).resolve().parents[2]
LOGO_PATH = REPO_ROOT / LOGO_FILENAME
PLAN_B_LOGO_PATH = REPO_ROOT / PLAN_B_LOGO_FILENAME
MOBILE_LOGO_PATH = LOGO_PATH
LOGO_ASSETS = {LOGO_FILENAME: LOGO_PATH, PLAN_B_LOGO_FILENAME: PLAN_B_LOGO_PATH}
# Arya's Field Pack static site (trips, missions, treasure hunt)
FIELD_PACK_ROOT = REPO_ROOT / "static" / "field-pack"
FIELD_PACK_PREFIX = "/field-pack"
MAX_REQUEST_BYTES = 24_000
ANALYTICS_COOKIE = "one_less_analytics"
ANALYTICS_OFF_VALUE = "off"
GA4_SNIPPET = """    <script async src="https://www.googletagmanager.com/gtag/js?id=G-X6V6PNY9ZV"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-X6V6PNY9ZV');
    </script>"""
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
{ga4_snippet}
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
      .brand-logo-wrap { display: block; flex: 0 0 auto; line-height: 0; }
      .brand-logo { display: block; width: min(148px, 32vw); height: min(148px, 32vw); border: 0; border-radius: 0; background: transparent; box-shadow: none; object-fit: contain; }
      .brand-copy { min-width: 0; align-self: center; }
      .tagline { margin: 0 0 10px; color: #2f2924; font-size: clamp(1.5rem, 3.2vw, 2.25rem); font-weight: 620; line-height: 1.02; }
      .subhead { margin: 0; max-width: 710px; color: #665b52; line-height: 1.55; font-size: 1.03rem; }
      .alpha-note { display: inline-flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 14px; padding: 9px 12px; border: 1px solid rgba(194,65,12,.2); border-radius: 999px; background: rgba(255,255,255,.72); color: #5f554d; font-size: .9rem; line-height: 1.35; }
      .alpha-note strong { color: #7c2d12; }
      .product-threads {
        display: flex; flex-wrap: wrap; gap: 8px; align-items: center;
        margin: 0 0 18px; padding: 8px;
        border: 1px solid rgba(194,65,12,.16); border-radius: 16px;
        background: rgba(255,255,255,.82); width: fit-content; max-width: 100%;
        box-shadow: 0 10px 28px rgba(124,45,18,.06);
      }
      .product-threads .thread {
        display: inline-flex; align-items: center; gap: 8px;
        border: 1px solid transparent; border-radius: 12px;
        padding: 10px 14px; text-decoration: none; color: #665b52; font-weight: 850;
      }
      .product-threads .thread:visited { color: #665b52; }
      .product-threads .thread:hover { background: #fff7ed; color: #7c2d12; }
      .product-threads .thread.active {
        border-color: rgba(194,65,12,.28); background: #ffedd5; color: #7c2d12;
        box-shadow: 0 8px 18px rgba(255,122,0,.12);
      }
      .product-threads .thread small {
        display: block; font-size: .75rem; font-weight: 720; opacity: .85; margin-top: 2px;
      }
      .product-threads .thread-copy { display: grid; gap: 0; line-height: 1.15; }
      .family-tools {
        display: flex; flex-wrap: wrap; gap: 10px; align-items: center;
        margin-top: 16px; padding: 12px 14px;
        border: 1px solid rgba(194,65,12,.18); border-radius: 14px;
        background: rgba(255,255,255,.78); max-width: 720px;
      }
      .family-tools-label { color: #7c2d12; font-size: .78rem; font-weight: 950; letter-spacing: .06em; text-transform: uppercase; }
      .family-tools a {
        display: inline-flex; align-items: center; gap: 6px;
        border: 1px solid rgba(194,65,12,.22); border-radius: 999px;
        padding: 8px 14px; background: #ffedd5; color: #7c2d12;
        font-weight: 850; font-size: .95rem; text-decoration: none;
        box-shadow: 0 8px 18px rgba(124,45,18,.08);
      }
      .family-tools a:hover { background: #fed7aa; }
      .family-tools a:visited { color: #7c2d12; }
      .family-tools .hint { color: #665b52; font-size: .88rem; font-weight: 720; line-height: 1.35; flex: 1 1 200px; }
      .shell { overflow: hidden; border: 1px solid rgba(255,255,255,.66); border-radius: 8px; background: rgba(255,255,255,.78); box-shadow: 0 30px 90px var(--shadow); backdrop-filter: blur(18px); }
      .tab-panel { background: rgba(255,255,255,.9); }
      .hidden { display: none; }
      button { border: 0; border-radius: 999px; padding: 10px 14px; background: #ffedd5; color: var(--accent-dark); font-weight: 850; cursor: pointer; transition: transform .15s ease, box-shadow .15s ease, background .15s ease; }
      button:hover { transform: translateY(-1px); }
      button.primary { align-self: start; min-height: 46px; border: 1px solid rgba(194,65,12,.24); border-radius: 10px; padding: 0 18px; background: #ff7a00; color: #1f1306; box-shadow: 0 14px 30px rgba(255,122,0,.24); font-size: 1rem; line-height: 1; }
      button.primary:hover { background: #ff8f1f; box-shadow: 0 16px 34px rgba(255,122,0,.3); }
      label { display: inline-flex; align-items: center; gap: 8px; color: #665b52; font-weight: 760; }
      .room-context { display: grid; gap: 10px; padding: 22px 24px; border-bottom: 1px solid rgba(102,91,82,.1); background: linear-gradient(135deg, rgba(255,255,255,.82), rgba(255,255,255,.48)); }
      .room-heading-row { display: flex; gap: 18px; align-items: baseline; justify-content: space-between; }
      .room-context h2 { flex: 0 0 auto; margin: 0; font-size: clamp(1.35rem, 3vw, 2rem); line-height: 1.08; letter-spacing: 0; white-space: nowrap; }
      .room-context p { margin: 0; max-width: 720px; color: #665b52; line-height: 1.55; }
      .chat { display: grid; gap: 12px; min-height: 300px; max-height: 50vh; overflow-y: auto; overscroll-behavior: contain; scroll-behavior: smooth; scroll-padding: 18px; padding: 20px 24px; background: rgba(255,255,255,.28); }
      .empty-state { align-self: start; border: 1px dashed rgba(194,65,12,.22); border-radius: 14px; padding: 16px; background: rgba(255,247,237,.76); color: #5f554d; }
      .empty-state h3 { margin: 0 0 6px; color: #3f332b; font-size: 1rem; }
      .empty-state p { margin: 0; line-height: 1.45; }
      .example-chips { display: flex; flex-wrap: wrap; gap: 8px; }
      .example-chip { border: 1px solid rgba(102,91,82,.18); border-radius: 999px; padding: 8px 10px; background: rgba(255,255,255,.88); color: #51463f; box-shadow: none; font-size: .88rem; font-weight: 820; }
      .example-chip:hover { transform: none; background: #fff7ed; }
      .example-expand { margin-top: 10px; border: 1px solid rgba(194,65,12,.22); background: #ffedd5; color: #7c2d12; box-shadow: none; font-size: .88rem; }
      .example-expand:hover { background: #fed7aa; transform: none; }
      .completion { justify-self: stretch; max-width: 100%; border: 1px solid rgba(22,101,52,.18); border-left: 5px solid #22c55e; border-radius: 12px; padding: 14px 16px; background: rgba(240,253,244,.88); color: #21402b; font-weight: 850; }
      .chat[aria-busy="true"] { background: linear-gradient(180deg, rgba(255,255,255,.36), rgba(255,247,237,.44)); }
      .bubble { max-width: 78%; border-radius: 8px; padding: 12px 14px; line-height: 1.48; white-space: pre-wrap; }
      .new-turn { animation: riseIn .34s ease-out both, softPulse 1.2s ease-out; }
      .parent.new-turn { box-shadow: 0 0 0 3px rgba(255,237,213,.95), 0 14px 30px rgba(39,33,29,.16); }
      .thinking { justify-self: stretch; max-width: 100%; border: 1px dashed rgba(194,65,12,.28); border-left: 5px solid var(--accent-line); border-radius: 8px; padding: 13px 15px; background: rgba(255,247,237,.86); color: #665b52; font-weight: 800; }
      .thinking-dots::after { content: ""; display: inline-block; width: 1.4em; text-align: left; animation: dots 1.1s steps(4, end) infinite; }
      .parent { justify-self: end; background: #2f2924; color: white; border-bottom-right-radius: 2px; box-shadow: 0 12px 28px rgba(39,33,29,.12); }
      .answer-preview { justify-self: stretch; position: relative; max-width: 100%; border: 1px dashed rgba(194,65,12,.18); border-left: 5px solid rgba(194,65,12,.18); border-radius: 8px; padding: 14px 16px 13px; background: rgba(255,247,237,.42); color: rgba(95,85,77,.66); box-shadow: 0 8px 20px rgba(194,65,12,.035); opacity: .76; animation: previewGlow 1.4s ease-out; }
      .answer-preview::before { content: "Preview only"; display: block; margin-bottom: 6px; color: rgba(154,52,18,.68); font-size: .72rem; font-weight: 900; letter-spacing: .08em; text-transform: uppercase; }
      .answer-preview-text { display: block; max-height: 4.5em; overflow: hidden; -webkit-mask-image: linear-gradient(180deg, #000 48%, rgba(0,0,0,.7) 72%, transparent 100%); mask-image: linear-gradient(180deg, #000 48%, rgba(0,0,0,.7) 72%, transparent 100%); }
      .answer-preview-helper { display: block; margin-top: 10px; border-top: 1px solid rgba(194,65,12,.11); padding-top: 9px; color: rgba(124,45,18,.78); font-size: .83rem; font-weight: 850; white-space: normal; }
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
      .detail-list { display: grid; gap: 7px; margin: 0; padding-left: 1.2rem; color: #665b52; line-height: 1.45; }
      .detail-list li::marker { color: #7c2d12; font-weight: 950; }
      .decision-note { margin: 14px 0 0; color: #5f554d; font-size: .92rem; font-weight: 820; }
      .agent a { color: #2563eb; font-weight: 850; text-decoration: underline; text-underline-offset: 3px; }
      .agent a:visited { color: #4f46e5; }
      .trace { justify-self: stretch; display: none; border-left: 3px solid var(--accent-line); border-radius: 8px; padding: 11px 12px; background: rgba(255,255,255,.56); color: #65564c; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: .8rem; white-space: pre-wrap; }
      .show-trace .trace { display: block; }
      form { position: relative; display: grid; gap: 12px; padding: 18px 20px; border-top: 1px solid rgba(102,91,82,.1); border-bottom: 1px solid rgba(102,91,82,.1); background: rgba(255,255,255,.86); }
      .prompt-label { margin: 0 4px -2px; color: #3f332b; font-size: .86rem; font-weight: 950; letter-spacing: .06em; text-transform: uppercase; }
      .input-copy { min-width: 0; display: grid; gap: 7px; }
      textarea { box-sizing: border-box; min-width: 0; width: 100%; min-height: calc(1.48em * 3 + 28px); max-height: calc(1.48em * 10 + 28px); border: 1px solid rgba(102,91,82,.2); border-radius: 14px; padding: 14px 15px; font: inherit; line-height: 1.48; background: white; resize: none; overflow-y: hidden; }
      textarea:focus { outline: 3px solid var(--accent-line); border-color: var(--accent); }
      .input-helper { margin: 0 4px; color: #665b52; font-size: .84rem; font-weight: 760; line-height: 1.32; }
      .input-helper-lead { display: block; color: #3f332b; font-weight: 900; }
      .input-helper-detail { display: block; margin-top: 2px; font-weight: 720; }
      .prompt-helper-tabs { display: flex; flex-wrap: wrap; gap: 0; align-items: flex-end; margin-bottom: -13px; padding: 0 4px; }
      .helper-tab { position: relative; border: 1px solid rgba(102,91,82,.16); border-bottom-color: rgba(102,91,82,.12); border-radius: 12px 12px 0 0; padding: 10px 14px 11px; background: rgba(255,255,255,.68); color: #665b52; box-shadow: none; font-size: .88rem; }
      .helper-tab + .helper-tab { margin-left: -1px; }
      .helper-tab:hover { background: #fff7ed; transform: none; }
      .helper-tab.active, .helper-tab[aria-selected="true"] { z-index: 1; border-color: rgba(194,65,12,.24); border-bottom-color: rgba(255,247,237,.92); background: rgba(255,247,237,.92); color: #7c2d12; box-shadow: 0 -8px 18px rgba(124,45,18,.04); }
      .helper-tab:focus-visible { outline: 3px solid var(--accent-line); outline-offset: 2px; }
      .helper-panel { display: grid; gap: 10px; border: 1px solid rgba(194,65,12,.16); border-radius: 12px; padding: 14px 12px 12px; background: rgba(255,247,237,.92); }
      .helper-panel.hidden { display: none; }
      .helper-panel p { margin: 0; color: #665b52; font-size: .86rem; font-weight: 760; line-height: 1.42; }
      .photo-helper-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(160px, auto) auto; gap: 8px; align-items: center; }
      .photo-helper-grid input, .photo-helper-grid select { min-width: 0; width: 100%; border: 1px solid rgba(102,91,82,.18); border-radius: 10px; padding: 10px 11px; background: #fff; color: #3f332b; font: inherit; font-size: .9rem; }
      .photo-helper-grid button { border-radius: 10px; background: #ffedd5; box-shadow: none; }
      .input-nudge { grid-column: 1 / -1; margin: -2px 4px 0; color: #7c2d12; font-size: .86rem; font-weight: 820; }
      .feedback-actions { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 24px 18px; background: rgba(255,255,255,.28); }
      .feedback-action { border: 1px solid rgba(102,91,82,.18); background: rgba(255,255,255,.88); color: #51463f; box-shadow: none; font-size: .88rem; }
      .vision-note { margin: 16px 0 12px; border: 1px solid rgba(102,91,82,.14); border-radius: 8px; padding: 18px 20px; background: rgba(255,255,255,.68); box-shadow: 0 12px 30px rgba(39,33,29,.06); }
      .vision-note h2 { margin: 0 0 7px; color: #7c2d12; font-size: 1rem; letter-spacing: .01em; }
      .vision-note p { margin: 0; max-width: 760px; color: #665b52; line-height: 1.5; }
      .trace-footer { display: none; margin: 14px 2px 0; color: #665b52; font-size: .92rem; }
      @keyframes riseIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes softPulse { 0% { outline: 0 solid rgba(255,237,213,0); } 24% { outline: 5px solid rgba(255,237,213,.82); } 100% { outline: 0 solid rgba(255,237,213,0); } }
      @keyframes previewGlow { 0% { opacity: 0; transform: translateY(10px); background: rgba(255,247,237,.25); } 36% { opacity: .96; background: rgba(255,237,213,.78); } 100% { opacity: .86; background: rgba(255,237,213,.5); } }
      @keyframes dots { 0% { content: ""; } 25% { content: "."; } 50% { content: ".."; } 75%, 100% { content: "..."; } }
      @media (prefers-reduced-motion: reduce) {
        .chat { scroll-behavior: auto; }
        .new-turn, .answer-preview, .thinking-dots::after { animation: none; }
      }
      @media (max-width: 640px) {
        body { padding: 16px; }
        .brand-lockup { gap: 12px; align-items: center; }
        .brand-logo { width: 112px; height: 112px; object-fit: contain; }
        .room-heading-row { display: grid; gap: 10px; }
        .room-context h2 { white-space: normal; }
        .bubble { max-width: 92%; }
        .agent { max-width: 100%; }
        .dinner-card { padding: 15px; border-radius: 12px; }
        .effort-chip { width: 100%; justify-content: flex-start; }
        form { grid-template-columns: 1fr; padding: 16px; }
        .primary { justify-self: stretch; min-width: 88px; }
        .input-copy { grid-column: 1; }
        .input-helper { font-size: .78rem; }
        .prompt-helper-tabs { margin-bottom: -13px; }
        .helper-tab { flex: 1 1 50%; padding: 10px 9px 11px; font-size: .82rem; }
        .photo-helper-grid { grid-template-columns: 1fr; }
      }
    </style>
  </head>
  <body data-mode="dinner">
    <main>
      <nav class="product-threads" aria-label="1Less product threads">
        <a class="thread active" href="/" aria-current="page">
          <span class="thread-copy">Dinner<small>Decide tonight’s meal</small></span>
        </a>
        <a class="thread" href="/field-pack/">
          <span class="thread-copy">Arya's Field Pack<small>Zoo · aquarium · museum trips</small></span>
        </a>
      </nav>
      <header class="hero">
        <div class="brand-lockup">
          <img class="brand-logo brand-logo-wrap" src="/1LessPrimaryLogo.png?v=transparent-square" alt="1Less logo" width="800" height="800" />
          <div class="brand-copy">
          <p class="tagline">One less thing on your plate.</p>
          <p class="subhead">Tell 1Less what tonight looks like. Get one doable dinner idea — not a recipe rabbit hole.</p>
          <p class="alpha-note"><strong>Dinner-only alpha</strong></p>
          </div>
        </div>
      </header>
      <section class="shell">
        <div class="tab-panel" id="active-panel" role="region" aria-label="Dinner-only alpha">
          <section class="room-context" data-room-context>
            <div class="room-heading-row">
              <h2 id="roomHeadline">Start with tonight.</h2>
            </div>
            <p id="roomDescription">What do you have, who needs to eat, and how much effort can dinner take?</p>
          </section>
          <form id="form" class="prompt-card">
            <div class="input-copy">
              <label class="prompt-label" for="message">Start with tonight</label>
              <textarea id="message" rows="3" autocomplete="off" aria-describedby="inputHelper inputNudge" placeholder="Let’s decide dinner. Steer me with some details?"></textarea>
              <p class="input-helper" id="inputHelper"><span class="input-helper-lead">Food, time, energy, picky kids, avoidances — messy is fine.</span></p>
            </div>
            <div class="prompt-helper-tabs" role="tablist" aria-label="Prompt helper tabs">
              <button class="helper-tab active" id="samplePromptToggle" type="button" role="tab" aria-selected="true" aria-expanded="true" aria-controls="samplePromptPanel">Use a sample night</button>
              <button class="helper-tab" id="photoPromptToggle" type="button" role="tab" aria-selected="false" aria-expanded="false" aria-controls="photoPromptPanel" tabindex="-1">Use photo to fill prompt</button>
            </div>
            <section class="helper-panel" id="samplePromptPanel" role="tabpanel" aria-labelledby="samplePromptToggle" aria-label="Sample nights that fill the prompt">
              <p>Pick one to fill the box, then edit anything before submitting.</p>
              <div class="example-chips" aria-label="Example dinner prompts">
                <button class="example-chip" type="button" data-prompt="10 minutes, rice, frozen peas, picky kid, not in the mood to cook.">10 min, rice + peas</button>
                <button class="example-chip" type="button" data-prompt="Tortillas, eggs, cheese, 20 minutes, low cleanup.">Tortillas, eggs, low cleanup</button>
                <button class="example-chip" type="button" data-prompt="Leftover rice, frozen peas, no store run, need one easy dinner.">Leftover rice, no store run</button>
                <button class="example-chip hidden" type="button" data-extra-prompt data-prompt="Frozen nuggets, tortillas, bagged salad, picky kid, make it feel like dinner.">Nuggets, tortillas, salad kit</button>
                <button class="example-chip hidden" type="button" data-extra-prompt data-prompt="Ground turkey, pasta, jar sauce, 25 minutes, one pan if possible.">Turkey, pasta, one pan</button>
                <button class="example-chip hidden" type="button" data-extra-prompt data-prompt="Canned beans, rice, cheese, avocado, cheap and filling.">Beans, rice, filling</button>
                <button class="example-chip hidden" type="button" data-extra-prompt data-prompt="Chicken thighs, potatoes, tired but can wait 35 minutes.">Chicken, potatoes, hands-off</button>
                <button class="example-chip hidden" type="button" data-extra-prompt data-prompt="Paneer or tofu, frozen veggies, rice, mild spice, kid-friendly.">Paneer/tofu, rice, mild</button>
                <button class="example-chip hidden" type="button" data-extra-prompt data-prompt="Leftover takeout rice, eggs, peas, need low cleanup.">Takeout rice, eggs, peas</button>
                <button class="example-chip hidden" type="button" data-extra-prompt data-prompt="Nothing thawed, rice, frozen peas, canned beans, everyone is hungry.">Pantry/freezer only</button>
              </div>
              <button class="example-expand" id="showMorePrompts" type="button" aria-expanded="false">Show 7 more ready-made prompts</button>
            </section>
            <section class="helper-panel hidden" id="photoPromptPanel" role="tabpanel" aria-labelledby="photoPromptToggle" aria-label="Photo prompt helper">
              <p id="photoTrustNote">Photo is only used to draft this dinner prompt. Edit anything it gets wrong. No pantry memory yet — just tonight’s prompt.</p>
              <div class="photo-helper-grid">
                <input id="photoPromptInput" type="file" accept="image/*" aria-describedby="photoTrustNote" />
                <select id="photoPromptSource" aria-label="What is this photo?">
                  <option value="fridge">Fridge</option>
                  <option value="pantry">Pantry</option>
                  <option value="freezer">Freezer</option>
                  <option value="counter">Counter / leftovers</option>
                  <option value="grocery_bag">Grocery bag</option>
                  <option value="receipt">Grocery receipt</option>
                  <option value="unsure">Not sure</option>
                </select>
                <button id="photoDraftButton" type="button">Draft prompt</button>
              </div>
            </section>
            <button class="primary" id="submitButton" type="submit">Get one dinner idea</button>
            <p class="input-nudge hidden" id="inputNudge" aria-live="polite"></p>
          </form>
          <div id="chat" class="chat" aria-live="polite">
            <section class="empty-state" id="emptyState" aria-label="Start dinner idea">
              <h3>No dinner idea yet.</h3>
              <p>Your editable prompt is above. Sample nights and photos only help fill it — you still choose when to submit.</p>
            </section>
          </div>
        </div>
      </section>
      <section class="vision-note" aria-labelledby="why-dinner-first">
        <h2 id="why-dinner-first">Why start with dinner?</h2>
        <p>Because dinner is often the chore before the chore. 1Less starts by removing just that one decision: a practical default you can use or tweak. For now, it only handles dinner.</p>
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
      const inputNudge = document.querySelector("#inputNudge");
      const submitButton = document.querySelector("#submitButton");
      const samplePromptToggle = document.querySelector("#samplePromptToggle");
      const samplePromptPanel = document.querySelector("#samplePromptPanel");
      const photoPromptToggle = document.querySelector("#photoPromptToggle");
      const photoPromptPanel = document.querySelector("#photoPromptPanel");
      const photoPromptInput = document.querySelector("#photoPromptInput");
      const photoPromptSource = document.querySelector("#photoPromptSource");
      const photoDraftButton = document.querySelector("#photoDraftButton");
      const emptyState = document.querySelector("#emptyState");
      const traceToggle = document.querySelector("#traceToggle");
      const roomHeadline = document.querySelector("#roomHeadline");
      const roomDescription = document.querySelector("#roomDescription");
      const tabPanel = document.querySelector("#active-panel");
      let answerPreviewBubble = null;
      let answerPreviewRequestId = 0;
      const rooms = {
        dinner: {
          title: "Dinner",
          summary: "Start with tonight.",
          headline: "Start with tonight.",
          description: "What do you have, who needs to eat, and how much effort can dinner take?",
        }
      };
      const inputCopyByState = {
        start: {
          placeholder: "Let’s decide dinner. Steer me with some details?",
          helper: "Food, time, energy, picky kids, avoidances — messy is fine.",
          mobilePlaceholder: "Let’s decide dinner. What matters tonight?",
          mobileHelper: "Food, time, energy, picky kids, avoidances."
        },
        recommendation: {
          placeholder: "Need it easier or more kid-proof?",
          helper: "Try: “too much work,” “kid won’t eat this,” “missing ingredient,” or “give me backup.”",
          mobilePlaceholder: "Need it easier or more kid-proof?",
          mobileHelper: "Try: too much work, kid won’t eat, missing ingredient, backup."
        },
        fallback: {
          placeholder: "Good enough, or one more tweak?",
          helper: "Say what failed — too much cleanup, missing ingredient, picky kid, or not in the mood.",
          mobilePlaceholder: "Good enough, or one more tweak?",
          mobileHelper: "Say what failed: cleanup, ingredient, picky kid, mood."
        }
      };
      let inputCopyState = "start";

      function setRoom(active) {
        activeMode = "dinner";
        const room = rooms.dinner;
        document.body.dataset.mode = activeMode;
        roomHeadline.textContent = room.headline;
        roomDescription.textContent = room.description;
        updateInputCopy(inputCopyState);
        tabPanel.setAttribute("aria-label", "Dinner-only alpha");
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
        submitButton.textContent = state === "start" ? "Get one dinner idea" : "Adjust idea";
        autoGrowInput();
        clearInputNudge();
      }

      function autoGrowInput() {
        input.style.height = "auto";
        const styles = window.getComputedStyle(input);
        const lineHeight = Number.parseFloat(styles.lineHeight) || 22;
        const maxHeight = lineHeight * 10 + 28;
        const nextHeight = Math.min(input.scrollHeight, maxHeight);
        input.style.height = `${nextHeight}px`;
        input.style.overflowY = input.scrollHeight > maxHeight ? "auto" : "hidden";
      }

      function fillPromptDraft(text, source) {
        input.value = text;
        answerPreviewRequestId += 1;
        removeAnswerPreview();
        autoGrowInput();
        clearInputNudge();
        showInputNudge("Edit anything I got wrong before submitting.");
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
        trackEvent("prompt_helper_filled", { source: source || "unknown" });
      }

      function activateHelperTab(tabName) {
        const sampleActive = tabName === "sample";
        samplePromptPanel.classList.toggle("hidden", !sampleActive);
        photoPromptPanel.classList.toggle("hidden", sampleActive);
        samplePromptToggle.classList.toggle("active", sampleActive);
        photoPromptToggle.classList.toggle("active", !sampleActive);
        samplePromptToggle.setAttribute("aria-selected", String(sampleActive));
        photoPromptToggle.setAttribute("aria-selected", String(!sampleActive));
        samplePromptToggle.setAttribute("aria-expanded", String(sampleActive));
        photoPromptToggle.setAttribute("aria-expanded", String(!sampleActive));
        samplePromptToggle.tabIndex = sampleActive ? 0 : -1;
        photoPromptToggle.tabIndex = sampleActive ? -1 : 0;
      }

      function photoPromptDraft(source) {
        const drafts = {
          fridge: { label: "fridge", likely: ["eggs", "tortillas", "leftover rice", "frozen peas", "cheese"], maybe: ["yogurt", "carrots", "salsa"] },
          pantry: { label: "pantry", likely: ["rice", "pasta", "canned beans", "tortillas", "jar sauce"], maybe: ["crackers", "broth", "tuna"] },
          freezer: { label: "freezer", likely: ["frozen peas", "frozen veggies", "nuggets", "flatbread", "rice"], maybe: ["dumplings", "frozen fruit"] },
          counter: { label: "counter/leftovers", likely: ["leftover rice", "tortillas", "cut vegetables", "fruit", "bread"], maybe: ["takeout leftovers", "cheese"] },
          grocery_bag: { label: "grocery bag", likely: ["eggs", "tortillas", "cheese", "bagged salad", "berries"], maybe: ["yogurt", "avocado"] },
          receipt: { label: "grocery receipt", likely: ["eggs", "tortillas", "cheese", "bagged salad", "rice"], maybe: ["berries", "yogurt"] },
          unsure: { label: "photo", likely: ["eggs", "tortillas", "rice", "peas", "cheese"], maybe: ["yogurt", "carrots", "salsa"] }
        };
        const draft = drafts[source] || drafts.unsure;
        return `Help me decide dinner tonight. From this ${draft.label} photo, I think I can use: ${draft.likely.join(", ")}. Maybe available: ${draft.maybe.join(", ")}. Ignore anything that seems wrong. I need something low-effort.`;
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

      function removeAnswerPreview() {
        if (answerPreviewBubble && answerPreviewBubble.parentNode) {
          answerPreviewBubble.remove();
        }
        answerPreviewBubble = null;
      }

      function renderAnswerPreview(text) {
        if (!text) {
          removeAnswerPreview();
          return null;
        }
        if (!answerPreviewBubble || answerPreviewBubble.parentNode !== chat) {
          answerPreviewBubble = document.createElement("div");
          answerPreviewBubble.className = "bubble answer-preview";
          answerPreviewBubble.setAttribute("aria-label", "Dinner idea preview");
          placeChatNode(answerPreviewBubble);
        }
        const previewText = document.createElement("span");
        previewText.className = "answer-preview-text";
        previewText.textContent = text;
        const helper = document.createElement("span");
        helper.className = "answer-preview-helper";
        helper.textContent = "This is just a preview — press Get one dinner idea for the full plan, or choose another pill to preview a different starting point.";
        answerPreviewBubble.replaceChildren(previewText, helper);
        scrollTurnIntoView(answerPreviewBubble, "smooth");
        return answerPreviewBubble;
      }

      async function previewDinnerIdea(message) {
        const requestId = ++answerPreviewRequestId;
        renderAnswerPreview("Checking one dinner idea…");
        try {
          const data = await postJson("/api/preview", { message, mode: activeMode });
          if (requestId !== answerPreviewRequestId || input.value.trim() !== message) return;
          renderAnswerPreview(data.preview);
        } catch (error) {
          if (requestId === answerPreviewRequestId) removeAnswerPreview();
          console.error(error);
        }
      }

      function stripTrailingPeriod(text) {
        return text.replace(/[.]$/, "");
      }

      function cleanSentence(text) {
        const clean = text.trim().replace(/^and\\s+/i, "");
        if (!clean) return "";
        const capitalized = clean.charAt(0).toUpperCase() + clean.slice(1);
        return /[.!?]$/.test(capitalized) ? capitalized : `${capitalized}.`;
      }

      function splitDinnerPlan(planText) {
        const clean = planText.trim();
        if (!clean) return [];
        const sentenceParts = clean.split(/(?<=[.!?])\\s+/).map(cleanSentence).filter(Boolean);
        if (sentenceParts.length > 1) return sentenceParts.slice(0, 3);
        const parts = stripTrailingPeriod(clean).split(/,\\s+/).map(cleanSentence).filter(Boolean);
        if (parts.length <= 3) return parts;
        return [parts[0], parts[1], cleanSentence(parts.slice(2).join(" "))];
      }

      function splitReasonItems(text) {
        return stripTrailingPeriod(text).split(/;\\s+/).map(cleanSentence).filter(Boolean);
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
            parsed.why.push(...splitReasonItems(line.replace("Why this is easier:", "").trim()));
          } else if (line.startsWith("Why it fits:")) {
            parsed.why.push(...splitReasonItems(line.replace("Why it fits:", "").trim()));
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
        return parts.map((part, index) => index === 0 ? `⏱ ${part}` : cleanSentence(part).replace(/[.]$/, ""));
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
          ${(parsed.why.length || parsed.details.length) ? `<section class="dinner-section" aria-label="Why this fits"><h4>Why this fits</h4><ul class="detail-list">${parsed.why.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}${parsed.details.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul></section>` : ""}
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

      function renderCompletion(response, options = {}) {
        const div = document.createElement("div");
        div.className = `completion${options.isNewTurn ? " new-turn" : ""}`;
        div.textContent = "Good enough counts. Dinner decided — one less thing.";
        placeChatNode(div, options.replaceNode);
        scrollTurnIntoView(options.turnStart || div, options.behavior || "smooth");
        return div;
      }

      function clearInputNudge() {
        inputNudge.textContent = "";
        inputNudge.classList.add("hidden");
      }

      function showInputNudge(message) {
        inputNudge.textContent = message;
        inputNudge.classList.remove("hidden");
      }

      function renderResponse(response, options = {}) {
        const isDinnerDecision = response.metadata && response.metadata.chapter === "chapter_1_dinner_decision";
        const turnStart = options.turnStart || null;
        if (response.context) addBubble("agent", `Context: ${response.context}`, { turnStart });
        const parentBubble = options.skipParent ? turnStart : addBubble("parent", response.parent_message, { isNewTurn: true });
        if (isDinnerDecision && response.metadata && response.metadata.accepted) {
          renderCompletion(response, { replaceNode: options.replaceNode, turnStart: parentBubble || turnStart, isNewTurn: true });
        } else if (isDinnerDecision) {
          renderDinnerCard(response, { replaceNode: options.replaceNode, turnStart: parentBubble || turnStart, isNewTurn: true });
        } else {
          addBubble("agent", response.message, { replaceNode: options.replaceNode, turnStart: parentBubble || turnStart, isNewTurn: true });
        }
        addTrace(response.trace);
        scrollTurnIntoView(parentBubble || turnStart, "smooth");
        if (isDinnerDecision && response.metadata && response.metadata.accepted) {
          updateInputCopy("start");
          document.querySelectorAll(".feedback-actions").forEach((node) => node.remove());
        } else if (isDinnerDecision) {
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
        if (!message) {
          showInputNudge("Give me a few details first — even “tired, 15 minutes, picky kid” is enough.");
          input.focus();
          return;
        }
        clearInputNudge();
        if (emptyState) emptyState.remove();
        document.querySelectorAll(".feedback-actions").forEach((node) => node.remove());
        removeAnswerPreview();
        input.value = "";
        autoGrowInput();
        chat.setAttribute("aria-busy", "true");
        const parentBubble = addBubble("parent", message, { isNewTurn: true });
        const thinkingBubble = addThinkingBubble(parentBubble);
        try {
          const data = await postJson("/api/chat", { session_id: sessionId, message, mode: activeMode });
          sessionId = data.session_id;
          renderResponse(data.response, { skipParent: true, turnStart: parentBubble, replaceNode: thinkingBubble });
        } catch (error) {
          addBubble("agent", "Something hiccuped. Try once more.", { replaceNode: thinkingBubble, turnStart: parentBubble, isNewTurn: true });
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

      samplePromptToggle.addEventListener("click", () => {
        activateHelperTab("sample");
      });

      photoPromptToggle.addEventListener("click", () => {
        activateHelperTab("photo");
      });

      document.querySelector(".prompt-helper-tabs").addEventListener("keydown", (event) => {
        if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
        event.preventDefault();
        const nextTab = samplePromptToggle.getAttribute("aria-selected") === "true" ? photoPromptToggle : samplePromptToggle;
        activateHelperTab(nextTab === samplePromptToggle ? "sample" : "photo");
        nextTab.focus();
      });

      document.addEventListener("click", (event) => {
        const button = event.target.closest("#showMorePrompts");
        if (!button) return;
        document.querySelectorAll("[data-extra-prompt]").forEach((node) => node.classList.remove("hidden"));
        button.setAttribute("aria-expanded", "true");
        button.classList.add("hidden");
      });

      document.addEventListener("click", (event) => {
        const button = event.target.closest("[data-prompt]");
        if (!button) return;
        fillPromptDraft(button.dataset.prompt, "sample");
      });

      function fillPhotoPromptDraft() {
        if (!photoPromptInput.files || !photoPromptInput.files.length) {
          showInputNudge("Choose or take a photo first — then I’ll draft editable prompt text from it.");
          photoPromptInput.focus();
          return;
        }
        fillPromptDraft(photoPromptDraft(photoPromptSource.value), "photo");
      }

      photoPromptInput.addEventListener("change", fillPhotoPromptDraft);
      photoPromptSource.addEventListener("change", () => {
        if (photoPromptInput.files && photoPromptInput.files.length) {
          fillPromptDraft(photoPromptDraft(photoPromptSource.value), "photo_source_change");
        }
      });
      photoDraftButton.addEventListener("click", fillPhotoPromptDraft);

      input.addEventListener("input", () => {
        answerPreviewRequestId += 1;
        removeAnswerPreview();
        autoGrowInput();
      });

      window.addEventListener("resize", () => {
        updateInputCopy(inputCopyState);
        autoGrowInput();
      });

      activateHelperTab("sample");
      autoGrowInput();

      traceToggle.addEventListener("change", () => {
        chat.classList.toggle("show-trace", traceToggle.checked);
      });
    </script>
  </body>
</html>
"""


def _cookie_values(cookie_header: str | None) -> dict[str, str]:
    cookies: dict[str, str] = {}
    if not cookie_header:
        return cookies
    for item in cookie_header.split(";"):
        if "=" not in item:
            continue
        name, value = item.split("=", 1)
        cookies[name.strip()] = value.strip()
    return cookies


def _analytics_disabled(cookie_header: str | None) -> bool:
    return _cookie_values(cookie_header).get(ANALYTICS_COOKIE) == ANALYTICS_OFF_VALUE


def _html_for_request(cookie_header: str | None) -> str:
    snippet = "" if _analytics_disabled(cookie_header) else GA4_SNIPPET
    return HTML.replace("{ga4_snippet}", snippet)


def _analytics_cookie_header(value: str, host_header: str | None, *, max_age: int) -> str:
    parts = [f"{ANALYTICS_COOKIE}={value}", f"Max-Age={max_age}", "Path=/", "SameSite=Lax", "HttpOnly"]
    host = (host_header or "").split(":", 1)[0].lower()
    if host == "1less.app" or host.endswith(".1less.app"):
        parts.insert(2, "Domain=1less.app")
    return "; ".join(parts)


def _image_content_type(path: Path) -> str:
    if path.suffix == ".svg":
        return "image/svg+xml"
    if path.suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if path.suffix == ".png":
        return "image/png"
    if path.suffix == ".webp":
        return "image/webp"
    if path.suffix == ".gif":
        return "image/gif"
    return "application/octet-stream"


def _static_content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return "text/html; charset=utf-8"
    if suffix == ".css":
        return "text/css; charset=utf-8"
    if suffix == ".js":
        return "application/javascript; charset=utf-8"
    if suffix == ".json":
        return "application/json; charset=utf-8"
    if suffix == ".svg":
        return "image/svg+xml"
    if suffix in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return _image_content_type(path)
    if suffix == ".ico":
        return "image/x-icon"
    if suffix == ".map":
        return "application/json; charset=utf-8"
    return "application/octet-stream"


def _safe_field_pack_path(url_path: str) -> Path | None:
    """Resolve /field-pack/... to a file under FIELD_PACK_ROOT, or None."""
    if url_path != FIELD_PACK_PREFIX and not url_path.startswith(FIELD_PACK_PREFIX + "/"):
        return None
    if not FIELD_PACK_ROOT.is_dir():
        return None
    rest = unquote(url_path[len(FIELD_PACK_PREFIX) :]).lstrip("/")
    # Block sneaky path segments early
    if ".." in Path(rest).parts:
        return None
    candidate = FIELD_PACK_ROOT / (rest if rest else "index.html")
    try:
        root = FIELD_PACK_ROOT.resolve()
        resolved = candidate.resolve()
        resolved.relative_to(root)
    except (OSError, ValueError):
        return None
    if resolved.is_dir():
        resolved = (resolved / "index.html").resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            return None
    if not resolved.is_file():
        return None
    return resolved


def _dinner_preview_text(message_text: str) -> str:
    lines = [line.strip() for line in message_text.splitlines() if line.strip()]
    preview_lines = lines[:3]
    return "\n".join(preview_lines)


class WebHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/analytics/off":
            self._handle_analytics_toggle(enabled=False)
            return
        if path == "/analytics/on":
            self._handle_analytics_toggle(enabled=True)
            return
        if path == "/analytics/status":
            self._handle_analytics_status()
            return
        asset_path = LOGO_ASSETS.get(path.lstrip("/"))
        if asset_path is not None:
            if not asset_path.exists():
                self.send_error(404)
                return
            self._send_binary(asset_path.read_bytes(), _image_content_type(asset_path))
            return
        field_pack_file = _safe_field_pack_path(path)
        if field_pack_file is not None:
            self._send_binary(field_pack_file.read_bytes(), _static_content_type(field_pack_file))
            return
        if path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        self._send_text(_html_for_request(self.headers.get("Cookie")), "text/html; charset=utf-8")

    def do_HEAD(self) -> None:
        path = urlsplit(self.path).path
        asset_path = LOGO_ASSETS.get(path.lstrip("/"))
        field_pack_file = _safe_field_pack_path(path)
        if path not in {"/", "/index.html"} and asset_path is None and field_pack_file is None:
            self.send_error(404)
            return
        if asset_path is not None:
            content_type = _image_content_type(asset_path)
            length = asset_path.stat().st_size if asset_path.exists() else 0
        elif field_pack_file is not None:
            content_type = _static_content_type(field_pack_file)
            length = field_pack_file.stat().st_size
        else:
            content_type = "text/html; charset=utf-8"
            length = len(_html_for_request(self.headers.get("Cookie")).encode("utf-8"))
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.end_headers()

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/chat":
            self._handle_chat()
            return
        if path == "/api/preview":
            self._handle_preview()
            return
        if path == "/api/scenario":
            self._handle_scenario()
            return
        self.send_error(404)

    def _handle_analytics_toggle(self, *, enabled: bool) -> None:
        if enabled:
            cookie = _analytics_cookie_header("on", self.headers.get("Host"), max_age=0)
            status = "included"
            body = "Google Analytics included for this browser. Visit /analytics/off to exclude testing again."
        else:
            cookie = _analytics_cookie_header(ANALYTICS_OFF_VALUE, self.headers.get("Host"), max_age=31_536_000)
            status = "excluded"
            body = "Google Analytics excluded for this browser. Visit /analytics/on to include traffic again."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Set-Cookie", cookie)
        self.send_header("X-Analytics-Status", status)
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _handle_analytics_status(self) -> None:
        disabled = _analytics_disabled(self.headers.get("Cookie"))
        status = "excluded" if disabled else "included"
        body = f"Google Analytics {status} for this browser. Use /analytics/off to exclude testing or /analytics/on to include traffic."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("X-Analytics-Status", status)
        self.send_header("Content-Length", str(len(body.encode("utf-8"))))
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

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

    def _handle_preview(self) -> None:
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
        message = (payload.get("message") or "").strip()
        if not message:
            self.send_error(400, "Missing message")
            return

        response = create_dinner_decision_session().send(message)
        self._send_json({"preview": _dinner_preview_text(response["message"]), "response": response})

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
