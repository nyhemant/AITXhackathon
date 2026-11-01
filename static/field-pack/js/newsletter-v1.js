/**
 * Weekly email box for grown-ups, on the printables pages only.
 * Static forms: placement=printables_hub or placement=printable_sheet.
 * "See a sample email" opens /newsletter/sample/ in a dialog. With JS off, that href is the page.
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

  var sampleDialog = null;
  var sampleOpener = null;
  var sampleArticle = null;
  var sampleRequest = null;

  function clearNode(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function tabbable(root) {
    var nodes = root.querySelectorAll(
      "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]"
    );
    var out = [];
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      if (el.tabIndex < 0) continue;
      if (el.closest && el.closest("[hidden]")) continue;
      out.push(el);
    }
    return out;
  }

  function trapTab(event) {
    if (event.key !== "Tab") return;
    var dialog = event.currentTarget;
    var items = tabbable(dialog);
    if (!items.length) {
      event.preventDefault();
      return;
    }
    var first = items[0];
    var last = items[items.length - 1];
    var active = document.activeElement;
    if (event.shiftKey) {
      if (active === first || !dialog.contains(active)) {
        event.preventDefault();
        last.focus();
      }
      return;
    }
    if (active === last || !dialog.contains(active)) {
      event.preventDefault();
      first.focus();
    }
  }

  function ensureSampleDialog() {
    if (sampleDialog) return sampleDialog;
    var dialog = document.createElement("dialog");
    dialog.className = "kz-nl-dialog";
    dialog.setAttribute("aria-labelledby", "kz-nl-sample-tag");
    var head = document.createElement("div");
    head.className = "kz-nl-dialog-head";
    var tag = document.createElement("p");
    tag.className = "kz-nl-sample-tag";
    tag.id = "kz-nl-sample-tag";
    tag.textContent = "Sample email";
    var closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "kz-nl-dialog-close";
    closeBtn.textContent = "Close";
    closeBtn.addEventListener("click", function () {
      dialog.close();
    });
    head.appendChild(tag);
    head.appendChild(closeBtn);
    var body = document.createElement("div");
    body.className = "kz-nl-dialog-body";
    body.tabIndex = 0;
    dialog.appendChild(head);
    dialog.appendChild(body);
    dialog.addEventListener("click", function (event) {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener("keydown", trapTab);
    dialog.addEventListener("close", function () {
      document.documentElement.classList.remove("kz-nl-modal-open");
      var opener = sampleOpener;
      if (!opener || typeof opener.focus !== "function") return;
      opener.focus();
      setTimeout(function () {
        opener.focus();
      }, 0);
    });
    document.body.appendChild(dialog);
    sampleDialog = dialog;
    return dialog;
  }

  function renderSample(body) {
    clearNode(body);
    if (!sampleArticle) {
      body.textContent = "Loading the sample.";
      return;
    }
    body.appendChild(document.importNode(sampleArticle, true));
  }

  function loadSample(href) {
    if (sampleArticle) return Promise.resolve(sampleArticle);
    if (sampleRequest) return sampleRequest;
    sampleRequest = fetch(href, {
      headers: { Accept: "text/html" },
      credentials: "same-origin",
    })
      .then(function (res) {
        if (!res.ok) throw new Error("status");
        return res.text();
      })
      .then(function (html) {
        var parsed = new DOMParser().parseFromString(html, "text/html");
        var article = parsed.querySelector("#kz-sample-email") || parsed.querySelector("article");
        if (!article) throw new Error("article");
        sampleArticle = article;
        return article;
      })
      .catch(function (err) {
        sampleRequest = null;
        throw err;
      });
    return sampleRequest;
  }

  function focusOpener(link) {
    if (document.activeElement !== link && typeof link.focus === "function") link.focus();
  }

  function openSample(link, placement) {
    var href = link.getAttribute("href") || "/newsletter/sample/";
    if (typeof HTMLDialogElement !== "function" || typeof document.createElement("dialog").showModal !== "function") {
      window.location.href = href;
      return;
    }
    var dialog = ensureSampleDialog();
    var body = dialog.querySelector(".kz-nl-dialog-body");
    sampleOpener = link;
    focusOpener(link);
    renderSample(body);
    if (!dialog.open) {
      document.documentElement.classList.add("kz-nl-modal-open");
      dialog.showModal();
    }
    var closeBtn = dialog.querySelector(".kz-nl-dialog-close");
    if (closeBtn) closeBtn.focus();
    track("newsletter_sample_open", placement);
    loadSample(href)
      .then(function () {
        if (!dialog.open) return;
        renderSample(body);
      })
      .catch(function () {
        if (!dialog.open) return;
        window.location.href = href;
      });
  }

  function plainSampleClick(event) {
    if (event.defaultPrevented || event.button !== 0) return false;
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return false;
    return true;
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
    var sampleLinks = form.querySelectorAll("a.kz-nl-sample");
    var placement = cleanPlacement(form.getAttribute("data-placement"));
    for (var s = 0; s < sampleLinks.length; s++) {
      sampleLinks[s].addEventListener("click", function (event) {
        if (!plainSampleClick(event)) return;
        event.preventDefault();
        openSample(event.currentTarget, placement);
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
