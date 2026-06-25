(function () {
  "use strict";

  var cssLink = document.querySelector("link[data-brt-css]");
  var fallbackLink = document.querySelector('link[href*="brt-fallback.css"]');
  var logoImg = document.querySelector(".site-header__logo-img--light");

  if (cssLink) {
    cssLink.addEventListener("error", function () {
      document.documentElement.classList.add("brt-css-fallback-mode");
    });
  }

  if (logoImg) {
    logoImg.addEventListener("error", function () {
      /* fail-open: alt text remains */
    });
  }

  window.addEventListener("DOMContentLoaded", function () {
    var targetH1 = document.querySelector(".brt-h1");

    if (targetH1 && !document.documentElement.classList.contains("brt-css-fallback-mode")) {
      var style = window.getComputedStyle(targetH1);
      var cssSheetLoaded = cssLink && cssLink.sheet;
      var usesDefaultTypography =
        style.fontSize === "32px" && style.letterSpacing === "normal";
      if (!cssSheetLoaded && usesDefaultTypography) {
        document.documentElement.classList.add("brt-css-fallback-mode");
      }
    }

    if (location.protocol === "file:" && cssLink && !cssLink.sheet) {
      showFileProtocolHint();
    }
  });

  function showFileProtocolHint() {
    if (document.getElementById("brt-file-protocol-hint")) return;
    var hint = document.createElement("div");
    hint.id = "brt-file-protocol-hint";
    hint.setAttribute("role", "status");
    hint.innerHTML =
      "<strong>Local preview:</strong> This browser blocks CSS and images on <code>file://</code>. " +
      "Open in <strong>Chrome</strong> or <strong>Safari</strong> (double-click <code>index.html</code> or <code>ÖFFNEN.command</code>). " +
      "Comet only: <code>python3 Webseite/preview-local.py</code> → http://127.0.0.1:8766/";
    hint.style.cssText =
      "margin:1rem;padding:1rem;background:#fff3cd;color:#0e1116;border:1px solid #856404;" +
      "font:14px/1.5 system-ui,sans-serif;";
    document.body.insertBefore(hint, document.body.firstChild);
  }
})();
