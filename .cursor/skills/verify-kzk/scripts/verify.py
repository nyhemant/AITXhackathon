#!/usr/bin/env python3
"""verify-kzk: drive KZK (kidzookit.com) like a tired parent on a phone (390x844) and a desktop (1280x800).

Locators only for waits (no wait_for_function string predicates: the site CSP has no 'unsafe-eval').
Analytics opt-out on every request: cookie one_less_analytics=off, ?notrack=1, UA containing kz-verify.

  python verify.py --out DIR                       # all journeys, phone + desktop
  python verify.py --only j2,j4 --out DIR          # some journeys
  python verify.py --only j5 --real-signup --out DIR   # ONE real test signup to nyhemant+kzkverify-<stamp>@gmail.com
Exit 1 when any check FAILs. Evidence: DIR/results.json + DIR/*.png.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import Error as PWError
from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

DOMAIN = "kidzookit.com"
UA_SUFFIX = "KidZooKitCheck/1.0; kz-verify"
CHROME = "/usr/bin/google-chrome"
# Approved copy pinned here. Title/meta/H1 are frozen through 2026-11-24; change only with Heymant's yes.
START_H1 = "Printable scavenger hunts for your next zoo, aquarium or museum trip"
WORDMARK = "Arya’s Wildlife Project"
CONTACT = "mailto:ask@kidzookit.com"
QR_DESTS = {  # printed QR codes: these must answer 200 forever (301 only if a page moves)
    "scavenger-hunt": "/field-pack/zoos/?utm_source=printable&utm_medium=qr&utm_campaign=scavenger-hunt",
    "park-scavenger-hunt": "/field-pack/?utm_source=printable&utm_medium=qr&utm_campaign=park-scavenger-hunt",
    "animal-bingo": "/field-pack/cards/?utm_source=printable&utm_medium=qr&utm_campaign=animal-bingo",
    "carpool": "/start/?utm_source=printable&utm_medium=qr&utm_campaign=carpool",
    "teacher-handout": "/field-pack/virtual-field-trip/?utm_source=printable&utm_medium=qr&utm_campaign=teacher-handout",
    "zoo-day-journal": "/field-pack/cards/?utm_source=printable&utm_medium=qr&utm_campaign=zoo-day-journal",
    "chaperone-card": "/field-pack/?utm_source=printable&utm_medium=qr&utm_campaign=chaperone-card",
}
VIEWPORTS = {
    "phone": dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2),
    "desktop": dict(viewport={"width": 1280, "height": 800}),
}
# window.print is replaced (before any page script) by a counter on <html data-kzv-printed>,
# so "Print" is proven without a dialog. Injected over CDP, so the CSP does not apply.
PRINT_SPY = (
    "window.print=function(){var h=document.documentElement;"
    "h.setAttribute('data-kzv-printed',String((+h.getAttribute('data-kzv-printed')||0)+1));};"
)
BANNED_COPY = re.compile(r"\b(free|no-cost)\b", re.I)


class Run:
    def __init__(self, base: str, out: Path):
        self.base = base.rstrip("/")
        self.out = out
        self.rows: list[dict] = []

    def check(self, j, vp, name, ok, detail="", warn=False):
        status = "PASS" if ok else ("WARN" if warn else "FAIL")
        row = {"journey": j, "viewport": vp, "check": name, "status": status, "detail": " ".join(str(detail).split())[:400]}
        self.rows.append(row)
        print(f"{status:4} {j:3} {vp:7} {name}  {row['detail'][:160]}", flush=True)
        return ok

    def url(self, path: str) -> str:
        u = path if path.startswith("http") else self.base + path
        p = urlsplit(u)
        q = (p.query + "&" if p.query else "") + "notrack=1"
        return f"{p.scheme}://{p.netloc}{p.path}?{q}" + (f"#{p.fragment}" if p.fragment else "")


class Page:
    """One tab with error and off-site request capture."""

    def __init__(self, run: Run, ctx, vp: str):
        self.run, self.vp = run, vp
        self.pg = ctx.new_page()
        self.errors: list[str] = []
        self.offsite: set[str] = set()
        self.pg.on("pageerror", lambda e: self.errors.append(f"pageerror: {e}"))
        self.pg.on("console", lambda m: self.errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        self.pg.on("request", self._req)

    def _req(self, req):
        host = urlsplit(req.url).hostname or ""
        if req.url.startswith(("data:", "blob:")) or host in ("", DOMAIN, "127.0.0.1", "localhost"):
            return
        self.offsite.add(host)

    def go(self, path, wait="networkidle"):
        resp = self.pg.goto(self.run.url(path), wait_until=wait, timeout=45000)
        self.pg.wait_for_timeout(600)
        return resp

    def act(self, loc):
        loc.scroll_into_view_if_needed(timeout=8000)
        if self.vp == "phone":
            loc.tap(timeout=8000)
        else:
            loc.click(timeout=8000)

    def shot(self, name):
        try:
            self.pg.screenshot(path=str(self.run.out / f"{name}-{self.vp}.png"))
        except PWError:
            pass

    def overflow(self) -> int:
        return int(self.pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"))

    def hygiene(self, j, label):
        r, vp = self.run, self.vp
        real = [e for e in self.errors if "cloudflareinsights" not in e and "Permissions-Policy" not in e]
        r.check(j, vp, f"{label}: no JS errors", not real, real[:3])
        cf = [e for e in self.errors if "cloudflareinsights" in e]
        if cf:
            r.check(j, vp, f"{label}: Cloudflare beacon noise", False, cf[:2], warn=True)
        off = sorted(h for h in self.offsite if not h.endswith("youtube-nocookie.com"))
        r.check(j, vp, f"{label}: no off-site requests", not off, off[:6], warn=bool(off))
        ov = self.overflow()
        r.check(j, vp, f"{label}: no sideways scroll", ov <= 1, f"overflow={ov}px")
        self.errors.clear()
        self.offsite.clear()


def visible_text(pg) -> str:
    return pg.locator("body").inner_text(timeout=10000)


# ---------------------------------------------------------------- journeys
def j1_landing(run: Run, ctx, vp):
    """Front door: / -> /start/, approved H1 + wordmark, print path above the fold, demo sheet link."""
    p = Page(run, ctx, vp)
    resp = p.go("/")
    pg = p.pg
    run.check("j1", vp, "/ lands on /start/", urlsplit(pg.url).path == "/start/" and resp and resp.status == 200, pg.url)
    h1 = pg.locator("h1")
    run.check("j1", vp, "one H1, approved text", h1.count() == 1 and h1.first.inner_text().strip() == START_H1, h1.all_inner_texts())
    wm = pg.locator(".start-wordmark")
    run.check("j1", vp, "wordmark 'Arya’s Wildlife Project' visible", wm.count() > 0 and wm.first.is_visible() and WORDMARK in wm.first.inner_text(), wm.all_inner_texts()[:1])
    fold = VIEWPORTS[vp]["viewport"]["height"]
    if vp == "phone":  # phones get a button; desktop shows the map with a "Tap a pin to print" hint
        cta = pg.get_by_role("link", name="Print a scavenger hunt")
        bb = cta.first.bounding_box() if cta.count() else None
        run.check("j1", vp, "'Print a scavenger hunt' above the fold", bool(bb) and bb["y"] + bb["height"] <= fold, bb)
    else:
        hint = pg.get_by_text("Tap a pin to print")
        bb = hint.first.bounding_box() if hint.count() else None
        run.check("j1", vp, "'Tap a pin to print' + map above the fold", bool(bb) and bb["y"] + bb["height"] <= fold, bb)
    demo = pg.locator('a.hxd-sheet[data-kz-cta="home-demo"]')
    href = demo.first.get_attribute("href") if demo.count() else None
    run.check("j1", vp, "demo sheet links to a printable hunt", bool(href) and href.endswith("#printable-hunt"), href)
    p.shot("j1-start")
    txt = visible_text(pg)
    bad = sorted(set(m.group(0).lower() for m in BANNED_COPY.finditer(txt)))
    run.check("j1", vp, "no 'free'/'no-cost' in visible copy", not bad, bad)
    mails = sorted(set(a for a in pg.locator("a[href^='mailto:']").evaluate_all("els=>els.map(e=>e.getAttribute('href'))")))
    run.check("j1", vp, "contact is ask@kidzookit.com only", mails == [CONTACT], mails)
    offsite_links = [h for h in pg.locator("a[href^='http']").evaluate_all("els=>els.map(e=>e.href)") if urlsplit(h).hostname != DOMAIN]
    run.check("j1", vp, "all links stay on kidzookit.com", not offsite_links, offsite_links[:5])
    # Tap the demo sheet like a parent would.
    p.act(demo.first)
    pg.wait_for_url(re.compile(r"/field-pack/perot-museum/"), timeout=15000)
    sec = pg.locator("#printable-hunt")
    sec.wait_for(state="visible", timeout=10000)
    run.check("j1", vp, "demo tap opens the hunt section", "printable-hunt" in pg.url and sec.is_visible(), pg.url)
    p.hygiene("j1", "start+demo")
    pg.close()


def j2_pin_to_print(run: Run, ctx, vp):
    """Pin on the /start/ map -> card -> 'Print the scavenger hunt' -> hunt section -> drawer -> Print."""
    p = Page(run, ctx, vp)
    p.go("/start/")
    pg = p.pg
    pins = pg.locator("[data-home-pin]")
    run.check("j2", vp, "map shows place pins", pins.count() >= 10, pins.count())
    # Parents tap the visible label. Some pins are "tag only" and their 44px button box sits under a
    # neighbour, so never tap the button centre (Perot's centre is under Fort Worth Zoo's label).
    pin = pg.locator('[data-home-pin="perot-museum"] .kzm-tag')
    p.act(pin)
    card = pg.locator("#home-pin-card")
    card.wait_for(state="visible", timeout=8000)
    run.check("j2", vp, "pin opens a card naming the place", "Perot Museum" in card.inner_text(), card.inner_text()[:80])
    p.shot("j2-pin-card")
    # Escape closes the card (desktop keyboard; phone uses the Close button).
    if vp == "desktop":
        pg.keyboard.press("Escape")
        card.wait_for(state="hidden", timeout=5000)
        run.check("j2", vp, "Escape closes the pin card", card.is_hidden())
        p.act(pin)
        card.wait_for(state="visible", timeout=8000)
    else:
        close = pg.locator("#home-pin-close")
        p.act(close)
        card.wait_for(state="hidden", timeout=5000)
        run.check("j2", vp, "Close button closes the pin card", card.is_hidden())
        p.act(pin)
        card.wait_for(state="visible", timeout=8000)
    # Multi-place pin lists each place with its own print link.
    dc = pg.locator('[data-home-pin="dc"] .kzm-tag')
    if dc.count():
        p.act(dc)
        pg.wait_for_timeout(400)
        n = card.get_by_role("link", name="Print the scavenger hunt").count()
        run.check("j2", vp, "2-place pin lists 2 print links", n == 2, n)
        p.act(pin)
        pg.wait_for_timeout(400)
    link = card.get_by_role("link", name="Print the scavenger hunt")
    run.check("j2", vp, "card has 'Print the scavenger hunt'", link.count() == 1, link.count())
    p.act(link.first)
    pg.wait_for_url(re.compile(r"/field-pack/perot-museum/"), timeout=15000)
    sec = pg.locator("#printable-hunt")
    sec.wait_for(state="visible", timeout=10000)
    pg.wait_for_timeout(500)
    bb = sec.bounding_box()
    run.check("j2", vp, "lands with the hunt section in view", bb is not None and bb["y"] < VIEWPORTS[vp]["viewport"]["height"] * 0.5, bb)
    stops = sec.locator("ol.kz-scav-list").first.locator("li")
    run.check("j2", vp, "hunt lists its stops (>=8)", stops.count() >= 8, stops.count())
    p.shot("j2-hunt")
    btn = sec.locator("button.kz-scav-print")
    p.act(btn)
    overlay = pg.locator("#mission-overlay")
    overlay.wait_for(state="visible", timeout=10000)
    sheet = pg.locator("#mission-sheet")
    sheet_txt = sheet.inner_text()
    run.check("j2", vp, "print drawer shows the sheet for this place", "Perot Museum" in sheet_txt, sheet_txt[:90])
    p.shot("j2-drawer")
    p.act(pg.locator("#mission-print-btn"))
    pg.locator("html[data-kzv-printed]").wait_for(state="attached", timeout=15000)
    run.check("j2", vp, "Print button opens the print dialog once", pg.locator("html").get_attribute("data-kzv-printed") == "1",
              pg.locator("html").get_attribute("data-kzv-printed"))
    # K4: two quick taps on Print give one dialog (the page guard ignores a second call within 2 s).
    pg.wait_for_timeout(2300)
    before = int(pg.locator("html").get_attribute("data-kzv-printed") or 0)
    pg.evaluate("() => { const b = document.querySelector('#mission-print-btn'); b.click(); b.click(); }")
    pg.wait_for_timeout(1500)
    after = int(pg.locator("html").get_attribute("data-kzv-printed") or 0)
    run.check("j2", vp, "double tap on Print opens one dialog (K4)", after - before == 1, f"{before}->{after}")
    pg.keyboard.press("Escape")
    overlay.wait_for(state="hidden", timeout=5000)
    run.check("j2", vp, "Escape closes the drawer", overlay.is_hidden())
    p.hygiene("j2", "pin+hunt")
    pg.close()


def j3_cards(run: Run, ctx, vp):
    """Animal cards index -> a card -> quick tips + quiz anchor + print."""
    p = Page(run, ctx, vp)
    p.go("/field-pack/cards/")
    pg = p.pg
    links = pg.locator("main a[href*='/field-pack/cards/'][href$='/']")
    run.check("j3", vp, "cards index lists many cards (>=40)", links.count() >= 40, links.count())
    lion = pg.locator("main a[href*='/field-pack/cards/african-lion/']").first
    p.act(lion)
    pg.wait_for_url(re.compile(r"/field-pack/cards/african-lion/"), timeout=15000)
    run.check("j3", vp, "lion card H1", "African lion" in pg.locator("h1").first.inner_text(), pg.locator("h1").all_inner_texts())
    run.check("j3", vp, "quick tips visible", pg.get_by_text("A group of lions is a pride.").first.is_visible())
    tq = pg.get_by_role("link", name="Take the quiz")
    run.check("j3", vp, "'Take the quiz' jumps to #quiz", tq.count() >= 1 and tq.first.get_attribute("href") == "#quiz")
    p.act(tq.first)
    pg.wait_for_timeout(700)
    first_q = pg.locator(".study-choice").first
    qb = first_q.bounding_box()
    run.check("j3", vp, "quiz is on screen after the jump", qb is not None and 0 <= qb["y"] < VIEWPORTS[vp]["viewport"]["height"], qb)
    p.shot("j3-card")
    pb = pg.get_by_role("button", name="Print this card")
    p.act(pb.first)
    pg.locator("html[data-kzv-printed]").wait_for(state="attached", timeout=10000)
    run.check("j3", vp, "'Print this card' opens the print dialog", True)
    p.hygiene("j3", "cards")
    pg.close()


def j4_quiz(run: Run, ctx, vp):
    """Quiz on the lion card: right answer, wrong answer, retry, progress, level switch, show answers."""
    p = Page(run, ctx, vp)
    p.go("/field-pack/cards/african-lion/")
    pg = p.pg
    prog = pg.get_by_text(re.compile(r"^\d+ of \d+ done$"))
    run.check("j4", vp, "progress starts at 0 of 10", prog.first.inner_text().strip() == "0 of 10 done", prog.first.inner_text())
    q1 = pg.locator(".choices").nth(0)
    right = q1.locator(".study-choice[data-choice='A pride']")
    p.act(right)
    pg.wait_for_timeout(300)
    run.check("j4", vp, "right answer marked correct", "is-correct-pick" in (right.get_attribute("class") or ""), right.get_attribute("class"))
    run.check("j4", vp, "progress 1 of 10 after a right answer", prog.first.inner_text().strip() == "1 of 10 done", prog.first.inner_text())
    q2 = pg.locator(".choices").nth(1)
    wrong = q2.locator(".study-choice[data-choice='Grass']")
    p.act(wrong)
    pg.wait_for_timeout(300)
    run.check("j4", vp, "wrong answer marked, kind retry line", "is-wrong-pick" in (wrong.get_attribute("class") or "")
              and pg.get_by_text("Not quite, try another!").first.is_visible(), wrong.get_attribute("class"))
    run.check("j4", vp, "wrong answer does not count as done", prog.first.inner_text().strip() == "1 of 10 done", prog.first.inner_text())
    meat = q2.locator(".study-choice[data-choice='Meat']")
    p.act(meat)
    pg.wait_for_timeout(300)
    run.check("j4", vp, "retry with the right answer counts", prog.first.inner_text().strip() == "2 of 10 done", prog.first.inner_text())
    p.shot("j4-quiz")
    pr = pg.locator(".study-level-btn", has_text="Park Ranger")
    p.act(pr)
    pg.wait_for_timeout(600)
    run.check("j4", vp, "Park Ranger level switches the set", "is-active" in (pr.get_attribute("class") or "") and "level=" in pg.url, pg.url)
    run.check("j4", vp, "new set starts at 0 done", re.match(r"0 of \d+ done", prog.first.inner_text().strip()) is not None, prog.first.inner_text())
    show = pg.locator("[data-study-reveal]:visible").first
    p.act(show)
    pg.wait_for_timeout(400)
    keys = pg.locator(".study-choice.is-correct-key:visible").count()
    run.check("j4", vp, "'Show answers' marks the key and flips to 'Hide answers'", keys >= 5 and show.inner_text().strip() == "Hide answers", f"keys={keys} btn={show.inner_text()!r}")
    p.hygiene("j4", "quiz")
    pg.close()


SIGNUP_ENV = "KZK_LIVE_SIGNUP_APPROVED"


def j5_newsletter(run: Run, ctx, vp, real_signup: bool, stamp: str):
    """Weekly email box on /printables/: errors, privacy line, sample dialog, mocked signup (real signup paused)."""
    p = Page(run, ctx, vp)
    p.go("/printables/")
    pg = p.pg
    form = pg.locator("form.kz-nl").first
    run.check("j5", vp, "weekly email box on /printables/", form.is_visible())
    email = form.locator("input[type='email']")
    msg = form.locator(".kz-nl-msg")
    submit = form.locator(".kz-nl-submit")
    run.check("j5", vp, "privacy line + Privacy link", form.get_by_text("Your email is used only to send this weekly email").is_visible()
              and form.get_by_role("link", name="Privacy").is_visible())
    hp = form.locator("input[name='website']")
    hb = hp.bounding_box() if hp.count() == 1 else None
    run.check("j5", vp, "honeypot off-screen, not tabbable, no autofill", bool(hb) and hb["x"] + hb["width"] <= 0
              and hp.get_attribute("tabindex") == "-1" and hp.get_attribute("autocomplete") == "off", hb)
    # Empty submit: must explain, never call it a success.
    p.act(submit)
    msg.filter(has_text=re.compile(r"\S")).wait_for(timeout=10000)
    run.check("j5", vp, "empty submit shows a fix-it message", "look quite right" in msg.inner_text() and email.get_attribute("aria-invalid") == "true", msg.inner_text())
    email.fill("not-an-email")
    p.act(submit)
    pg.wait_for_timeout(1200)
    run.check("j5", vp, "bad address shows a fix-it message", "look quite right" in msg.inner_text(), msg.inner_text())
    p.errors[:] = [e for e in p.errors if "status of 400" not in e]  # the two deliberate bad posts answer 400
    # Sample email dialog opens, Escape closes, focus returns to the link.
    sample = form.locator("a.kz-nl-sample")
    p.act(sample)
    dlg = pg.locator("dialog.kz-nl-dialog")
    dlg.wait_for(state="visible", timeout=8000)
    dlg.locator("#kz-sample-email, article").first.wait_for(timeout=8000)
    run.check("j5", vp, "sample email dialog opens with the sample", dlg.is_visible())
    p.shot("j5-sample")
    pg.keyboard.press("Escape")
    dlg.wait_for(state="hidden", timeout=5000)
    focused = pg.locator("a.kz-nl-sample:focus").count()
    run.check("j5", vp, "Escape closes the sample, focus back on the link", dlg.is_hidden() and focused == 1, f"focused={focused}")
    if not real_signup:
        # Default: the signup step is MOCKED in the browser. /api/newsletter is answered by page.route, so nothing
        # reaches the server or Kit and no email can go out (owner rule 2026-11-18: no live signups).
        hits = []
        def fake(body):
            def handler(route):
                hits.append(route.request.url)
                route.fulfill(status=200, content_type="application/json", body=json.dumps(body))
            return handler
        guard_url = "https://app.kit.com/forms/guards/mock-0000-test"
        pg.route("**/api/newsletter*", fake({"ok": False, "error": "verify", "verify_url": guard_url}))
        email.fill("mock-only@example.invalid")
        p.act(submit)
        msg.filter(has_text="One more step").wait_for(timeout=10000)
        link = msg.locator("a.kz-nl-verify")
        run.check("j5", vp, "mocked robot-check reply shows Kit's check link (no request left the browser)",
                  link.count() == 1 and link.get_attribute("href") == guard_url and link.get_attribute("target") == "_blank"
                  and "noopener" in (link.get_attribute("rel") or "") and email.is_enabled() and submit.is_enabled(), msg.inner_text())
        pg.unroute("**/api/newsletter*")
        pg.route("**/api/newsletter*", fake({"ok": True}))
        p.act(submit)
        msg.filter(has_text="You're in").wait_for(timeout=10000)
        run.check("j5", vp, "mocked success names the confirmation email and locks the box",
                  "Confirm your KidZooKit weekly animal card" in msg.inner_text()
                  and "from KidZooKit" in msg.inner_text()
                  and "You're in" in msg.inner_text()
                  and email.is_disabled() and submit.is_disabled(), msg.inner_text())
        pg.unroute("**/api/newsletter*")
        run.check("j5", vp, "mocked signup: both posts answered in the browser", len(hits) == 2, hits)
        p.shot("j5-mock-signup")
    else:
        addr = f"nyhemant+kzkverify-{stamp}@gmail.com"
        email.fill(addr)
        p.act(submit)
        msg.filter(has_text=re.compile(r"You're|already|wrong|One more step")).wait_for(timeout=20000)
        text = msg.inner_text()
        guard = msg.locator("a.kz-nl-verify")
        if "One more step" in text:
            # Kit quarantined the signup (seen on live 2026-11-18): the box must say so and link Kit's check.
            href = guard.get_attribute("href") if guard.count() else ""
            ok = bool(re.fullmatch(r"https://app\.kit\.com/forms/guards/[A-Za-z0-9-]{8,80}", href or ""))
            run.check("j5", vp, f"real signup {addr}: Kit asked for a robot check, box shows the check link", ok, f"{text} href={href}")
            run.check("j5", vp, "robot-check reply does not lock the box", email.is_enabled() and submit.is_enabled())
            (run.out / "signup.txt").write_text(f"{addr}\nverify {href}\nEXPECT: no email until the check is passed\n")
        else:
            run.check("j5", vp, f"real signup {addr} says check inbox", "Check your inbox to confirm" in text, text)
            run.check("j5", vp, "after signup the form locks", email.is_disabled() and submit.is_disabled())
            (run.out / "signup.txt").write_text(f"{addr}\nsuccess\nEXPECT: exactly 1 confirmation email; check Gmail\n")
        p.shot("j5-signup")
    p.hygiene("j5", "newsletter")
    pg.close()


def j6_print_and_qr(run: Run, ctx, vp):
    """Printable PDFs on /printables/ answer 200 + %PDF; printed QR destinations answer 200."""
    p = Page(run, ctx, vp)
    p.go("/printables/")
    pg = p.pg
    hrefs = sorted(set(pg.locator("a[href$='.pdf']").evaluate_all("els=>els.map(e=>e.href)")))
    run.check("j6", vp, "printables hub links PDFs (>=14)", len(hrefs) >= 14, len(hrefs))
    bad = []
    for h in hrefs:
        r = ctx.request.get(run.url(h), timeout=30000)
        body = r.body()
        if r.status != 200 or body[:4] != b"%PDF" or "pdf" not in r.headers.get("content-type", ""):
            bad.append((h, r.status, r.headers.get("content-type")))
    run.check("j6", vp, f"all {len(hrefs)} PDFs open as PDFs", not bad, bad[:4])
    for name, dest in QR_DESTS.items():
        r = ctx.request.get(run.url(dest), max_redirects=0, timeout=30000)
        run.check("j6", vp, f"QR {name} answers 200", r.status == 200 and "qr-welcome.js" in r.text(), r.status)
    old = ctx.request.get(run.url("/"), max_redirects=0)
    run.check("j6", vp, "/ is a 301 to /start/", old.status == 301 and urlsplit(old.headers.get("location", "")).path == "/start/", (old.status, old.headers.get("location")))
    dup = ctx.request.get(run.url("/field-pack/zoos/index.html?utm_source=kzv"), max_redirects=0)
    run.check("j6", vp, "a directory's /index.html is a 301 to the directory (query kept)",
              dup.status == 301 and dup.headers.get("location", "").endswith("/field-pack/zoos/?utm_source=kzv"),
              (dup.status, dup.headers.get("location")))
    pg.close()


def j7_trust(run: Run, ctx, vp):
    """About/privacy/404/newsletter pages: calm, honest, on-domain, security headers."""
    p = Page(run, ctx, vp)
    pg = p.pg
    resp = p.go("/about/")
    run.check("j7", vp, "/about/ keeps 'Arya’s Wildlife Project'", resp.status == 200 and "Arya" in visible_text(pg))
    resp = p.go("/privacy/")
    t = visible_text(pg)
    run.check("j7", vp, "/privacy/ names the contact address", resp.status == 200 and "ask@kidzookit.com" in t)
    run.check("j7", vp, "/privacy/ covers the weekly email", "email" in t.lower() and ("unsubscribe" in t.lower() or "Kit" in t))
    run.check("j7", vp, "/privacy/ names the KidZooKit sender and no longer mentions a robot check",
              "“KidZooKit” at ask@kidzookit.com" in t and "reCAPTCHA" not in t and "robot check" not in t
              and "1less.app" not in t.lower())
    resp = p.go("/no-such-page-kzv/", wait="load")
    run.check("j7", vp, "unknown page answers 404", resp.status == 404, resp.status)
    back = pg.locator("a[href]").filter(has_text=re.compile(r"start|home|cards|places|KidZooKit", re.I))
    run.check("j7", vp, "404 page offers a way back", back.count() > 0, back.count())
    p.shot("j7-404")
    p.errors[:] = [e for e in p.errors if "status of 404" not in e]  # the deliberate 404
    for path in ("/newsletter/thanks/", "/newsletter/oops/?reason=email", "/newsletter/try-again/", "/newsletter/one-more-step/"):
        resp = p.go(path, wait="load")
        tt = visible_text(pg)
        run.check("j7", vp, f"{path} answers 200 with a way back", resp.status == 200 and pg.get_by_role("link").count() > 0, tt[:80])
    # No-JS error pages name one cause each (K1, 2026-11-18).
    oops_email = p.go("/newsletter/oops/?reason=email", wait="load") and visible_text(pg)
    run.check("j7", vp, "bad-address page does not claim a server error", "look quite right" in oops_email and "went wrong" not in oops_email, oops_email[:120])
    again = p.go("/newsletter/try-again/", wait="load") and visible_text(pg)
    run.check("j7", vp, "server-error page does not blame the address", "went wrong" in again and "look quite right" not in again, again[:120])
    r = ctx.request.get(run.url("/start/"))
    h = r.headers
    run.check("j7", vp, "security headers on /start/", all(k in h for k in ("content-security-policy", "x-content-type-options", "referrer-policy"))
              and "frame-ancestors 'none'" in h.get("content-security-policy", ""), [k for k in ("content-security-policy", "x-content-type-options", "referrer-policy") if k not in h])
    # No-JS fallback: a bad address posts to /api/newsletter and comes back to the oops page (no Kit call).
    r = ctx.request.post(run.base + "/api/newsletter", form={"email_address": "nope", "placement": "printables_hub"}, max_redirects=0)
    run.check("j7", vp, "no-JS bad address -> 303 oops?reason=email", r.status == 303 and r.headers.get("location") == "/newsletter/oops/?reason=email",
              (r.status, r.headers.get("location")))
    p.hygiene("j7", "trust")
    pg.close()


JOURNEYS = {
    "j1": j1_landing, "j2": j2_pin_to_print, "j3": j3_cards, "j4": j4_quiz,
    "j5": j5_newsletter, "j6": j6_print_and_qr, "j7": j7_trust,
}
ONE_VIEWPORT = {"j6": "phone", "j7": "phone"}  # pure HTTP-ish journeys: one viewport is enough


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://kidzookit.com")
    ap.add_argument("--out", required=True)
    ap.add_argument("--only", default="")
    ap.add_argument("--viewports", default="phone,desktop")
    ap.add_argument("--real-signup", action="store_true",
                    help="PAUSED: ONE real Kit signup to nyhemant+kzkverify-<stamp>@gmail.com (phone only); also needs "
                         f"{SIGNUP_ENV}=yes. Default mocks the signup in the browser.")
    a = ap.parse_args()
    if a.real_signup and os.environ.get(SIGNUP_ENV) != "yes":
        sys.exit(f"STOP: live newsletter signups are paused (owner rule 2026-11-18). The default run mocks the signup. "
                 f"Only with a new owner OK: {SIGNUP_ENV}=yes ... --real-signup")
    host = urlsplit(a.base).hostname
    if host not in (DOMAIN, "127.0.0.1", "localhost"):
        sys.exit(f"STOP: base host {host!r} is not {DOMAIN}")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    run = Run(a.base, out)
    stamp = datetime.now().strftime("%m%d%H%M")
    only = [j for j in a.only.split(",") if j] or list(JOURNEYS)
    started = time.time()
    with sync_playwright() as pw:
        launch = dict(args=["--no-sandbox"])
        if Path(CHROME).exists():
            launch["executable_path"] = CHROME
        browser = pw.chromium.launch(**launch)
        for vp in a.viewports.split(","):
            ua = browser.new_context().new_page().evaluate("navigator.userAgent").replace("HeadlessChrome", "Chrome")
            ctx = browser.new_context(user_agent=f"{ua} {UA_SUFFIX}", **VIEWPORTS[vp])
            ctx.add_cookies([{"name": "one_less_analytics", "value": "off", "domain": host, "path": "/"}])
            ctx.add_init_script(PRINT_SPY)
            for j in only:
                if ONE_VIEWPORT.get(j, vp) != vp:
                    continue
                try:
                    if j == "j5":
                        JOURNEYS[j](run, ctx, vp, a.real_signup and vp == "phone", stamp)
                    else:
                        JOURNEYS[j](run, ctx, vp)
                except (PWTimeout, PWError, AssertionError) as e:
                    run.check(j, vp, "journey finished", False, f"{type(e).__name__}: {str(e).splitlines()[0]}")
            ctx.close()
        browser.close()
    counts = {s: sum(r["status"] == s for r in run.rows) for s in ("PASS", "WARN", "FAIL")}
    (out / "results.json").write_text(json.dumps({"base": a.base, "at": datetime.now().isoformat(timespec="seconds"),
                                                  "seconds": round(time.time() - started), "counts": counts, "rows": run.rows}, indent=1))
    print(f"SUMMARY {counts['PASS']} PASS / {counts['WARN']} WARN / {counts['FAIL']} FAIL -> {out}/results.json")
    sys.exit(1 if counts["FAIL"] else 0)


if __name__ == "__main__":
    main()
