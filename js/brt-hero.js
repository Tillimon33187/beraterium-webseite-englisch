(function () {
  "use strict";

  var SLIDE_DURATION_MS = 6500;

  function initBerateriumHero() {
    var root = document.querySelector(".brt");
    if (!root) return;

    var hero = root.querySelector(".brt-hero");
    if (!hero) return;

    var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var slideFallbackTimer = null;
    var slides = hero.querySelectorAll(".brt-hero__slide");
    var topics = hero.querySelectorAll(".brt-hero__topic");
    var heroTag = hero.querySelector(".js-hero-tag");
    var heroTitle = hero.querySelector(".js-hero-title");
    var heroSubline = hero.querySelector(".js-hero-subline");
    var primaryCta = hero.querySelector(".js-hero-primary-cta");
    var scrollBtn = hero.querySelector(".brt-hero__scroll");
    var activeSlide = 0;

    hero.style.setProperty("--hero-slide-duration", (SLIDE_DURATION_MS / 1000) + "s");

    function applyTopicContent(button) {
      if (!button) return;
      if (heroTag && button.dataset.tag) heroTag.textContent = button.dataset.tag;
      if (heroTitle && button.dataset.title) heroTitle.textContent = button.dataset.title;
      if (heroSubline && button.dataset.subline) heroSubline.textContent = button.dataset.subline;
      if (primaryCta && button.dataset.primaryCtaLabel) primaryCta.textContent = button.dataset.primaryCtaLabel;
      if (primaryCta && button.dataset.primaryCtaHref) primaryCta.setAttribute("href", button.dataset.primaryCtaHref);
    }

    if (scrollBtn) {
      scrollBtn.addEventListener("click", function () {
        var nextSection = hero.nextElementSibling;
        if (nextSection) {
          nextSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    }

    function restartProgress(topicButton) {
      var progress = topicButton.querySelector(".brt-hero__topic-progress");
      if (!progress) return;
      progress.style.animation = "none";
      void progress.offsetWidth;
      progress.style.animation = "";
    }

    function scheduleFallbackAdvance() {
      if (prefersReduced) return;
      if (slideFallbackTimer) window.clearTimeout(slideFallbackTimer);
      slideFallbackTimer = window.setTimeout(function () {
        setSlide(activeSlide + 1);
      }, SLIDE_DURATION_MS);
    }

    function setSlide(index) {
      if (!slides.length || !topics.length) return;
      var safeIndex = (index + slides.length) % slides.length;
      activeSlide = safeIndex;

      slides.forEach(function (slide, slideIndex) {
        slide.classList.toggle("is-active", slideIndex === safeIndex);
      });
      topics.forEach(function (topic, topicIndex) {
        topic.classList.toggle("is-active", topicIndex === safeIndex);
      });

      applyTopicContent(topics[safeIndex]);
      restartProgress(topics[safeIndex]);
      scheduleFallbackAdvance();
    }

    topics.forEach(function (topicButton) {
      var progress = topicButton.querySelector(".brt-hero__topic-progress");
      if (progress) {
        progress.addEventListener("animationend", function (event) {
          if (event.animationName !== "brt-hero-topic-progress") return;
          if (!topicButton.classList.contains("is-active")) return;
          setSlide(activeSlide + 1);
        });
      }

      topicButton.addEventListener("click", function () {
        var targetIndex = Number(topicButton.dataset.slideIndex);
        if (Number.isNaN(targetIndex)) return;
        setSlide(targetIndex);
      });
    });

    setSlide(0);

    window.requestAnimationFrame(function () {
      var activeTopic = hero.querySelector(".brt-hero__topic.is-active");
      if (activeTopic) restartProgress(activeTopic);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBerateriumHero);
  } else {
    initBerateriumHero();
  }
})();
