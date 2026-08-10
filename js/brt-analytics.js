/* Beraterium GA4 custom events — only fires when gtag is available (after analytics consent). */
(function () {
  "use strict";

  function track(eventName, params) {
    if (typeof gtag !== "function") return;
    gtag("event", eventName, params || {});
  }

  window.brtTrack = track;

  function pathKey(href) {
    try {
      var u = new URL(href, location.href);
      return u.pathname.replace(/\/index\.html$/, "/");
    } catch (e) {
      return href || "";
    }
  }

  function isContactPath(p) {
    return /\/(kontakt|contact)\/?$/i.test(p);
  }

  function isContactFormPath(p) {
    return /\/(kontaktformular|contact-form)\/?$/i.test(p);
  }

  function isBlindspotPath(p) {
    return /blindspot-check/i.test(p);
  }

  function ctaLocation(link) {
    if (link.closest(".site-header")) {
      return link.classList.contains("site-header__cta") ? "header_cta" : "header_nav";
    }
    if (link.closest(".brt-hero")) return "hero";
    if (link.closest("footer") || link.closest(".brt-footer")) return "footer";
    if (link.closest(".brt-article")) return "blog_article";
    if (link.closest(".bqc-result")) return "blindspot_result";
    if (link.closest(".brt-guarantee") || link.closest(".brt-cta-band")) return "cta_band";
    return "content";
  }

  function initCtaTracking() {
    document.addEventListener(
      "click",
      function (e) {
        var link = e.target.closest("a[href]");
        if (!link) return;
        var p = pathKey(link.getAttribute("href"));
        var type = null;
        if (isContactPath(p)) type = "erstgespraech";
        else if (isBlindspotPath(p)) type = "blindspot";
        else if (isContactFormPath(p)) type = "kontaktformular";
        if (!type) return;
        track("cta_click", {
          cta_type: type,
          cta_location: ctaLocation(link),
          link_url: p,
          link_text: (link.textContent || "").trim().slice(0, 80),
          page_path: location.pathname,
        });
      },
      true
    );
  }

  function initCalendlyTracking() {
    window.addEventListener("message", function (e) {
      if (e.origin !== "https://calendly.com") return;
      if (!e.data || !e.data.event) return;
      if (e.data.event === "calendly.event_scheduled") {
        var payload = e.data.payload || {};
        var eventType = payload.event_type || {};
        track("calendly_booked", {
          page_path: location.pathname,
          event_type: eventType.name || "",
        });
      }
    });
  }

  function initContactFormTracking() {
    var form = document.querySelector(".brt-form--contact");
    if (!form) return;
    form.addEventListener("submit", function () {
      if (!form.checkValidity()) return;
      var agb = form.querySelector("#agb_accepted");
      var privacy = form.querySelector("#privacy_accepted");
      if (agb && privacy && (!agb.checked || !privacy.checked)) return;
      track("contact_form_submit", { page_path: location.pathname });
    });
  }

  function init() {
    initCtaTracking();
    initCalendlyTracking();
    initContactFormTracking();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
