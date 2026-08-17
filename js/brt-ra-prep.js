/* RA-Vorbereitung Fragebogen — /tools/ra-vorbereitung/ */
(function () {
  "use strict";

  var root = document.getElementById("brt-ra-prep");
  var configEl = document.getElementById("brt-ra-prep-config");
  if (!root || !configEl) return;

  var CFG;
  try {
    CFG = JSON.parse(configEl.textContent);
  } catch (e) {
    return;
  }

  var S = CFG.strings;
  var WEITERE_VALUE = "weitere";

  var state = {
    stepIdx: 0,
    answers: {},
    submissionId: "",
    submitting: false,
    done: false
  };

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
    return "rap-" + Date.now() + "-" + Math.random().toString(16).slice(2);
  }

  function scrollToRoot() {
    var y = root.getBoundingClientRect().top + window.pageYOffset - 96;
    try {
      window.scrollTo({ top: y < 0 ? 0 : y, behavior: "auto" });
    } catch (err) {
      window.scrollTo(0, y < 0 ? 0 : y);
    }
  }

  function focusHeading(view) {
    var h = view.querySelector("h2, h3");
    if (!h) return;
    h.setAttribute("tabindex", "-1");
    try { h.focus({ preventScroll: true }); } catch (err) { /* no-op */ }
  }

  var isFirstView = true;

  function setView(node) {
    root.innerHTML = "";
    root.appendChild(node);
    if (node.classList.contains("brt-fade-up")) node.classList.add("is-visible");
    if (!isFirstView) scrollToRoot();
    isFirstView = false;
    focusHeading(node);
  }

  function currentStep() {
    return CFG.steps[state.stepIdx];
  }

  function getVal(fieldId) {
    return state.answers[fieldId];
  }

  function setVal(fieldId, value) {
    state.answers[fieldId] = value;
  }

  function ensureWeitereChecked(groupId, autoValue) {
    autoValue = autoValue || WEITERE_VALUE;
    var vals = Array.isArray(getVal(groupId)) ? getVal(groupId).slice() : [];
    if (vals.indexOf(autoValue) < 0) {
      vals.push(autoValue);
      setVal(groupId, vals);
    }
  }

  function postJson(url, payload) {
    return fetch(url, {
      method: "POST",
      redirect: "follow",
      headers: { "Content-Type": "text/plain;charset=utf-8" },
      body: JSON.stringify(payload)
    }).then(function (res) {
      return res.text().then(function (text) {
        var data = {};
        try {
          data = text ? JSON.parse(text) : {};
        } catch (err) {
          data = {};
        }
        if (!res.ok) {
          var httpErr = new Error((data && data.error) || ("HTTP " + res.status));
          httpErr.code = (data && data.error) || "http_error";
          throw httpErr;
        }
        if (!data || data.ok !== true) {
          var bad = new Error((data && data.error) || "invalid_response");
          bad.code = (data && data.error) || "invalid_response";
          throw bad;
        }
        return data;
      });
    });
  }

  function submitErrorMessage(code) {
    if (code === "mail_failed") return S.error_mail || S.error_submit;
    if (code === "not_configured" || code === "sheet_failed") return S.error_unavailable;
    if (code === "missing_fields") return S.error_validation || S.error_submit;
    return S.error_submit;
  }

  function isEmail(v) {
    return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(String(v || "").trim());
  }

  function checkboxGroupValid(groupId, detailFieldId) {
    var vals = getVal(groupId);
    var hasSelection = Array.isArray(vals) && vals.length > 0;
    if (hasSelection) return true;
    if (detailFieldId && String(getVal(detailFieldId) || "").trim()) return true;
    return false;
  }

  function validateStep(step) {
    var errors = {};
    (step.fields || []).forEach(function (field) {
      var id = field.id;
      var type = field.type;
      if (field.linked_group) return;

      if (type === "consent_privacy") {
        if (!getVal(id)) errors[id] = S.validation_privacy;
        return;
      }
      if (type === "consent_terms") {
        if (!getVal(id)) errors[id] = S.validation_terms;
        return;
      }
      if (type === "newsletter") return;
      if (!field.required) return;
      var val = getVal(id);
      if (type === "select") {
        if (val !== "herr" && val !== "frau") errors[id] = S.validation_salutation;
        return;
      }
      if (type === "email") {
        if (!isEmail(val)) errors[id] = S.validation_email;
        return;
      }
      if (type === "tel") {
        if (!String(val || "").trim()) errors[id] = S.validation_phone;
        return;
      }
      if (type === "checkbox_group") {
        if (!checkboxGroupValid(id, field.detail_field)) {
          errors[id] = S.validation_checkbox || S.validation_required;
        }
        return;
      }
      if (!String(val || "").trim()) errors[id] = S.validation_required;
    });
    return errors;
  }

  function renderField(field, form) {
    var wrap = el("div", "rap-field");
    var id = field.id;
    var type = field.type;

    if (type === "consent_privacy") {
      wrap.innerHTML =
        '<div class="brt-form__check-group">' +
        '<label class="brt-form__check"><input type="checkbox" name="' + esc(id) + '">' +
        "<span>" + esc(S.consent_privacy) +
        ' <a href="' + esc(CFG.privacyUrl) + '" target="_blank" rel="noopener">' +
        esc(S.privacy_link) + " ↗</a> *</span></label>" +
        '<p class="brt-form__error" data-err="' + esc(id) + '" role="alert" hidden></p></div>';
      form.appendChild(wrap);
      var cb = wrap.querySelector('input[name="' + id + '"]');
      cb.checked = !!getVal(id);
      cb.addEventListener("change", function () { setVal(id, cb.checked); });
      return;
    }

    if (type === "consent_terms") {
      wrap.innerHTML =
        '<div class="brt-form__check-group">' +
        '<label class="brt-form__check"><input type="checkbox" name="' + esc(id) + '">' +
        "<span>" + esc(S.consent_terms) +
        ' <a href="' + esc(CFG.termsUrl) + '" target="_blank" rel="noopener">' +
        esc(S.terms_link) + " ↗</a> *</span></label>" +
        '<p class="brt-form__error" data-err="' + esc(id) + '" role="alert" hidden></p></div>';
      form.appendChild(wrap);
      var cb2 = wrap.querySelector('input[name="' + id + '"]');
      cb2.checked = !!getVal(id);
      cb2.addEventListener("change", function () { setVal(id, cb2.checked); });
      return;
    }

    if (type === "newsletter") {
      wrap.innerHTML =
        '<div class="brt-form__check-group">' +
        '<label class="brt-form__check"><input type="checkbox" name="' + esc(id) + '">' +
        "<span>" + esc(S.consent_newsletter) + "</span></label></div>";
      form.appendChild(wrap);
      var cb3 = wrap.querySelector('input[name="' + id + '"]');
      cb3.checked = !!getVal(id);
      cb3.addEventListener("change", function () { setVal(id, cb3.checked); });
      return;
    }

    if (type === "checkbox_group") {
      var detailId = field.detail_field;
      var autoValue = field.detail_auto_value || WEITERE_VALUE;
      if (detailId && String(getVal(detailId) || "").trim()) {
        ensureWeitereChecked(id, autoValue);
      }

      var legend = el("fieldset", "rap-checkgroup");
      var labelText = esc(field.label) + (field.required ? " *" : "");
      legend.innerHTML = "<legend class=\"rap-field__label\">" + labelText + "</legend>";
      if (field.hint) {
        legend.appendChild(el("p", "rap-field__hint", esc(field.hint)));
      }
      var group = el("div", "rap-checkgroup__items");
      var selected = Array.isArray(getVal(id)) ? getVal(id) : [];
      (field.options || []).forEach(function (opt) {
        var lid = id + "-" + opt.value;
        var item = el("label", "brt-form__check");
        item.innerHTML =
          '<input type="checkbox" id="' + esc(lid) + '" value="' + esc(opt.value) + '"' +
          (selected.indexOf(opt.value) >= 0 ? " checked" : "") + ">" +
          "<span>" + esc(opt.label) + "</span>";
        group.appendChild(item);
      });
      legend.appendChild(group);
      legend.innerHTML += '<p class="brt-form__error" data-err="' + esc(id) + '" role="alert" hidden></p>';
      wrap.appendChild(legend);
      form.appendChild(wrap);
      group.querySelectorAll("input[type=checkbox]").forEach(function (cb) {
        cb.addEventListener("change", function () {
          if (id === "social_media") {
            if (cb.value === "keine" && cb.checked) {
              group.querySelectorAll("input:checked").forEach(function (other) {
                if (other !== cb) other.checked = false;
              });
            } else if (cb.checked && cb.value !== "keine") {
              var noneCb = group.querySelector('input[value="keine"]');
              if (noneCb) noneCb.checked = false;
            }
          }
          var vals = [];
          group.querySelectorAll("input:checked").forEach(function (c) { vals.push(c.value); });
          setVal(id, vals);
        });
      });
      return;
    }

    if (field.linked_group) {
      var linkedGroup = field.linked_group;
      var linkedAuto = field.linked_auto_value || WEITERE_VALUE;
      var linkedLabel = esc(field.label);
      var linkedInputTag = type === "textarea"
        ? '<textarea name="' + esc(id) + '" rows="' + (field.rows || 3) + '"></textarea>'
        : '<input type="text" name="' + esc(id) + '">';
      wrap.innerHTML = "<label>" + linkedLabel + linkedInputTag + "</label>";
      if (field.hint) {
        wrap.appendChild(el("p", "rap-field__hint", esc(field.hint)));
      }
      form.appendChild(wrap);
      var linkedInput = wrap.querySelector("[name=\"" + id + "\"]");
      if (getVal(id) != null) linkedInput.value = getVal(id);
      linkedInput.addEventListener("input", function () {
        setVal(id, linkedInput.value);
        if (String(linkedInput.value || "").trim()) {
          ensureWeitereChecked(linkedGroup, linkedAuto);
          var weitereCb = form.querySelector('input[id="' + linkedGroup + "-" + linkedAuto + '"]');
          if (weitereCb) weitereCb.checked = true;
        }
      });
      return;
    }

    var labelHtml = esc(field.label) + (field.required ? " *" : "");
    if (type === "textarea") {
      wrap.innerHTML =
        "<label>" + labelHtml +
        '<textarea name="' + esc(id) + '" rows="' + (field.rows || 4) + '"></textarea></label>';
      if (field.hint) {
        wrap.insertBefore(el("p", "rap-field__hint", esc(field.hint)), wrap.firstChild.nextSibling);
      }
    } else if (type === "select") {
      var opts = '<option value="">' + (CFG.locale === "en" ? "Please choose" : "Bitte wählen") + "</option>";
      (field.options || []).forEach(function (opt) {
        opts += '<option value="' + esc(opt.value) + '">' + esc(opt.label) + "</option>";
      });
      wrap.innerHTML = "<label>" + labelHtml + '<select name="' + esc(id) + '" required>' + opts + "</select></label>";
    } else {
      wrap.innerHTML =
        "<label>" + labelHtml +
        '<input type="' + esc(type === "url" ? "url" : type) + '" name="' + esc(id) + '"' +
        (field.autocomplete ? ' autocomplete="' + esc(field.autocomplete) + '"' : "") +
        "></label>";
      if (field.hint) {
        wrap.insertBefore(el("p", "rap-field__hint", esc(field.hint)), wrap.firstChild.nextSibling);
      }
    }
    wrap.innerHTML += '<p class="brt-form__error" data-err="' + esc(id) + '" role="alert" hidden></p>';
    form.appendChild(wrap);

    var input = wrap.querySelector("[name=\"" + id + "\"]");
    if (getVal(id) != null) input.value = getVal(id);
    input.addEventListener("input", function () {
      setVal(id, input.value);
    });
    if (type === "select") {
      input.addEventListener("change", function () { setVal(id, input.value); });
    }
  }

  function showErrors(form, errors) {
    form.querySelectorAll("[data-err]").forEach(function (node) {
      var key = node.getAttribute("data-err");
      if (errors[key]) {
        node.textContent = errors[key];
        node.hidden = false;
      } else {
        node.textContent = "";
        node.hidden = true;
      }
    });
  }

  function collectAnswersPayload() {
    var antworten = {};
    CFG.steps.forEach(function (step) {
      (step.fields || []).forEach(function (field) {
        var t = field.type;
        if (t === "consent_privacy" || t === "consent_terms" || t === "newsletter") return;
        if (["anrede", "vorname", "nachname", "email", "telefon", "unternehmen"].indexOf(field.id) >= 0) {
          return;
        }
        antworten[field.id] = getVal(field.id);
      });
    });
    return antworten;
  }

  function submitForm() {
    if (state.submitting || state.done) return;
    if (!CFG.submitUrl) {
      setView(viewError(S.error_unavailable));
      return;
    }
    state.submitting = true;
    var payload = {
      action: "submit",
      submission_id: state.submissionId,
      locale: CFG.locale,
      anrede: getVal("anrede"),
      vorname: String(getVal("vorname") || "").trim(),
      nachname: String(getVal("nachname") || "").trim(),
      email: String(getVal("email") || "").trim(),
      telefon: String(getVal("telefon") || "").trim(),
      unternehmen: String(getVal("unternehmen") || "").trim(),
      antworten: collectAnswersPayload(),
      consent_privacy: getVal("consent_privacy") === true,
      consent_terms: getVal("consent_terms") === true,
      newsletter_opt_in: getVal("newsletter_opt_in") === true,
      page_url: window.location.href,
      referrer: document.referrer || "",
      browser_language: navigator.language || "",
      timezone: (function () {
        try { return Intl.DateTimeFormat().resolvedOptions().timeZone; } catch (e) { return ""; }
      })()
    };

    postJson(CFG.submitUrl, payload).then(function () {
      state.done = true;
      state.submitting = false;
      setView(viewSuccess());
    }).catch(function (err) {
      state.submitting = false;
      setView(viewStep(currentStep(), submitErrorMessage(err && err.code)));
    });
  }

  function viewIntro() {
    var v = el("div", "rap-card rap-card--center brt-fade-up");
    v.appendChild(el("h2", "brt-h2", esc(S.intro_title)));
    v.appendChild(el("p", "brt-body", esc(S.intro_text)));
    var btn = el("button", "brt-btn brt-btn--lg", esc(S.start));
    btn.type = "button";
    btn.addEventListener("click", function () {
      state.submissionId = uuid();
      state.stepIdx = 0;
      setView(viewStep(currentStep()));
    });
    var actions = el("div", "rap-actions rap-actions--center");
    actions.appendChild(btn);
    v.appendChild(actions);
    return v;
  }

  function viewProgress() {
    var total = CFG.steps.length;
    var current = state.stepIdx + 1;
    var pct = total ? (current / total) * 100 : 0;
    var wrap = el("div", "rap-progress");
    wrap.innerHTML =
      '<p class="rap-progress__label">' +
      esc(S.progress.replace("{current}", String(current)).replace("{total}", String(total))) +
      "</p>" +
      '<div class="rap-progress__track"><div class="rap-progress__bar" style="transform:scaleX(' +
      (pct / 100) + ')"></div></div>';
    return wrap;
  }

  function viewStep(step, errorMsg) {
    var v = el("div", "rap-card brt-fade-up");
    v.appendChild(viewProgress());
    v.appendChild(el("h2", "brt-h3", esc(step.title)));
    if (step.intro) v.appendChild(el("p", "brt-body rap-step__intro", esc(step.intro)));

    var form = el("form", "brt-form rap-form");
    form.setAttribute("novalidate", "");
    (step.fields || []).forEach(function (field) { renderField(field, form); });

    if (errorMsg) {
      var err = el("p", "brt-form__error", esc(errorMsg));
      err.setAttribute("role", "alert");
      form.appendChild(err);
    }

    var actions = el("div", "rap-actions rap-actions--between");
    if (state.stepIdx > 0) {
      var back = el("button", "brt-btn brt-btn--outline", esc(S.back));
      back.type = "button";
      back.addEventListener("click", function () {
        state.stepIdx -= 1;
        setView(viewStep(currentStep()));
      });
      actions.appendChild(back);
    } else {
      actions.appendChild(el("span"));
    }

    var isLast = state.stepIdx >= CFG.steps.length - 1;
    var nextLabel = isLast ? S.submit : S.next;
    var next = el("button", "brt-btn", esc(nextLabel));
    next.type = "button";
    next.addEventListener("click", function () {
      var errors = validateStep(step);
      showErrors(form, errors);
      if (Object.keys(errors).length) return;
      if (isLast) {
        var sending = el("div", "rap-sending");
        sending.innerHTML =
          '<div class="rap-spinner rap-spinner--lg" aria-hidden="true"></div>' +
          "<h3 class=\"brt-h3\">" + esc(S.sending_headline) + "</h3>" +
          "<p class=\"brt-body\">" + esc(S.sending_text) + "</p>";
        form.innerHTML = "";
        form.appendChild(sending);
        submitForm();
        return;
      }
      state.stepIdx += 1;
      setView(viewStep(currentStep()));
    });
    actions.appendChild(next);
    v.appendChild(form);
    v.appendChild(actions);
    return v;
  }

  function viewSuccess() {
    var v = el("div", "rap-card rap-card--center brt-fade-up");
    v.appendChild(el("h2", "brt-h2", esc(S.success_title)));
    v.appendChild(el("p", "brt-body", esc(S.success_text)));
    return v;
  }

  function viewError(msg) {
    var v = el("div", "rap-card brt-fade-up");
    v.appendChild(el("p", "brt-form__error", esc(msg)));
    return v;
  }

  setView(viewIntro());
})();
