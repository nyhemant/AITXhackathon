"""Study-card quiz: wrong pick is grey + disabled; second try still scores."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
FP = REPO / "static" / "field-pack"
STUDY_JS = FP / "js" / "study-card.js"
STUDY_CSS = FP / "css" / "study-card.css"
STYLES = FP / "css" / "styles.css"
SEO = REPO / "scripts" / "generate_bdo_seo.py"
LION = FP / "cards" / "african-lion" / "index.html"

RUNTIME = r"""
const fs = require("fs");
const src = fs.readFileSync(process.argv[2], "utf8");
function sliceFn(name, next) {
  const start = src.indexOf("function " + name);
  const end = src.indexOf("function " + next);
  if (start < 0 || end < 0 || end <= start) throw new Error("missing " + name);
  return src.slice(start, end);
}
function makeClassList(initial) {
  const s = new Set((initial || "").split(/\s+/).filter(Boolean));
  return {
    add(c) { s.add(c); },
    remove(...cs) { cs.forEach((c) => s.delete(c)); },
    contains(c) { return s.has(c); },
    toString() { return [...s].join(" "); },
  };
}
function el(attrs) {
  const node = {
    attrs: { ...attrs },
    classList: makeClassList(attrs.class || ""),
    children: [],
    hidden: !!attrs.hidden,
    disabled: false,
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k) ? String(this.attrs[k]) : ""; },
    setAttribute(k, v) { this.attrs[k] = String(v); },
    querySelector(sel) { return this.querySelectorAll(sel)[0] || null; },
    querySelectorAll(sel) {
      const out = [];
      const walk = (n) => {
        if (match(n, sel)) out.push(n);
        (n.children || []).forEach(walk);
      };
      walk(this);
      return out;
    },
  };
  return node;
}
function match(n, sel) {
  if (sel === ".study-why") return (n.attrs.class || "").split(/\s+/).includes("study-why");
  if (sel === ".study-q") return (n.attrs.class || "").split(/\s+/).includes("study-q");
  const m = sel.match(/^\.study-choice(?:\[data-letter="([A-C])"\])?$/);
  if (m) {
    if (!(n.attrs.class || "").split(/\s+/).includes("study-choice")) return false;
    return !m[1] || n.getAttribute("data-letter") === m[1];
  }
  return false;
}
function question() {
  const q = el({ class: "mission study-q", "data-correct": "B" });
  const why = el({ class: "study-why", hidden: true });
  why.hidden = true;
  const a = el({ class: "choice study-choice", "data-letter": "A" });
  const b = el({ class: "choice study-choice", "data-letter": "B" });
  const c = el({ class: "choice study-choice", "data-letter": "C" });
  q.children.push(a, b, c, why);
  return { q, a, b, c, why };
}

function questions(root) {
  return [...root.querySelectorAll(".study-q")];
}
const markChoice = eval("(" + sliceFn("markChoice", "scoreOf").trim() + ")");
const scoreOf = eval("(" + sliceFn("scoreOf", "paintScore").trim() + ")");

function fail(msg) { console.error(msg); process.exit(1); }

const first = question();
markChoice(first.q, first.a, false);
if (!first.a.classList.contains("is-wrong-pick")) fail("wrong pick should be is-wrong-pick");
if (!first.a.disabled) fail("wrong pick should be disabled");
if (first.b.classList.contains("is-correct-key")) fail("must not reveal correct key on wrong");
if (first.c.classList.contains("is-wrong-pick") || first.c.disabled) fail("other choices stay enabled");
if (!first.why.hidden) fail("why must stay hidden after a wrong pick");
if (first.q.classList.contains("mission-ok")) fail("wrong pick is not scored correct");
if (scoreOf({ querySelectorAll: () => [first.q] }) !== 0) fail("score stays 0 after a wrong pick");

markChoice(first.q, first.a, false);
if (!first.a.disabled || !first.a.classList.contains("is-wrong-pick")) fail("disabled wrong stays disabled");

markChoice(first.q, first.c, false);
if (!first.c.classList.contains("is-wrong-pick") || !first.c.disabled) fail("second wrong also disables");
if (!first.a.classList.contains("is-wrong-pick") || !first.a.disabled) fail("first wrong must accumulate");
if (first.b.classList.contains("is-correct-key")) fail("still no correct key after two wrongs");
if (!first.why.hidden) fail("why still hidden after two wrongs");
if (scoreOf({ querySelectorAll: () => [first.q] }) !== 0) fail("score still 0 after two wrongs");

markChoice(first.q, first.b, false);
if (!first.b.classList.contains("is-correct-pick")) fail("correct pick gets is-correct-pick");
if (first.why.hidden) fail("why shows after correct");
if (!first.q.classList.contains("mission-ok")) fail("question marked mission-ok");
if (!first.a.classList.contains("is-wrong-pick") || !first.c.classList.contains("is-wrong-pick")) {
  fail("prior wrongs stay grey after a later correct");
}
if (!first.a.disabled || !first.c.disabled) fail("remaining choices disable once correct is locked");
if (scoreOf({ querySelectorAll: () => [first.q] }) !== 1) fail("second-attempt correct still scores");

const locked = question();
markChoice(locked.q, locked.b, false);
markChoice(locked.q, locked.a, false);
if (locked.a.classList.contains("is-wrong-pick")) fail("cannot change a locked correct question");
if (!locked.b.classList.contains("is-correct-pick")) fail("correct pick stays after extra taps");

const firstTry = question();
markChoice(firstTry.q, firstTry.b, false);
if (!firstTry.b.classList.contains("is-correct-pick") || firstTry.why.hidden) fail("first-try correct still shows why");
if (scoreOf({ querySelectorAll: () => [firstTry.q] }) !== 1) fail("first-try correct scores");

console.log("ok");
"""


def _fn(src: str, name: str, nxt: str) -> str:
    start = src.index(f"function {name}")
    end = src.index(f"function {nxt}")
    return src[start:end]


class StudyCardQuizTests(unittest.TestCase):
    def test_mark_choice_allows_second_try_without_revealing(self):
        js = STUDY_JS.read_text(encoding="utf-8")
        mark = _fn(js, "markChoice", "scoreOf")
        self.assertIn('btn.classList.add("is-wrong-pick")', mark)
        self.assertIn("btn.disabled = true", mark)
        self.assertIn("why.hidden = true", mark)
        self.assertIn('btn.classList.add("is-correct-pick")', mark)
        self.assertIn("why.hidden = false", mark)
        self.assertNotIn('right.classList.add("is-correct-key")', mark)
        self.assertNotIn("is-correct-key", mark)
        self.assertNotIn(
            'classList.remove("is-correct-pick", "is-wrong-pick", "is-correct-key")',
            mark,
        )
        self.assertIn("is-wrong-pick", mark)
        bind = _fn(js, "bind", "boot")
        self.assertIn("choice.disabled", bind)
        reveal = _fn(js, "revealAll", "paintPicker")
        self.assertIn('b.classList.toggle("is-correct-key", letter === correct)', reveal)
        self.assertIn("b.disabled = false", reveal)

    def test_study_wrong_css_is_grey_and_scoped(self):
        css = STUDY_CSS.read_text(encoding="utf-8")
        self.assertIn(".card-page .card-study-pack .study-choice.is-wrong-pick", css)
        self.assertIn("#d5d8de", css)
        self.assertIn("#7b828c", css)
        self.assertIn("#4a5058", css)
        self.assertNotIn("#fff1e0", css)
        self.assertNotIn("#d97706", css)
        styles = STYLES.read_text(encoding="utf-8")
        self.assertRegex(
            styles,
            r"\.choice\.is-wrong-pick \{\s*background: #fff1e0 !important;",
        )
        self.assertIn("border-color: #d97706 !important;", styles)

    def test_cache_versions_bumped_for_quiz_ux(self):
        seo = SEO.read_text(encoding="utf-8")
        self.assertIn('STUDY_CARD_JS_VER = "10"', seo)
        self.assertIn('STUDY_CARD_CSS_VER = "9"', seo)
        html = LION.read_text(encoding="utf-8")
        self.assertIn("study-card.js?v=10", html)
        self.assertIn("study-card.css?v=9", html)

    def test_runtime_wrong_then_correct_scores(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is required for the study-card quiz runtime harness")
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(RUNTIME)
            harness = fh.name
        try:
            proc = subprocess.run(
                [node, harness, str(STUDY_JS)],
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
        finally:
            Path(harness).unlink(missing_ok=True)
        self.assertEqual(proc.returncode, 0, proc.stderr or proc.stdout)
        self.assertIn("ok", proc.stdout)


if __name__ == "__main__":
    unittest.main()
