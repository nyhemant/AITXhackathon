/**
 * Weekly email box for grown-ups, on the printables pages only.
 * Static forms: placement=printables_hub or placement=printable_sheet.
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
    if (value === "printables_hub" || value === "printable_sheet") return value;
    return "other";
  }

  function track(name, placement) {
    var params = { placement: cleanPlacement(placement) };
    if (name === "sign_up") params.method = "newsletter";
    // sign_up sends placement and method only. Drop any address-shaped value.
    Object.keys(params).forEach(function (key) {
      var value = params[key];
      if (key === "email" || key === "email_address" || key === "mail") {
        delete params[key];
        return;
      }
      if (typeof value === "string" && value.indexOf("@") !== -1) delete params[key];
    });
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

  function init() {
    var forms = document.querySelectorAll("form.kz-nl");
    if (storageGet(SUB_KEY) === "1" || storageGet(DISMISS_KEY) === "1") {
      for (var h = 0; h < forms.length; h++) forms[h].hidden = true;
      return;
    }
    for (var i = 0; i < forms.length; i++) {
      bind(forms[i]);
      watchView(forms[i]);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
