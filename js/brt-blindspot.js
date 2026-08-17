/* Beraterium Blindspot Quick Check 2.0
 * Liest die Konfiguration aus <script type="application/json" id="brt-blindspot-config">
 * (erzeugt von _blindspot.py) und rendert den Check in #brt-blindspot.
 * Auswertung komplett client-seitig; submitUrl/reportUrl (Google Apps Script)
 * sind optional — ohne Backend läuft der Check degradiert weiter.
 */
(function () {
  "use strict";

  var root = document.getElementById("brt-blindspot");
  var configEl = document.getElementById("brt-blindspot-config");
  if (!root || !configEl) return;

  var CFG;
  try {
    CFG = JSON.parse(configEl.textContent);
  } catch (e) {
    return;
  }

  var S = CFG.strings;

  function track(name, params) {
    if (typeof window.brtTrack === "function") window.brtTrack(name, params);
  }

  var state = {
    segment: null,      /* Segment-Objekt */
    questions: [],      /* Fragen des gewählten Segments */
    pages: [],          /* Fragen in Seiten à questionsPerPage */
    pageIdx: 0,
    answers: {},        /* qid -> { severity: 0-3, measure: 0|1 } */
    submissionId: "",
    result: null
  };

  /* ------------------------------------------------------------------ */
  /* Helpers                                                             */
  /* ------------------------------------------------------------------ */

  function el(tag, className, html) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (html != null) node.innerHTML = html;
    return node;
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function uuid() {
    if (window.crypto && typeof window.crypto.randomUUID === "function") {
      return window.crypto.randomUUID();
    }
    return "bqc-" + Date.now() + "-" + Math.random().toString(16).slice(2);
  }

  function scrollToRoot() {
    var y = root.getBoundingClientRect().top + window.pageYOffset - 96;
    try {
      window.scrollTo({ top: y < 0 ? 0 : y, behavior: "auto" });
    } catch (e) {
      window.scrollTo(0, y < 0 ? 0 : y);
    }
  }

  function scrollToEl(el) {
    if (!el) return;
    var header = document.querySelector(".site-header");
    var headerH = header ? header.getBoundingClientRect().height : 96;
    var y = el.getBoundingClientRect().top + window.pageYOffset - (headerH + 20);
    try {
      window.scrollTo({ top: y < 0 ? 0 : y, behavior: "smooth" });
    } catch (e) {
      window.scrollTo(0, y < 0 ? 0 : y);
    }
  }

  function focusHeading(view) {
    var h = view.querySelector("h2, h3");
    if (!h) return;
    h.setAttribute("tabindex", "-1");
    try { h.focus({ preventScroll: true }); } catch (e) { /* no-op */ }
  }

  var isFirstView = true;

  function setView(node) {
    root.innerHTML = "";
    root.appendChild(node);
    // Views are inserted after load, so the site's IntersectionObserver never
    // sees them — reveal the fade-up state directly.
    if (node.classList.contains("brt-fade-up")) node.classList.add("is-visible");
    // ponytail: skip scroll on initial page load so the hero stays visible; scroll on in-check navigation only
    if (!isFirstView) scrollToRoot();
    isFirstView = false;
    focusHeading(node);
  }

  function questionById(id) {
    for (var i = 0; i < CFG.questions.length; i++) {
      if (CFG.questions[i].id === id) return CFG.questions[i];
    }
    return null;
  }

  function pickField(q, field, segmentId) {
    if (!q) return "";
    if (segmentId === "solo" && q[field + "_solo"]) return q[field + "_solo"];
    if (segmentId === "gruender" && q[field + "_gruender"]) return q[field + "_gruender"];
    if (segmentId === "kmu" && q[field + "_kmu"]) return q[field + "_kmu"];
    return q[field] != null ? q[field] : "";
  }

  function resolveQuestion(q, segmentId) {
    if (!q) return q;
    return {
      id: q.id,
      cat: q.cat,
      text: pickField(q, "text", segmentId),
      short: pickField(q, "short", segmentId),
      why: pickField(q, "why", segmentId),
      step: pickField(q, "step", segmentId)
    };
  }

  function chunk(arr, size) {
    var out = [];
    for (var i = 0; i < arr.length; i += size) out.push(arr.slice(i, i + size));
    return out;
  }

  /* ------------------------------------------------------------------ */
  /* Scoring                                                             */
  /* ------------------------------------------------------------------ */

  function lightFor(points) {
    if (points <= CFG.trafficLight.green_max) return "green";
    if (points <= CFG.trafficLight.yellow_max) return "yellow";
    return "red";
  }

  function computeResult() {
    var total = 0;
    var perQuestion = [];
    var perCategory = {}; /* cat -> {points, max} */
    var counts = { green: 0, yellow: 0, red: 0 };

    state.questions.forEach(function (q) {
      var a = state.answers[q.id];
      var pts = a.severity + a.measure;
      total += pts;
      var light = lightFor(pts);
      counts[light] += 1;
      perQuestion.push({ id: q.id, points: pts, light: light });
      if (!perCategory[q.cat]) perCategory[q.cat] = { points: 0, max: 0 };
      perCategory[q.cat].points += pts;
      perCategory[q.cat].max += CFG.maxPointsPerQuestion;
    });

    var max = state.questions.length * CFG.maxPointsPerQuestion;
    var pct = max ? Math.round((total / max) * 100) : 0;
    var band = CFG.resultBands[CFG.resultBands.length - 1];
    for (var i = 0; i < CFG.resultBands.length; i++) {
      if (pct <= CFG.resultBands[i].max_pct) { band = CFG.resultBands[i]; break; }
    }

    return {
      totalPoints: total,
      maxPoints: max,
      percent: pct,
      band: band,
      counts: counts,
      perQuestion: perQuestion,
      perCategory: perCategory,
      redQuestions: perQuestion
        .filter(function (pq) { return pq.light === "red"; })
        .map(function (pq) {
          for (var i = 0; i < state.questions.length; i++) {
            if (state.questions[i].id === pq.id) return state.questions[i];
          }
          return resolveQuestion(questionById(pq.id), state.segment && state.segment.id);
        })
    };
  }

  /* ------------------------------------------------------------------ */
  /* Backend (optional)                                                  */
  /* ------------------------------------------------------------------ */

  function postJson(url, payload) {
    /* text/plain vermeidet den CORS-Preflight bei Google Apps Script */
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(payload)
    }).then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json().catch(function () { return {}; });
    }).then(function (data) {
      if (!data || data.ok !== true) {
        var bad = new Error((data && data.error) || "invalid_response");
        bad.code = (data && data.error) || "invalid_response";
        throw bad;
      }
      return data;
    });
  }

  function reportErrorMessage(code) {
    if (code === "pdf_failed") return S.report_error_pdf;
    if (code === "missing_fields") return S.report_error_validation;
    if (code === "email_failed" || code === "mail_failed") return S.report_email_failed;
    return S.report_error;
  }

  function submitAnswers(result) {
    if (!CFG.submitUrl) return;
    var payload = {
      action: "submit",
      submission_id: state.submissionId,
      locale: CFG.locale,
      zielgruppe: state.segment.id,
      gesamtscore: result.totalPoints,
      max_score: result.maxPoints,
      prozent: result.percent,
      status: result.band.key,
      rote_punkte_anzahl: result.counts.red,
      gelbe_punkte_anzahl: result.counts.yellow,
      gruene_punkte_anzahl: result.counts.green,
      antworten: state.questions.map(function (q) {
        var a = state.answers[q.id];
        return { id: q.id, severity: a.severity, measure: a.measure };
      }),
      kategorien: result.perCategory,
      page_url: location.href,
      referrer: document.referrer || "",
      browser_language: navigator.language || "",
      timezone: (function () {
        try { return Intl.DateTimeFormat().resolvedOptions().timeZone || ""; }
        catch (e) { return ""; }
      })()
    };
    /* fire-and-forget: Ergebnis wird lokal berechnet, Speichern darf scheitern */
    postJson(CFG.submitUrl, payload).catch(function () { /* no-op */ });
  }

  /* ------------------------------------------------------------------ */
  /* Views                                                               */
  /* ------------------------------------------------------------------ */

  function viewIntro() {
    var v = el("div", "bqc-card brt-fade-up");
    v.appendChild(el("p", "brt-tag", "BLINDSPOT QUICK CHECK"));
    v.appendChild(el("h2", "brt-h2", esc(S.intro_headline)));
    v.appendChild(el("p", "brt-body", esc(S.howto_text)));
    v.appendChild(el("p", "bqc-note brt-body", esc(S.intro_note)));
    var btn = el("button", "brt-btn brt-btn--lg", esc(S.start_button));
    btn.type = "button";
    btn.addEventListener("click", function () { setView(viewSegment()); });
    var actions = el("div", "bqc-actions");
    actions.appendChild(btn);
    v.appendChild(actions);
    return v;
  }

  function viewSegment() {
    var v = el("div", "bqc-card brt-fade-up");
    v.appendChild(el("h2", "brt-h3", esc(S.segment_headline)));
    v.appendChild(el("p", "brt-body", esc(S.segment_text)));
    var list = el("div", "bqc-segments");
    CFG.segments.forEach(function (seg) {
      var btn = el("button", "brt-btn brt-btn--outline bqc-segment-btn", esc(seg.cta));
      btn.type = "button";
      btn.addEventListener("click", function () {
        state.segment = seg;
        state.questions = seg.question_ids.map(function (id) {
          return resolveQuestion(questionById(id), seg.id);
        });
        state.pages = chunk(state.questions, CFG.questionsPerPage);
        state.pageIdx = 0;
        state.answers = {};
        state.submissionId = uuid();
        track("blindspot_segment", {
          segment_id: seg.id || "",
          page_path: location.pathname,
        });
        setView(viewHowto());
      });
      list.appendChild(btn);
    });
    v.appendChild(list);
    return v;
  }

  function viewHowto() {
    var v = el("div", "bqc-card brt-fade-up");
    v.appendChild(el("h2", "brt-h3", esc(S.howto_headline)));
    var countText = S.howto_count_template
      .replace("{count}", state.questions.length)
      .replace("{segment}", state.segment.label);
    v.appendChild(el("p", "brt-body",
      esc(S.howto_text) + " <strong>" + esc(countText) + "</strong>"));
    v.appendChild(el("p", "bqc-note brt-body", esc(S.howto_note)));
    var btn = el("button", "brt-btn brt-btn--lg", esc(S.howto_button));
    btn.type = "button";
    btn.addEventListener("click", function () {
      track("blindspot_start", {
        segment_id: (state.segment && state.segment.id) || "",
        question_count: state.questions.length,
        page_path: location.pathname,
      });
      setView(viewQuestions());
    });
    var actions = el("div", "bqc-actions");
    actions.appendChild(btn);
    v.appendChild(actions);
    return v;
  }

  function optionGroup(name, options, legendText, selected, onChange) {
    var fs = el("fieldset", "bqc-options");
    fs.appendChild(el("legend", "bqc-options__legend", legendText));
    options.forEach(function (opt) {
      var id = name + "-" + opt.value;
      var label = el("label", "bqc-option");
      label.setAttribute("for", id);
      var input = document.createElement("input");
      input.type = "radio";
      input.name = name;
      input.id = id;
      input.value = String(opt.value);
      if (selected === opt.value) input.checked = true;
      input.addEventListener("change", function () { onChange(opt.value); });
      label.appendChild(input);
      label.appendChild(el("span", "bqc-option__label", esc(opt.label)));
      fs.appendChild(label);
    });
    return fs;
  }

  function viewQuestions() {
    var page = state.pages[state.pageIdx];
    var total = state.questions.length;
    var from = state.pageIdx * CFG.questionsPerPage + 1;
    var to = from + page.length - 1;
    var pct = Math.round((to / total) * 100);

    var v = el("div", "bqc-card brt-fade-up");

    var progress = el("div", "bqc-progress");
    progress.setAttribute("role", "status");
    var progressLabel = S.progress_template
      .replace("{from}", from).replace("{to}", to).replace("{total}", total);
    progress.appendChild(el("p", "bqc-progress__label", esc(progressLabel) + " · " + pct + "\u00a0%"));
    var track = el("div", "bqc-progress__track");
    var bar = el("div", "bqc-progress__bar");
    bar.style.transform = "scaleX(" + (pct / 100) + ")";
    track.appendChild(bar);
    progress.appendChild(track);
    v.appendChild(progress);

    var err = el("p", "brt-form__error bqc-page-error", esc(S.validation_answer));
    err.setAttribute("role", "alert");
    err.hidden = true;

    page.forEach(function (q, idx) {
      var block = el("section", "bqc-question");
      block.setAttribute("data-qid", q.id);
      var n = from + idx;
      block.appendChild(el("h3", "bqc-question__title",
        '<span class="bqc-question__num">' + n + "</span> " + esc(q.text)));
      if (!state.answers[q.id]) state.answers[q.id] = { severity: null, measure: null };
      block.appendChild(optionGroup(
        "sev-" + q.id, CFG.likert, esc(S.severity_question),
        state.answers[q.id].severity,
        function (val) { state.answers[q.id].severity = val; block.classList.remove("is-invalid"); }
      ));
      block.appendChild(optionGroup(
        "mea-" + q.id, CFG.measureOptions, esc(CFG.measureQuestion),
        state.answers[q.id].measure,
        function (val) { state.answers[q.id].measure = val; block.classList.remove("is-invalid"); }
      ));
      v.appendChild(block);
    });

    v.appendChild(err);

    var nav = el("div", "bqc-actions bqc-actions--between");
    var back = el("button", "brt-btn brt-btn--outline", esc(S.back));
    back.type = "button";
    back.addEventListener("click", function () {
      if (state.pageIdx === 0) { setView(viewSegment()); return; }
      state.pageIdx -= 1;
      setView(viewQuestions());
    });
    var isLast = state.pageIdx === state.pages.length - 1;
    var next = el("button", "brt-btn", esc(isLast ? S.evaluate : S.next));
    next.type = "button";
    next.addEventListener("click", function () {
      var missing = page.filter(function (q) {
        var a = state.answers[q.id];
        return a.severity == null || a.measure == null;
      });
      if (missing.length) {
        err.hidden = false;
        page.forEach(function (q) {
          var a = state.answers[q.id];
          var block = v.querySelector('[data-qid="' + q.id + '"]');
          if (block) block.classList.toggle("is-invalid", a.severity == null || a.measure == null);
        });
        var firstInvalid = v.querySelector(".bqc-question.is-invalid");
        if (firstInvalid) firstInvalid.scrollIntoView({ block: "center", behavior: "smooth" });
        return;
      }
      err.hidden = true;
      if (isLast) {
        setView(viewLoading());
      } else {
        state.pageIdx += 1;
        setView(viewQuestions());
      }
    });
    nav.appendChild(back);
    nav.appendChild(next);
    v.appendChild(nav);
    return v;
  }

  function viewLoading() {
    var v = el("div", "bqc-card bqc-card--center brt-fade-up");
    v.appendChild(el("div", "bqc-spinner"));
    v.appendChild(el("h2", "brt-h3", esc(S.loading_headline)));
    v.appendChild(el("p", "brt-body", esc(S.loading_text)));

    state.result = computeResult();
    submitAnswers(state.result);
    track("blindspot_complete", {
      segment_id: (state.segment && state.segment.id) || "",
      score_band: state.result.band.key,
      score_percent: state.result.percent,
      red_count: state.result.counts.red,
      yellow_count: state.result.counts.yellow,
      green_count: state.result.counts.green,
      page_path: location.pathname,
    });

    window.setTimeout(function () { setView(viewResult()); }, 3500);
    return v;
  }

  function viewResult() {
    var r = state.result;
    var v = el("div", "bqc-result brt-fade-up");

    var head = el("div", "bqc-card");
    head.appendChild(el("h2", "brt-h2", esc(S.result_headline)));
    head.appendChild(el("p", "brt-body", esc(S.result_thanks)));

    var score = el("div", "bqc-score bqc-score--" + r.band.key);
    score.appendChild(el("p", "bqc-score__pct", r.percent + "\u00a0%"));
    var scoreBody = el("div", "bqc-score__body");
    scoreBody.appendChild(el("p", "bqc-score__label", esc(r.band.label)));
    scoreBody.appendChild(el("p", "brt-body", esc(r.band.text)));
    scoreBody.appendChild(el("p", "bqc-score__lights",
      '<span class="bqc-dot bqc-dot--green"></span>' + r.counts.green +
      ' &nbsp; <span class="bqc-dot bqc-dot--yellow"></span>' + r.counts.yellow +
      ' &nbsp; <span class="bqc-dot bqc-dot--red"></span>' + r.counts.red));
    score.appendChild(scoreBody);
    head.appendChild(score);
    head.appendChild(el("p", "bqc-note brt-body", esc(S.result_disclaimer)));
    v.appendChild(head);

    /* Kategorien */
    var catCard = el("div", "bqc-card");
    catCard.appendChild(el("h3", "brt-h3", esc(S.result_categories_title)));
    Object.keys(r.perCategory).forEach(function (cat) {
      var c = r.perCategory[cat];
      var catPct = c.max ? Math.round((c.points / c.max) * 100) : 0;
      var catLight = catPct <= 25 ? "green" : catPct <= 60 ? "yellow" : "red";
      var row = el("div", "bqc-cat");
      row.appendChild(el("p", "bqc-cat__label",
        esc(CFG.categories[cat] || cat) + ' <span class="bqc-cat__pct">' + catPct + "\u00a0%</span>"));
      var t = el("div", "bqc-cat__track");
      var b = el("div", "bqc-cat__bar bqc-cat__bar--" + catLight);
      b.style.transform = "scaleX(" + (Math.max(catPct, 3) / 100) + ")";
      t.appendChild(b);
      row.appendChild(t);
      catCard.appendChild(row);
    });
    v.appendChild(catCard);

    /* Rote Punkte */
    var redCard = el("div", "bqc-card");
    redCard.appendChild(el("h3", "brt-h3", esc(S.result_red_title)));
    if (r.redQuestions.length === 0) {
      redCard.appendChild(el("p", "brt-body", esc(S.result_no_red)));
    } else {
      r.redQuestions.forEach(function (q) {
        var item = el("article", "bqc-red");
        item.appendChild(el("h4", "bqc-red__title",
          '<span class="bqc-dot bqc-dot--red" aria-hidden="true"></span> ' +
          esc(CFG.categories[q.cat] || q.cat) + ": " + esc(q.short)));
        item.appendChild(el("p", "brt-body",
          "<strong>" + esc(S.result_red_why) + "</strong> " + esc(q.why)));
        item.appendChild(el("p", "brt-body",
          "<strong>" + esc(S.result_red_step) + "</strong> " + esc(q.step)));
        redCard.appendChild(item);
      });
    }
    v.appendChild(redCard);

    /* CTAs */
    var cta = el("div", "bqc-card bqc-cta");
    var bookWrap = el("div", "bqc-cta__col");
    var book = el("a", "brt-btn brt-btn--lg", esc(S.cta_booking));
    book.href = CFG.bookingUrl;
    bookWrap.appendChild(book);
    bookWrap.appendChild(el("p", "brt-meta", esc(S.cta_booking_sub)));
    cta.appendChild(bookWrap);

    var reportWrap = el("div", "bqc-cta__col");
    if (CFG.reportUrl) {
      var rep = el("button", "brt-btn brt-btn--outline brt-btn--lg", esc(S.cta_report));
      rep.type = "button";
      rep.addEventListener("click", function () {
        var existing = v.querySelector(".bqc-report");
        if (existing) { existing.scrollIntoView({ block: "center", behavior: "smooth" }); return; }
        var form = viewReportForm();
        v.appendChild(form);
        form.scrollIntoView({ block: "start", behavior: "smooth" });
      });
      reportWrap.appendChild(rep);
    } else {
      reportWrap.appendChild(el("p", "brt-body bqc-note", esc(S.report_unavailable)));
    }
    cta.appendChild(reportWrap);

    var restart = el("button", "bqc-restart", esc(S.restart));
    restart.type = "button";
    restart.addEventListener("click", function () {
      state.segment = null;
      state.result = null;
      setView(viewIntro());
    });
    cta.appendChild(restart);
    v.appendChild(cta);

    return v;
  }

  function viewReportForm() {
    var wrap = el("div", "bqc-card bqc-report");
    wrap.appendChild(el("h3", "brt-h3", esc(S.report_headline)));
    wrap.appendChild(el("p", "brt-body", esc(S.report_text)));

    var form = el("form", "brt-form bqc-report__form");
    form.setAttribute("novalidate", "");
    form.innerHTML =
      "<label>" + esc(S.report_salutation) + ' *<select name="anrede" required>' +
      '<option value="">' + esc(S.report_salutation_choose) + "</option>" +
      '<option value="herr">' + esc(S.report_salutation_herr) + "</option>" +
      '<option value="frau">' + esc(S.report_salutation_frau) + "</option></select></label>" +
      "<label>" + esc(S.report_first_name) + ' *<input type="text" name="vorname" required autocomplete="given-name"></label>' +
      "<label>" + esc(S.report_last_name) + ' *<input type="text" name="nachname" required autocomplete="family-name"></label>' +
      "<label>" + esc(S.report_email) + ' *<input type="email" name="email" required autocomplete="email"></label>' +
      "<label>" + esc(S.report_company) + '<input type="text" name="unternehmen" autocomplete="organization"></label>' +
      '<div class="brt-form__check-group">' +
      '<label class="brt-form__check"><input type="checkbox" name="consent_privacy" value="Ja">' +
      "<span>" + esc(S.report_privacy) + ' <a href="' + esc(CFG.privacyUrl) + '" target="_blank" rel="noopener">Datenschutzerklärung ↗</a></span></label>' +
      '<p class="brt-form__error" data-err="privacy" role="alert" hidden>' + esc(S.validation_privacy) + "</p>" +
      "</div>" +
      '<div class="brt-form__check-group">' +
      '<label class="brt-form__check"><input type="checkbox" name="newsletter_opt_in" value="Ja">' +
      "<span>" + esc(S.report_newsletter) + "</span></label>" +
      "</div>" +
      '<p class="brt-form__error" data-err="salutation" role="alert" hidden>' + esc(S.validation_salutation) + "</p>" +
      '<p class="brt-form__error" data-err="fields" role="alert" hidden>' + esc(S.validation_email) + "</p>" +
      '<button class="brt-btn" type="submit">' + esc(S.report_submit) + "</button>" +
      '<p class="bqc-report__status" role="status" aria-live="polite"></p>' +
      '<div class="bqc-sending" hidden aria-live="assertive" aria-busy="true">' +
      '<div class="bqc-spinner bqc-spinner--lg" aria-hidden="true"></div>' +
      "<h4 class=\"brt-h3\">" + esc(S.report_sending_headline) + "</h4>" +
      "<p class=\"brt-body\">" + esc(S.report_sending_text) + "</p>" +
      '<p class="bqc-sending-hint">' + esc(S.report_sending_hint) + "</p></div>";

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var privacyBox = form.querySelector('input[name="consent_privacy"]');
      var privacyErr = form.querySelector('[data-err="privacy"]');
      var salutationErr = form.querySelector('[data-err="salutation"]');
      var fieldsErr = form.querySelector('[data-err="fields"]');
      var status = form.querySelector(".bqc-report__status");
      var sending = form.querySelector(".bqc-sending");
      var anrede = form.anrede.value;
      var vorname = form.vorname.value.trim();
      var nachname = form.nachname.value.trim();
      var email = form.email.value.trim();

      var salutationOk = anrede === "herr" || anrede === "frau";
      var fieldsOk = salutationOk && vorname && nachname && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
      salutationErr.hidden = salutationOk;
      fieldsErr.hidden = !!fieldsOk;
      privacyErr.hidden = privacyBox.checked;
      if (!fieldsOk || !privacyBox.checked) return;

      var btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.hidden = true;
      form.classList.add("is-sending");
      form.querySelectorAll("input, select").forEach(function (n) { n.disabled = true; });
      status.textContent = "";
      sending.hidden = false;
      requestAnimationFrame(function () { scrollToEl(sending); });

      var started = Date.now();
      var minWait = 2800;

      postJson(CFG.reportUrl, {
        action: "report",
        submission_id: state.submissionId,
        locale: CFG.locale,
        anrede: anrede,
        vorname: vorname,
        nachname: nachname,
        email: email,
        unternehmen: form.unternehmen.value.trim(),
        zielgruppe: state.segment.id,
        gesamtscore: state.result.totalPoints,
        max_score: state.result.maxPoints,
        prozent: state.result.percent,
        status: state.result.band.key,
        consent_privacy: true,
        newsletter_opt_in: !!form.newsletter_opt_in.checked
      }).then(function (data) {
        var delay = Math.max(0, minWait - (Date.now() - started));
        window.setTimeout(function () {
          sending.hidden = true;
          form.classList.remove("is-sending");
          if (data && data.email_sent === false) {
            form.querySelectorAll("input, select").forEach(function (n) { n.disabled = false; });
            btn.hidden = false;
            btn.disabled = false;
            status.textContent = S.report_email_failed;
            status.className = "bqc-report__status bqc-report__status--err";
            if (window.console && console.error) {
              console.error("blindspot report mail failed:", data.email_error || "email_sent:false");
            }
            return;
          }
          status.textContent = S.report_success;
          status.className = "bqc-report__status bqc-report__status--ok";
          track("blindspot_report_submit", {
            segment_id: (state.segment && state.segment.id) || "",
            score_band: state.result && state.result.band ? state.result.band.key : "",
            page_path: location.pathname,
          });
        }, delay);
      }).catch(function (err) {
        sending.hidden = true;
        form.classList.remove("is-sending");
        form.querySelectorAll("input, select").forEach(function (n) { n.disabled = false; });
        btn.hidden = false;
        btn.disabled = false;
        status.textContent = reportErrorMessage(err && err.code);
        status.className = "bqc-report__status bqc-report__status--err";
        if (window.console && console.error) {
          console.error("blindspot report failed:", err && err.code, err);
        }
      });
    });

    wrap.appendChild(form);
    return wrap;
  }

  /* ------------------------------------------------------------------ */

  setView(viewIntro());
})();
