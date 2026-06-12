(function () {
  "use strict";

  var cssLink = document.querySelector("link[data-brt-css]");

  if (cssLink) {
    cssLink.addEventListener("error", function () {
      document.documentElement.classList.add("brt-css-fallback-mode");
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
  });
})();
