/**
 * Weekly email box.
 * Hub: enhance the static form (placement=cards_hub_aotd).
 * Card: after .study-finish (placement=quiz_finish). Not inside that live region.
 * Events go through FPTrack / OneLessAnalytics.track so the opt-out is kept.
 * Never send the email address, or any hash of it, to analytics.
 */
(function () {
  "use strict";

  var SUB_KEY = "kz_nl_subscribed";
  var DISMISS_KEY = "kz_nl_dismissed";
  var seen = {};

  function storageGet(key) {
    try {
      return localStorage.getItem(key);
    } catch (err) {
      return null;
    }
  }

  function storageSet(key) {
    try {
      localStorage.setItem(key, "1");
    } catch (err) {
      /* private mode */
    }
  }

  function cleanPlacement(value) {
    if (value === "quiz_finish" || value === "cards_hub_aotd") return value;
    return "other";
  }

  function track(name, placement) {
    var params = { placement: cleanPlacement(placement) };
    if (name === "sign_up") params.method = "newsletter";
    if (typeof window.FPTrack === "function") {
      window.FPTrack(name, params);
      return;
    }
    var helper = window.OneLessAnalytics;
    if (helper && typeof helper.track === "function") helper.track(name, params);
  }

  function watchView(form) {
    var placement = cleanPlacement(form.getAttribute("data-placement"));
    if (seen[placement]) return;
    if (typeof IntersectionObserver !== "function") return;
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting || seen[placement]) return;
          seen[placement] = true;
          track("newsletter_view", placement);
          observer.disconnect();
        });
      },
      { threshold: 0.4 }
    );
    observer.observe(form);
  }

  function quizFormHtml() {
    return (
      '<form class="kz-nl kz-nl--quiz no-print" action="/api/newsletter" method="post" data-placement="quiz_finish" novalidate aria-labelledby="kz-nl-h-quiz">' +
      '<h3 class="kz-nl-h" id="kz-nl-h-quiz">One animal + a quiz each week</h3>' +
      '<p class="kz-nl-sub">A real animal card, three quick questions and a printable, in your inbox once a week.</p>' +
      '<div class="kz-nl-fields">' +
      '<div class="kz-nl-field">' +
      '<label for="kz-nl-email-quiz">Your email</label>' +
      '<input id="kz-nl-email-quiz" name="email_address" type="email" autocomplete="email" inputmode="email" required placeholder="you@example.com" aria-describedby="kz-nl-privacy-quiz kz-nl-msg-quiz">' +
      "</div>" +
      '<div class="kz-nl-actions">' +
      '<button class="kz-nl-submit" type="submit">Send me the weekly animal</button>' +
      '<button class="kz-nl-dismiss" type="button">No thanks</button>' +
      "</div></div>" +
      '<div class="kz-nl-hp" aria-hidden="true"><label for="kz-nl-website-quiz">Website</label>' +
      '<input id="kz-nl-website-quiz" name="website" type="text" tabindex="-1" autocomplete="off"></div>' +
      '<input type="hidden" name="placement" value="quiz_finish">' +
      '<p class="kz-nl-privacy" id="kz-nl-privacy-quiz">Email only, nothing about your kids. Unsubscribe anytime. No spam. <a href="/privacy/">Privacy</a></p>' +
      '<p class="kz-nl-msg" id="kz-nl-msg-quiz" role="status" aria-live="polite"></p>' +
      "</form>"
    );
  }

  function showStatus(form, kind, text) {
    var msg = form.querySelector(".kz-nl-msg");
    var input = form.querySelector('input[type="email"]');
    if (msg) {
      msg.textContent = text;
      if (kind) msg.setAttribute("data-state", kind);
      else msg.removeAttribute("data-state");
    }
    if (!input) return;
    if (kind === "error") {
      input.setAttribute("aria-invalid", "true");
      input.focus();
    } else {
      input.removeAttribute("aria-invalid");
    }
  }

  function bind(form) {
    if (form.getAttribute("data-nl-bound") === "1") return;
    form.setAttribute("data-nl-bound", "1");
    var dismiss = form.querySelector(".kz-nl-dismiss");
    if (dismiss) {
      dismiss.addEventListener("click", function () {
        storageSet(DISMISS_KEY);
        form.remove();
      });
    }
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var placement = cleanPlacement(form.getAttribute("data-placement"));
      var button = form.querySelector(".kz-nl-submit");
      if (button) {
        button.disabled = true;
        button.setAttribute("aria-busy", "true");
      }
      showStatus(form, "", "");
      fetch("/api/newsletter", {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form),
      })
        .then(function (res) {
          return res.json().then(
            function (json) {
              return { res: res, json: json };
            },
            function () {
              return { res: res, json: null };
            }
          );
        })
        .then(function (out) {
          var json = out.json;
          if (out.res.ok && json && json.ok === true) {
            var already = json.already === true;
            showStatus(
              form,
              "ok",
              already
                ? "You're already on the list. Thanks!"
                : "You're in! Check your inbox to confirm. The next animal arrives soon."
            );
            storageSet(SUB_KEY);
            if (!already) track("sign_up", placement);
            if (button) button.disabled = true;
            var input = form.querySelector('input[type="email"]');
            if (input) input.disabled = true;
            if (dismiss) dismiss.remove();
            return;
          }
          var code = json && json.error;
          showStatus(
            form,
            "error",
            code === "invalid_email"
              ? "That email doesn't look quite right. Mind checking it?"
              : "Something went wrong on our end. Please try again in a minute."
          );
          if (button) button.disabled = false;
        })
        .catch(function () {
          showStatus(form, "error", "Something went wrong on our end. Please try again in a minute.");
          if (button) button.disabled = false;
        })
        .then(function () {
          if (button) button.removeAttribute("aria-busy");
        });
    });
  }

  function mountQuiz(finish) {
    if (storageGet(SUB_KEY) === "1" || storageGet(DISMISS_KEY) === "1") return;
    var foot = finish.parentNode;
    if (!foot || !foot.classList || !foot.classList.contains("study-foot")) return;
    var existing = foot.querySelector(".kz-nl--quiz");
    if (existing) {
      if (finish.nextElementSibling !== existing) finish.insertAdjacentElement("afterend", existing);
      return;
    }
    var holder = document.createElement("div");
    holder.innerHTML = quizFormHtml();
    var form = holder.firstElementChild;
    if (!form) return;
    finish.insertAdjacentElement("afterend", form);
    bind(form);
    watchView(form);
  }

  function syncQuiz() {
    var feet = document.querySelectorAll(".study-foot");
    for (var i = 0; i < feet.length; i++) {
      var foot = feet[i];
      var finish = foot.querySelector(".study-finish");
      var form = foot.querySelector(".kz-nl--quiz");
      if (!finish) {
        if (form) form.remove();
        continue;
      }
      mountQuiz(finish);
    }
  }

  function observeQuiz() {
    var feet = document.querySelectorAll(".study-foot");
    if (!feet.length || typeof MutationObserver !== "function") return;
    var observer = new MutationObserver(syncQuiz);
    for (var i = 0; i < feet.length; i++) {
      observer.observe(feet[i], { childList: true });
    }
    syncQuiz();
  }

  function init() {
    var forms = document.querySelectorAll("form.kz-nl");
    for (var i = 0; i < forms.length; i++) {
      var form = forms[i];
      if (storageGet(SUB_KEY) === "1") {
        form.hidden = true;
        continue;
      }
      bind(form);
      watchView(form);
    }
    observeQuiz();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
