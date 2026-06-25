(function () {
  "use strict";

  function fileProtocolHref(href) {
    if (!href || href.charAt(0) === "#") return href;
    if (/^(https?:|mailto:|tel:)/i.test(href)) return href;

    var hash = "";
    var query = "";
    var path = href;
    var hashAt = path.indexOf("#");
    if (hashAt !== -1) {
      hash = path.slice(hashAt);
      path = path.slice(0, hashAt);
    }
    var queryAt = path.indexOf("?");
    if (queryAt !== -1) {
      query = path.slice(queryAt);
      path = path.slice(0, queryAt);
    }

    if (/\.html$/i.test(path)) return href;
    if (path === "." || path === "./") path = "./index.html";
    else if (path === ".." || path === "../") path = "../index.html";
    else if (path.slice(-1) === "/") path = path + "index.html";
    else if (!/\.[a-zA-Z0-9]{2,8}$/.test(path)) path = path.replace(/\/?$/, "/") + "index.html";

    return path + query + hash;
  }

  function initFileProtocolLinks() {
    if (location.protocol !== "file:") return;

    document.addEventListener("click", function (e) {
      var link = e.target.closest("a[href]");
      if (!link) return;
      if (link.classList.contains("site-header__parent-link") && !window.matchMedia("(min-width: 1024px)").matches) {
        return;
      }
      var href = link.getAttribute("href");
      if (!href) return;
      var rewritten = fileProtocolHref(href);
      if (rewritten === href) return;
      e.preventDefault();
      location.href = new URL(rewritten, location.href).href;
    }, true);
  }

  function revealHashTargetContent(target) {
    if (!target) return;
    target.querySelectorAll(".brt-fade-up, .brt-stagger > *").forEach(function (el) {
      el.classList.add("is-visible");
      el.style.transitionDelay = "0ms";
    });
  }

  function scrollToTeamSection(section) {
    if (!section) return;

    revealTeamExpandForTarget(section);
    revealHashTargetContent(section);

    var header = document.querySelector(".site-header");
    var headerH = header ? header.getBoundingClientRect().height : 84;
    var scrollTarget = section.querySelector(".brt-split__media") || section;
    var gap = 32;
    var offset = headerH + gap;
    var rectTop = scrollTarget.getBoundingClientRect().top;
    var y = rectTop + window.pageYOffset - offset;
    window.scrollTo(0, Math.max(0, y));
  }

  function scrollToAnchorHash() {
    var hash = location.hash;
    if (!hash || hash.length < 2) return;
    var target = document.getElementById(decodeURIComponent(hash.slice(1)));
    if (!target) return;
    scrollToTeamSection(target);
  }

  function scheduleAnchorScroll() {
    scrollToAnchorHash();
    requestAnimationFrame(function () {
      scrollToAnchorHash();
      requestAnimationFrame(scrollToAnchorHash);
    });
  }

  function scheduleTeamSectionScroll(section) {
    requestAnimationFrame(function () {
      scrollToTeamSection(section);
      requestAnimationFrame(function () {
        scrollToTeamSection(section);
      });
    });
  }

  function forceInstantScroll(y) {
    var root = document.documentElement;
    var body = document.body;
    var rootPrev = root.style.scrollBehavior;
    var bodyPrev = body ? body.style.scrollBehavior : "";
    root.style.scrollBehavior = "auto";
    if (body) body.style.scrollBehavior = "auto";
    window.scrollTo(0, Math.max(0, y));
    root.style.scrollBehavior = rootPrev;
    if (body) body.style.scrollBehavior = bodyPrev;
  }

  function getTeamSectionScrollY(section) {
    if (!section) return 0;
    var scrollTarget =
      section.querySelector(".brt-section__header") ||
      section.querySelector(".brt-page-hero .brt-container") ||
      section.querySelector("h1") ||
      section;
    var header = document.querySelector(".site-header");
    var headerH = header ? header.getBoundingClientRect().height : 84;
    var gap = 32;
    return Math.max(0, scrollTarget.getBoundingClientRect().top + window.pageYOffset - (headerH + gap));
  }

  function getTeamCardMediaScrollY(media) {
    if (!media) return 0;
    var header = document.querySelector(".site-header");
    var headerH = header ? header.getBoundingClientRect().height : 84;
    return Math.max(0, media.getBoundingClientRect().top + window.pageYOffset - headerH);
  }

  function scrollToTeamCardMedia(media) {
    if (!media) return;
    forceInstantScroll(getTeamCardMediaScrollY(media));
    requestAnimationFrame(function () {
      forceInstantScroll(getTeamCardMediaScrollY(media));
    });
  }

  function getTeamListFirstMedia(list) {
    if (!list) return null;
    var card = list.querySelector("li:not(.brt-home-team__card--more)") || list.querySelector("li");
    return card ? card.querySelector(".brt-card__media") : null;
  }

  function scrollToTeamSectionHeaderInstant(section) {
    if (!section) return;
    revealHashTargetContent(section);
    forceInstantScroll(getTeamSectionScrollY(section));
  }

  function collapseTeamExpand(list, more) {
    var root = document.documentElement;
    var anchorPrev = root.style.overflowAnchor;
    root.style.overflowAnchor = "none";
    more.forEach(function (item) {
      item.hidden = true;
    });
    var media = getTeamListFirstMedia(list);
    scrollToTeamCardMedia(media);
    requestAnimationFrame(function () {
      scrollToTeamCardMedia(media);
      root.style.overflowAnchor = anchorPrev;
    });
  }

  function resolveTeamExpandScrollSection(list) {
    if (!list) return null;
    return list.closest("#home-team") || list.closest("#ueber-uns-team") || list.closest("#about-team") || list.closest("section");
  }

  function revealTeamExpandForTarget(target) {
    if (!target || !target.classList.contains("brt-home-team__card--more")) return;
    var list = target.closest("ul");
    if (!list || !list.id) return;
    var btn = document.querySelector('.brt-home-team__toggle[aria-controls="' + list.id + '"]');
    list.querySelectorAll(".brt-home-team__card--more").forEach(function (el) {
      el.hidden = false;
    });
    if (btn) {
      btn.setAttribute("aria-expanded", "true");
      btn.textContent = btn.getAttribute("data-less-label") || "Show less";
    }
  }

  function initCaseStudies() {
    document.querySelectorAll("[data-case-studies]").forEach(function (root) {
      var panels = Array.prototype.slice.call(root.querySelectorAll("[data-case-study-panel]"));
      var tabs = Array.prototype.slice.call(root.querySelectorAll("[data-case-study-tab]"));
      var prevBtn = root.querySelector("[data-case-study-prev]");
      var nextBtn = root.querySelector("[data-case-study-next]");
      if (!panels.length) return;

      var current = 0;

      function show(index) {
        current = (index + panels.length) % panels.length;
        panels.forEach(function (panel, i) {
          var active = i === current;
          panel.hidden = !active;
          panel.classList.toggle("is-active", active);
        });
        tabs.forEach(function (tab, i) {
          var active = i === current;
          tab.classList.toggle("is-active", active);
          tab.setAttribute("aria-selected", active ? "true" : "false");
          tab.tabIndex = active ? 0 : -1;
        });
      }

      tabs.forEach(function (tab, i) {
        tab.addEventListener("click", function () {
          show(i);
        });
      });

      if (prevBtn) {
        prevBtn.addEventListener("click", function () {
          show(current - 1);
        });
      }

      if (nextBtn) {
        nextBtn.addEventListener("click", function () {
          show(current + 1);
        });
      }

      root.addEventListener("keydown", function (e) {
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          show(current - 1);
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          show(current + 1);
        }
      });

      show(0);
    });
  }

  function initTestimonialsCarousel() {
    document.querySelectorAll("[data-testimonials-carousel]").forEach(function (carousel) {
      var viewport = carousel.querySelector(".brt-testimonials__viewport");
      var track = carousel.querySelector(".brt-testimonials__track");
      var prevBtn = carousel.querySelector(".brt-testimonials__btn--prev");
      var nextBtn = carousel.querySelector(".brt-testimonials__btn--next");
      if (!viewport || !track) return;

      function scrollStep() {
        var card = track.querySelector(".brt-testimonial-card");
        if (!card) return viewport.clientWidth;
        var gap = parseFloat(getComputedStyle(track).gap) || 24;
        return card.offsetWidth + gap;
      }

      function scrollBy(direction) {
        viewport.scrollBy({
          left: direction * scrollStep(),
          behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        });
      }

      function updateButtons() {
        if (!prevBtn || !nextBtn) return;
        var maxScroll = viewport.scrollWidth - viewport.clientWidth;
        prevBtn.disabled = viewport.scrollLeft <= 1;
        nextBtn.disabled = viewport.scrollLeft >= maxScroll - 1;
      }

      if (prevBtn) {
        prevBtn.addEventListener("click", function () {
          scrollBy(-1);
        });
      }

      if (nextBtn) {
        nextBtn.addEventListener("click", function () {
          scrollBy(1);
        });
      }

      viewport.addEventListener("scroll", updateButtons, { passive: true });
      viewport.addEventListener("keydown", function (e) {
        if (e.key === "ArrowLeft") {
          e.preventDefault();
          scrollBy(-1);
        } else if (e.key === "ArrowRight") {
          e.preventDefault();
          scrollBy(1);
        }
      });
      window.addEventListener("resize", updateButtons);
      updateButtons();
    });
  }

  function initTeamExpandToggle() {
    document.querySelectorAll(".brt-home-team__toggle").forEach(function (btn) {
      if (btn.dataset.teamExpandBound) return;
      btn.dataset.teamExpandBound = "true";

      btn.addEventListener("click", function () {
        var controlsId = btn.getAttribute("aria-controls");
        var list = controlsId ? document.getElementById(controlsId) : document.getElementById("home-team-cards");
        if (!list) return;
        var more = list.querySelectorAll(".brt-home-team__card--more");
        if (!more.length) return;
        var scrollSection = resolveTeamExpandScrollSection(list);
        var expanded = btn.getAttribute("aria-expanded") === "true";
        var next = !expanded;
        btn.setAttribute("aria-expanded", next ? "true" : "false");
        btn.textContent = next
          ? btn.getAttribute("data-less-label") || "Show less"
          : btn.getAttribute("data-more-label") || "Show more";
        if (next) {
          more.forEach(function (item) {
            item.hidden = false;
          });
          var media = more[0] ? more[0].querySelector(".brt-card__media") : null;
          scrollToTeamCardMedia(media);
        } else if (scrollSection) {
          btn.blur();
          collapseTeamExpand(list, more);
        } else {
          more.forEach(function (item) {
            item.hidden = true;
          });
        }
      });
    });
  }

  function initTeamBioToggle() {
    document.querySelectorAll(".brt-team-bio__toggle").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var bio = btn.closest(".brt-team-bio");
        if (!bio) return;
        var more = bio.querySelector(".brt-team-bio__more");
        if (!more) return;
        var section = bio.closest("section[id]");
        var expanded = btn.getAttribute("aria-expanded") === "true";
        var next = !expanded;
        more.hidden = !next;
        btn.setAttribute("aria-expanded", next ? "true" : "false");
        btn.textContent = next
          ? btn.getAttribute("data-less-label") || "Show less"
          : btn.getAttribute("data-more-label") || "Show more";
        if (!next) {
          scheduleTeamSectionScroll(section);
        }
      });
    });
  }

  function stepsFlowSvgPoint(svg, el, anchor) {
    var svgRect = svg.getBoundingClientRect();
    if (!svgRect.width || !svgRect.height) return null;
    var vb = svg.viewBox.baseVal;
    var vbW = vb.width || 640;
    var vbH = vb.height || 400;
    var r = el.getBoundingClientRect();
    var x = r.left + r.width / 2 - svgRect.left;
    var y = anchor === "top" ? r.top - svgRect.top + 3 : r.top + r.height / 2 - svgRect.top;
    return {
      x: (x / svgRect.width) * vbW,
      y: (y / svgRect.height) * vbH
    };
  }

  function buildStepsFlowPathD(p1, p2, p3, arcOffset) {
    var offset = arcOffset || 72;
    var arcY = Math.min(p1.y, p2.y, p3.y) - offset;
    if (arcY < 20) arcY = 20;
    var mid12 = (p1.x + p2.x) / 2;
    var mid23 = (p2.x + p3.x) / 2;
    return "M " + p1.x + " " + p1.y +
      " C " + p1.x + " " + arcY + ", " + mid12 + " " + arcY + ", " + p2.x + " " + p2.y +
      " S " + mid23 + " " + arcY + ", " + p3.x + " " + p3.y;
  }

  function stepsFlowPathHitsCopy(pathEl, copyRects, samples) {
    var hits = 0;
    var total = pathEl.getTotalLength();
    for (var i = 0; i <= samples; i++) {
      var pt = pathEl.getPointAtLength((total * i) / samples);
      copyRects.forEach(function (rect) {
        if (pt.x >= rect.left && pt.x <= rect.right && pt.y >= rect.top && pt.y <= rect.bottom) {
          hits++;
        }
      });
    }
    return hits;
  }

  function layoutStepsFlowDiagram(diagram, state) {
    var svg = diagram.querySelector(".brt-steps-flow__path");
    var platforms = diagram.querySelectorAll(".brt-steps-flow__platform");
    var basePath = diagram.querySelector(".brt-steps-flow__path-base");
    var progressPath = diagram.querySelector(".brt-steps-flow__path-progress");
    var softPath = diagram.querySelector(".brt-steps-flow__path-soft");
    if (!svg || platforms.length < 3 || !basePath || !progressPath) return false;

    if (softPath) {
      softPath.style.display = "none";
    }

    var p1 = stepsFlowSvgPoint(svg, platforms[0], "top");
    var p2 = stepsFlowSvgPoint(svg, platforms[1], "top");
    var p3 = stepsFlowSvgPoint(svg, platforms[2], "top");
    if (!p1 || !p2 || !p3) return false;

    var svgRect = svg.getBoundingClientRect();
    var vb = svg.viewBox.baseVal;
    var copyRects = [];
    diagram.querySelectorAll(".brt-steps-flow__copy").forEach(function (copy) {
      var r = copy.getBoundingClientRect();
      copyRects.push({
        left: ((r.left - svgRect.left) / svgRect.width) * vb.width,
        right: ((r.right - svgRect.left) / svgRect.width) * vb.width,
        top: ((r.top - svgRect.top) / svgRect.height) * vb.height,
        bottom: ((r.bottom - svgRect.top) / svgRect.height) * vb.height
      });
    });

    var hitCount = 0;
    var arcOffset = 72;
    for (var attempt = 0; attempt < 5; attempt++) {
      var d = buildStepsFlowPathD(p1, p2, p3, arcOffset);
      basePath.setAttribute("d", d);
      progressPath.setAttribute("d", d);
      state.mainLength = progressPath.getTotalLength();
      hitCount = stepsFlowPathHitsCopy(progressPath, copyRects, 40);
      if (hitCount === 0) break;
      arcOffset += 28;
    }

    progressPath.style.strokeDasharray = String(state.mainLength);

    return true;
  }

  function initStepsFlowScroll() {
    var diagrams = document.querySelectorAll(".brt-steps-flow__diagram");
    if (!diagrams.length) return;

    var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var states = [];

    diagrams.forEach(function (diagram) {
      var progressPath = diagram.querySelector(".brt-steps-flow__path-progress");
      if (!progressPath) return;

      var state = {
        diagram: diagram,
        section: diagram.closest(".brt-section--steps-flow") || diagram,
        progressPath: progressPath,
        mainLength: 0,
        progress: 0
      };

      if (!layoutStepsFlowDiagram(diagram, state)) return;
      progressPath.style.strokeDashoffset = String(state.mainLength);
      states.push(state);
    });

    if (!states.length) return;

    function stepsFlowScrollProgress(state) {
      var sectionRect = state.section.getBoundingClientRect();
      var diagramRect = state.diagram.getBoundingClientRect();
      var vh = window.innerHeight;
      var isWide = window.matchMedia("(min-width: 1024px)").matches;
      var progressStartTop = isWide ? vh * 0.56 : vh * 0.6;
      var diagramOffset = diagramRect.top - sectionRect.top;
      var sectionTopWhenFull = Math.max(0, vh - sectionRect.height);
      var progressEndTop = sectionTopWhenFull + diagramOffset;
      if (isWide) {
        progressEndTop = Math.max(112, Math.min(progressEndTop, progressStartTop - 100));
      } else {
        progressEndTop = Math.max(128, Math.min(progressEndTop, progressStartTop - 80));
      }
      var range = progressStartTop - progressEndTop;
      if (range <= 0) return diagramRect.top <= progressEndTop ? 1 : 0;
      var progress = (progressStartTop - diagramRect.top) / range;
      return Math.min(Math.max(progress, 0), 1);
    }

    function update() {
      states.forEach(function (state) {
        var progress = stepsFlowScrollProgress(state);
        if (prefersReduced) {
          progress = progress >= 0.4 ? 1 : 0;
        }
        state.progress = progress;
        state.progressPath.style.strokeDashoffset = String(state.mainLength * (1 - progress));
      });
    }

    var ticking = false;
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        update();
        ticking = false;
      });
    }

    function onResize() {
      states.forEach(function (state) {
        layoutStepsFlowDiagram(state.diagram, state);
        state.progressPath.style.strokeDashoffset = String(state.mainLength * (1 - state.progress));
      });
    }

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onResize, { passive: true });
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        onResize();
        update();
      });
    });
    update();
  }

  function initCompareColumnHover() {
    var table = document.querySelector(".brt-compare__table");
    if (!table || !window.matchMedia("(hover: hover)").matches) return;

    function highlightCol(col) {
      table.querySelectorAll(".brt-compare__col-hover").forEach(function (el) {
        el.classList.remove("brt-compare__col-hover");
      });
      if (col < 2 || col > 4) return;
      table.querySelectorAll(
        "thead .brt-compare__head:nth-child(" + col + "), tbody td:nth-child(" + col + "), tfoot td:nth-child(" + col + ")"
      ).forEach(function (el) {
        el.classList.add("brt-compare__col-hover");
      });
    }

    table.addEventListener("mouseover", function (e) {
      var cell = e.target.closest("th, td");
      if (!cell || !table.contains(cell)) return;
      var col = cell.cellIndex + 1;
      highlightCol(col);
    });

    table.addEventListener("mouseleave", function () {
      highlightCol(0);
    });
  }

  function initBerateriumSite() {
    initTeamExpandToggle();
    initTeamBioToggle();
    initCaseStudies();
    initTestimonialsCarousel();
    initStepsFlowScroll();
    initCompareColumnHover();

    if (location.hash) {
      if ("scrollRestoration" in history) history.scrollRestoration = "manual";
      window.scrollTo(0, 0);
    }

    var root = document.querySelector(".brt");
    var header = document.querySelector(".site-header");
    var navToggle = document.querySelector(".site-header__toggle");
    var nav = document.querySelector("#site-nav");
    var prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var menuMq = window.matchMedia("(min-width: 1024px)");
    var isInnerPage = document.body.classList.contains("brt-page--inner");

    function syncHeaderHeight() {
      if (!header) return;
      document.documentElement.style.setProperty("--header-height", header.offsetHeight + "px");
    }

    function updateHeaderState() {
      if (!header) return;
      if (isInnerPage) {
        header.classList.add("site-header--solid");
        syncHeaderHeight();
        return;
      }
      var shouldBeSolid = window.scrollY > 20 || (nav && nav.classList.contains("is-open"));
      header.classList.toggle("site-header--solid", shouldBeSolid);
      syncHeaderHeight();
    }

    if (navToggle && nav) {
      function closeMobileNav() {
        navToggle.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
        document.body.classList.remove("is-nav-open");
        if (header) header.classList.remove("site-header--menu-open");
        document.querySelectorAll(".site-header__item--has-menu.is-submenu-open").forEach(function (item) {
          item.classList.remove("is-submenu-open");
          var link = item.querySelector(".site-header__parent-link");
          if (link) link.setAttribute("aria-expanded", "false");
        });
        updateHeaderState();
      }

      function toggleMobileSubmenu(item, link) {
        if (!item.classList.contains("is-submenu-open")) {
          document.querySelectorAll(".site-header__item--has-menu.is-submenu-open").forEach(function (openItem) {
            if (openItem === item) return;
            openItem.classList.remove("is-submenu-open");
            var openLink = openItem.querySelector(".site-header__parent-link");
            if (openLink) openLink.setAttribute("aria-expanded", "false");
          });
          item.classList.add("is-submenu-open");
          link.setAttribute("aria-expanded", "true");
        } else {
          item.classList.remove("is-submenu-open");
          link.setAttribute("aria-expanded", "false");
        }
      }

      navToggle.addEventListener("click", function () {
        var expanded = navToggle.getAttribute("aria-expanded") === "true";
        navToggle.setAttribute("aria-expanded", expanded ? "false" : "true");
        nav.classList.toggle("is-open", !expanded);
        document.body.classList.toggle("is-nav-open", !expanded);
        if (header) header.classList.toggle("site-header--menu-open", !expanded);
        if (expanded) {
          document.querySelectorAll(".site-header__item--has-menu.is-submenu-open").forEach(function (item) {
            item.classList.remove("is-submenu-open");
            var link = item.querySelector(".site-header__parent-link");
            if (link) link.setAttribute("aria-expanded", "false");
          });
        }
        updateHeaderState();
      });

      nav.addEventListener("click", function (e) {
        if (menuMq.matches) return;
        var link = e.target.closest("a[href]");
        if (!link || !nav.contains(link)) return;

        if (link.classList.contains("site-header__parent-link")) {
          e.preventDefault();
          e.stopPropagation();
          var item = link.closest(".site-header__item--has-menu");
          if (!item) return;
          toggleMobileSubmenu(item, link);
          return;
        }

        closeMobileNav();
      }, true);

      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && nav.classList.contains("is-open")) closeMobileNav();
      });

      menuMq.addEventListener("change", function () {
        if (menuMq.matches) closeMobileNav();
      });
    }

    document.querySelectorAll(".site-header__item--has-menu").forEach(function (item) {
      var link = item.querySelector(".site-header__parent-link");
      if (!link) return;

      function syncDesktopExpanded() {
        if (!menuMq.matches) return;
        var hovered = item.matches(":hover") || item.matches(":focus-within");
        link.setAttribute("aria-expanded", hovered ? "true" : "false");
      }

      item.addEventListener("mouseenter", syncDesktopExpanded);
      item.addEventListener("mouseleave", syncDesktopExpanded);
      item.addEventListener("focusin", syncDesktopExpanded);
      item.addEventListener("focusout", syncDesktopExpanded);
    });

    window.addEventListener("scroll", updateHeaderState, { passive: true });
    window.addEventListener("resize", updateHeaderState, { passive: true });
    updateHeaderState();

    if (location.hash) {
      scheduleAnchorScroll();
      window.addEventListener("load", scheduleAnchorScroll);
    }
    window.addEventListener("hashchange", scheduleAnchorScroll);

    if (!root) return;

    root.querySelectorAll(".brt-legal, .brt-hero .brt-fade-up").forEach(function (el) {
      el.classList.add("is-visible");
    });

    function reveal(entries, observer) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        if (entry.target.classList.contains("brt-stagger")) {
          Array.prototype.forEach.call(entry.target.children, function (child, i) {
            child.style.transitionDelay = i * 80 + "ms";
            child.classList.add("is-visible");
          });
        }
        if (entry.target.querySelector(".brt-stagger")) {
          var stagger = entry.target.querySelector(".brt-stagger");
          Array.prototype.forEach.call(stagger.children, function (child, i) {
            child.style.transitionDelay = i * 80 + "ms";
            child.classList.add("is-visible");
          });
        }
        observer.unobserve(entry.target);
      });
    }

    if (!prefersReduced && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(reveal, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
      root.querySelectorAll(".brt-fade-up, .brt-stagger").forEach(function (el) {
        if (el.closest(".brt-hero")) return;
        io.observe(el);
      });
      root.querySelectorAll(".brt-stagger > *").forEach(function (el) {
        if (el.closest(".brt-hero")) return;
        io.observe(el);
      });
    } else {
      root.querySelectorAll(".brt-fade-up, .brt-stagger > *").forEach(function (el) {
        el.classList.add("is-visible");
      });
    }

    if (!prefersReduced) {
      root.querySelectorAll("[data-count]").forEach(function (el) {
        var target = parseInt(el.getAttribute("data-count"), 10);
        var suffix = el.getAttribute("data-suffix") || "";
        if (isNaN(target)) return;

        var counted = false;
        function animateCount() {
          if (counted) return;
          counted = true;
          var start = performance.now();
          var duration = 1200;
          function tick(now) {
            var p = Math.min((now - start) / duration, 1);
            el.textContent = Math.round(target * p) + suffix;
            if (p < 1) requestAnimationFrame(tick);
          }
          requestAnimationFrame(tick);
        }

        if ("IntersectionObserver" in window) {
          var statIo = new IntersectionObserver(function (entries, obs) {
            if (entries[0].isIntersecting) {
              animateCount();
              obs.disconnect();
            }
          }, { threshold: 0.5 });
          statIo.observe(el);
        }
      });
    }

    var filters = document.querySelector(".brt-blog-filters");
    var grid = document.getElementById("blog-grid-list");
    if (filters && grid) {
      filters.addEventListener("click", function (e) {
        var link = e.target.closest("a[data-filter]");
        if (!link) return;
        e.preventDefault();
        var filter = link.getAttribute("data-filter");
        filters.querySelectorAll("a").forEach(function (a) {
          a.classList.toggle("is-active", a === link);
        });
        grid.querySelectorAll("[data-category]").forEach(function (card) {
          var cat = card.getAttribute("data-category");
          card.hidden = !(filter === "alle" || cat === filter);
        });
      });
    }

    initArticlePage();
    initYoutubeEmbeds();
    initAnchorNav();
    initCalendlyEmbed();
    initContactForm();
  }

  function prefersReducedMotion() {
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function getArticleStickyBarHeight(stickyBar) {
    if (!stickyBar) return 0;
    if (stickyBar.dataset.layoutHeight) return parseFloat(stickyBar.dataset.layoutHeight);
    if (stickyBar.offsetHeight) return stickyBar.offsetHeight;
    return 55;
  }

  function cacheArticleStickyBarHeight(stickyBar) {
    if (!stickyBar || stickyBar.dataset.layoutHeight) return;
    var wasHidden = stickyBar.hidden;
    stickyBar.hidden = false;
    stickyBar.dataset.layoutHeight = String(Math.round(stickyBar.getBoundingClientRect().height));
    if (wasHidden) stickyBar.hidden = true;
  }

  function scrollWithOffset(target, behavior) {
    if (!target) return;
    var header = document.querySelector(".site-header");
    var stickyBar = document.querySelector("[data-article-sticky-bar]");
    var scrollMarginTop = parseFloat(window.getComputedStyle(target).scrollMarginTop);
    var headerH = header ? header.getBoundingClientRect().height : 84;
    var stickyH = getArticleStickyBarHeight(stickyBar);
    var offset = scrollMarginTop > 0 ? scrollMarginTop : headerH + stickyH + 16;
    var y = target.getBoundingClientRect().top + window.pageYOffset - offset;
    window.scrollTo({
      top: Math.max(0, y),
      behavior: behavior || (prefersReducedMotion() ? "auto" : "smooth"),
    });
  }

  function initAnchorNav() {
    var nav = document.querySelector("[data-anchor-nav]");
    if (!nav) return;

    var links = nav.querySelectorAll('a[href^="#"]');
    if (!links.length) return;

    var headings = [];
    links.forEach(function (link) {
      var id = link.getAttribute("href").slice(1);
      var el = document.getElementById(id);
      if (el) headings.push({ link: link, el: el });
    });
    if (!headings.length) return;

    function anchorScrollOffset() {
      var header = document.querySelector(".site-header");
      var headerH = header ? header.getBoundingClientRect().height : 84;
      return headerH + nav.getBoundingClientRect().height + 16;
    }

    function scrollToSection(target) {
      if (!target) return;
      var y = target.getBoundingClientRect().top + window.pageYOffset - anchorScrollOffset();
      window.scrollTo({
        top: Math.max(0, y),
        behavior: prefersReducedMotion() ? "auto" : "smooth",
      });
    }

    function setActive(activeLink) {
      links.forEach(function (link) {
        var isActive = link === activeLink;
        link.classList.toggle("is-active", isActive);
        if (isActive) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
      if (activeLink) {
        activeLink.scrollIntoView({
          block: "nearest",
          inline: "center",
          behavior: prefersReducedMotion() ? "auto" : "smooth",
        });
      }
    }

    if ("IntersectionObserver" in window) {
      var visible = new Map();
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) visible.set(entry.target, entry.intersectionRatio);
            else visible.delete(entry.target);
          });
          if (!visible.size) return;
          var best = null;
          var bestRatio = -1;
          visible.forEach(function (ratio, el) {
            if (ratio >= bestRatio) {
              bestRatio = ratio;
              best = el;
            }
          });
          if (!best) return;
          headings.forEach(function (item) {
            if (item.el === best) setActive(item.link);
          });
        },
        { rootMargin: "-22% 0px -52% 0px", threshold: [0, 0.25, 0.5, 0.75, 1] }
      );
      headings.forEach(function (item) {
        observer.observe(item.el);
      });
    } else {
      setActive(headings[0].link);
    }

    links.forEach(function (link, index) {
      link.addEventListener("click", function (e) {
        var id = link.getAttribute("href").slice(1);
        var target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        scrollToSection(target);
        setActive(link);
        if (history.replaceState) history.replaceState(null, "", "#" + id);
        else location.hash = id;
      });

      link.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowRight") next = links[index + 1];
        else if (e.key === "ArrowLeft") next = links[index - 1];
        else if (e.key === "Home") next = links[0];
        else if (e.key === "End") next = links[links.length - 1];
        if (!next) return;
        e.preventDefault();
        next.focus();
      });
    });
  }

  function initContactForm() {
    var form = document.querySelector(".brt-form--contact");
    if (!form) return;

    var agb = form.querySelector("#agb_accepted");
    var privacy = form.querySelector("#privacy_accepted");
    var agbError = form.querySelector("#agb-error");
    var privacyError = form.querySelector("#privacy-error");
    if (!agb || !privacy || !agbError || !privacyError) return;

    function setCheckError(input, errorEl, label, show) {
      label.classList.toggle("is-invalid", show);
      input.setAttribute("aria-invalid", show ? "true" : "false");
      if (show) errorEl.removeAttribute("hidden");
      else errorEl.setAttribute("hidden", "");
    }

    function validateChecks() {
      var agbOk = agb.checked;
      var privacyOk = privacy.checked;
      setCheckError(agb, agbError, agb.closest(".brt-form__check"), !agbOk);
      setCheckError(privacy, privacyError, privacy.closest(".brt-form__check"), !privacyOk);
      return agbOk && privacyOk;
    }

    [agb, privacy].forEach(function (input) {
      input.addEventListener("change", function () {
        if (input.checked) {
          var errorEl = input.id === "agb_accepted" ? agbError : privacyError;
          setCheckError(input, errorEl, input.closest(".brt-form__check"), false);
        }
      });
    });

    form.addEventListener("submit", function (e) {
      if (!form.checkValidity()) {
        e.preventDefault();
        form.reportValidity();
        return;
      }
      if (!validateChecks()) {
        e.preventDefault();
        if (!agb.checked) agb.focus();
        else if (!privacy.checked) privacy.focus();
      }
    });
  }

  function initCalendlyEmbed() {
    var embed = document.querySelector("[data-calendly-embed]");
    if (!embed) return;

    var widget = embed.querySelector(".calendly-inline-widget");
    if (!widget) return;

    function setWidgetHeight(height) {
      if (!height || height < 400) return;
      widget.style.height = Math.ceil(height) + "px";
    }

    window.addEventListener("message", function (e) {
      if (e.origin !== "https://calendly.com") return;
      if (!e.data || !e.data.event) return;
      if (e.data.event === "calendly.page_height" && e.data.payload && e.data.payload.height) {
        setWidgetHeight(e.data.payload.height);
      }
    });
  }

  function initKeypointsLinks(article) {
    var links = (article || document).querySelectorAll(".brt-article__keypoints-link");
    if (!links.length) return;

    links.forEach(function (link) {
      link.addEventListener("click", function (e) {
        var id = link.getAttribute("href").slice(1);
        var target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        scrollWithOffset(target);
      });
    });
  }

  function initArticlePage() {
    var article = document.querySelector("[data-article]");
    if (!article) return;
    initArticleStickyBar(article);
    initArticleProgress(article);
    initArticleBackTop(article);
    initArticleToc(article);
    initKeypointsLinks(article);
  }

  function initYoutubeEmbeds() {
    var wraps = document.querySelectorAll("[data-youtube-embed]");
    if (!wraps.length) return;

    wraps.forEach(function (wrap) {
      if (wrap.dataset.youtubeReady) return;
      wrap.dataset.youtubeReady = "true";

      var poster = wrap.querySelector(".brt-article__video-poster");
      var videoId = wrap.getAttribute("data-youtube-id");
      var title = wrap.getAttribute("data-youtube-title") || "YouTube video";
      if (!poster || !videoId) return;

      poster.addEventListener("click", function () {
        if (wrap.querySelector("iframe")) return;

        var src = buildYoutubeEmbedSrc(videoId, wrap);

        var iframe = document.createElement("iframe");
        iframe.src = src;
        iframe.title = title;
        iframe.setAttribute(
          "allow",
          "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        );
        iframe.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
        iframe.setAttribute("allowfullscreen", "");

        wrap.classList.add("brt-article__video-wrap--playing");
        wrap.replaceChild(iframe, poster);
      });
    });
  }

  function getYoutubeEmbedOrigin() {
    if (location.protocol === "http:" || location.protocol === "https:") {
      return location.origin;
    }
    return "";
  }

  function getYoutubeWidgetReferrer(wrap) {
    if (location.protocol === "http:" || location.protocol === "https:") {
      return location.href.split("#")[0];
    }
    return wrap.getAttribute("data-youtube-page") || "https://www.beraterium.de/";
  }

  function buildYoutubeEmbedSrc(videoId, wrap) {
    var origin = getYoutubeEmbedOrigin();
    var referrer = getYoutubeWidgetReferrer(wrap);
    var params = ["autoplay=1", "rel=0", "widget_referrer=" + encodeURIComponent(referrer)];
    if (origin) {
      params.push("origin=" + encodeURIComponent(origin));
    }
    return "https://www.youtube.com/embed/" + videoId + "?" + params.join("&");
  }

  function initArticleStickyBar(article) {
    var bar = article.querySelector("[data-article-sticky-bar]");
    var hero = article.querySelector("[data-article-hero]");
    var main = article.querySelector(".brt-article__main");
    if (!bar || !hero) return;

    var header = document.querySelector(".site-header");

    cacheArticleStickyBarHeight(bar);

    function syncStickyBarTop() {
      if (!header) return;
      bar.style.top = Math.round(header.getBoundingClientRect().bottom) + "px";
    }

    var ticking = false;
    function update() {
      ticking = false;
      syncStickyBarTop();
      var scrollY = window.pageYOffset;
      var heroBottom = hero.getBoundingClientRect().bottom + scrollY;
      var pastHero = scrollY > heroBottom - 80;

      var inText = false;
      if (main) {
        var mainRect = main.getBoundingClientRect();
        var mainTop = mainRect.top + scrollY;
        var mainBottom = mainTop + main.offsetHeight;
        var headerH = header ? header.getBoundingClientRect().height : 84;
        var readStart = scrollY + headerH + 48;
        inText = mainBottom > readStart && mainTop < scrollY + window.innerHeight;
      } else {
        inText = pastHero;
      }

      var show = pastHero && inText;
      bar.hidden = !show;
      article.toggleAttribute("data-sticky-visible", show);
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
  }

  function initArticleProgress(article) {
    var barWrap = article.querySelector("[data-article-progress]");
    var bar = barWrap && barWrap.querySelector(".brt-article__progress-bar");
    var body = document.getElementById("article-body");
    if (!barWrap || !bar || !body) return;

    var ticking = false;
    function update() {
      ticking = false;
      var rect = body.getBoundingClientRect();
      var bodyTop = rect.top + window.pageYOffset;
      var bodyHeight = body.offsetHeight;
      var viewport = window.innerHeight;
      var scrollY = window.pageYOffset;
      var start = bodyTop - viewport * 0.15;
      var end = bodyTop + bodyHeight - viewport * 0.5;
      var range = Math.max(end - start, 1);
      var progress = Math.min(Math.max((scrollY - start) / range, 0), 1);
      bar.style.width = (progress * 100).toFixed(1) + "%";
      var hero = article.querySelector("[data-article-hero]");
      var heroBottom = hero
        ? hero.getBoundingClientRect().bottom + window.pageYOffset
        : bodyTop;
      article.toggleAttribute("data-scrolled", scrollY > heroBottom - 120);
    }

    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }

    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
  }

  function initArticleBackTop(article) {
    var btn = document.querySelector("[data-article-back-top]");
    var body = document.getElementById("article-body");
    if (!btn || !body) return;

    function toggle() {
      var show = window.pageYOffset > body.getBoundingClientRect().top + window.pageYOffset + 400;
      btn.hidden = !show;
    }

    toggle();
    window.addEventListener("scroll", toggle, { passive: true });

    btn.addEventListener("click", function () {
      window.scrollTo({
        top: 0,
        behavior: prefersReducedMotion() ? "auto" : "smooth",
      });
      btn.blur();
    });
  }

  function initArticleToc(article) {
    var toc = (article || document).querySelector("[data-article-toc]");
    if (!toc) return;

    var details = toc.querySelector(".brt-article__toc-details");
    var desktopMq = window.matchMedia("(min-width: 1024px)");

    function syncTocOpen() {
      if (!details) return;
      if (desktopMq.matches) {
        details.setAttribute("open", "");
      } else if (!details.dataset.userToggled) {
        details.removeAttribute("open");
      }
    }

    if (details) {
      syncTocOpen();
      desktopMq.addEventListener("change", syncTocOpen);
      details.addEventListener("toggle", function () {
        if (!desktopMq.matches) details.dataset.userToggled = "1";
      });
    }

    var links = toc.querySelectorAll('a[href^="#"]');
    if (!links.length) return;

    var headings = [];
    links.forEach(function (link) {
      var id = link.getAttribute("href").slice(1);
      var el = document.getElementById(id);
      if (el) headings.push({ link: link, el: el });
    });
    if (!headings.length) return;

    function setActive(activeLink) {
      links.forEach(function (link) {
        var isActive = link === activeLink;
        link.classList.toggle("is-active", isActive);
        if (isActive) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
      if (activeLink && desktopMq.matches) {
        activeLink.scrollIntoView({ block: "nearest" });
      }
    }

    if ("IntersectionObserver" in window) {
      var visible = new Map();
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) visible.set(entry.target, entry.intersectionRatio);
            else visible.delete(entry.target);
          });
          if (!visible.size) return;
          var best = null;
          var bestRatio = -1;
          visible.forEach(function (ratio, el) {
            if (ratio >= bestRatio) {
              bestRatio = ratio;
              best = el;
            }
          });
          if (!best) return;
          headings.forEach(function (item) {
            if (item.el === best) setActive(item.link);
          });
        },
        { rootMargin: "-20% 0px -55% 0px", threshold: [0, 0.25, 0.5, 0.75, 1] }
      );
      headings.forEach(function (item) {
        observer.observe(item.el);
      });
    }

    links.forEach(function (link, index) {
      link.addEventListener("click", function (e) {
        var id = link.getAttribute("href").slice(1);
        var target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        scrollWithOffset(target);
        setActive(link);
        if (details && !desktopMq.matches) details.removeAttribute("open");
      });

      link.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowDown") next = links[index + 1];
        else if (e.key === "ArrowUp") next = links[index - 1];
        else if (e.key === "Home") next = links[0];
        else if (e.key === "End") next = links[links.length - 1];
        if (!next) return;
        e.preventDefault();
        next.focus();
      });
    });
  }

  initFileProtocolLinks();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initBerateriumSite);
  } else {
    initBerateriumSite();
  }
})();
