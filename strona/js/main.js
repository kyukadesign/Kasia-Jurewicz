/* Kancelaria KJK – skrypty strony (bez zależności). Treść i nawigacja działają także bez JavaScriptu. */
(function () {
  'use strict';
  var root = document.documentElement;
  var cfg = window.KJK_CONFIG || {};
  var desktop = window.matchMedia('(min-width: 1024px)');
  function isDesktop() { return desktop.matches && !root.classList.contains('nav-collapsed'); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function safeUrl(u) { return typeof u === 'string' && /^https:\/\/[^\s"'<>]+$/.test(u) ? u : ''; }
  var params = new URLSearchParams(location.search);

  /* ---------- Nagłówek: linia pod spodem po przewinięciu ---------- */
  var header = document.querySelector('[data-header]');
  function onScroll() { if (header) header.classList.toggle('is-scrolled', window.scrollY > 8); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Menu specjalizacji (wzorzec disclosure: otwiera się kliknięciem, nie najechaniem) ---------- */
  var megaBtn = document.querySelector('.mega-toggle');
  var mega = document.getElementById('mega');
  var megaLinks = mega ? $$('a', mega) : [];
  function setMega(open, focusFirst) {
    if (!megaBtn || !mega) return;
    megaBtn.setAttribute('aria-expanded', String(open));
    mega.hidden = !open;
    if (open && focusFirst && megaLinks[0]) megaLinks[0].focus();
  }
  if (megaBtn && mega) {
    megaBtn.addEventListener('click', function () { setMega(megaBtn.getAttribute('aria-expanded') !== 'true'); });
    megaBtn.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); setMega(true, true); }
    });
    mega.addEventListener('keydown', function (e) {
      var i = megaLinks.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') { e.preventDefault(); megaLinks[Math.min(i + 1, megaLinks.length - 1)].focus(); }
      if (e.key === 'ArrowUp') { e.preventDefault(); if (i <= 0) megaBtn.focus(); else megaLinks[i - 1].focus(); }
      if (e.key === 'Home') { e.preventDefault(); megaLinks[0].focus(); }
      if (e.key === 'End') { e.preventDefault(); megaLinks[megaLinks.length - 1].focus(); }
    });
    document.addEventListener('click', function (e) {
      if (isDesktop() && !e.target.closest('.has-mega')) setMega(false);
    });
    megaBtn.parentNode.addEventListener('focusout', function (e) {
      if (isDesktop() && e.relatedTarget && !megaBtn.parentNode.contains(e.relatedTarget)) setMega(false);
    });
  }

  /* ---------- Menu: gdy pozycje nie mieszczą się obok znaku, przechodzi w przycisk „Menu” ---------- */
  var bar = document.querySelector('.bar');
  var brandEl = document.querySelector('.brand');
  var navList = document.querySelector('.nav-list');
  function fitNav() {
    if (!bar || !brandEl || !navList) return;
    if (root.classList.contains('menu-open')) return;
    root.classList.remove('nav-collapsed');
    if (!desktop.matches) return;
    var cs = getComputedStyle(bar);
    var room = bar.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    if (brandEl.scrollWidth + navList.scrollWidth + 40 > room) root.classList.add('nav-collapsed');
  }
  fitNav();
  window.addEventListener('resize', fitNav);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitNav);

  /* ---------- Menu na telefonie (pełny ekran) ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var toggleLabel = toggle ? toggle.querySelector('.nav-toggle-label') : null;
  var nav = document.getElementById('nav');
  function setMenu(open, quiet) {
    if (!toggle) return;
    toggle.setAttribute('aria-expanded', String(open));
    if (toggleLabel) toggleLabel.textContent = open ? 'Zamknij' : 'Menu';
    root.classList.toggle('menu-open', open);
    if (open) {
      var first = nav.querySelector('a, button');
      if (first && !quiet) first.focus();
    } else {
      setMega(false);
    }
  }
  if (toggle && nav) {
    toggle.addEventListener('click', function () { setMenu(toggle.getAttribute('aria-expanded') !== 'true'); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a') && !isDesktop()) setMenu(false, true); });
    // pętla fokusu w otwartym menu
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab' || !root.classList.contains('menu-open')) return;
      var items = [toggle].concat($$('a, button', nav).filter(function (el) { return el.offsetParent !== null; }));
      var first = items[0], last = items[items.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    var onBp = function () { fitNav(); if (isDesktop()) setMenu(false, true); setMega(false); };
    if (desktop.addEventListener) desktop.addEventListener('change', onBp);
  }
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (megaBtn && megaBtn.getAttribute('aria-expanded') === 'true') { setMega(false); megaBtn.focus(); return; }
    if (root.classList.contains('menu-open')) { setMenu(false); toggle.focus(); }
  });

  /* ---------- Powrót przyciskiem „Wstecz” (strona z pamięci podręcznej): menu zamknięte, formularz gotowy ---------- */
  window.addEventListener('pageshow', function (e) {
    if (!e.persisted) return;
    setMenu(false, true);
    setMega(false);
    var busy = document.querySelector('#contact-form button[aria-busy]');
    if (busy) { busy.removeAttribute('aria-busy'); busy.disabled = false; var bl = busy.querySelector('.btn-label'); if (bl && bl.getAttribute('data-label')) bl.textContent = bl.getAttribute('data-label'); }
  });

  /* ---------- Media społecznościowe: widoczne dopiero po wpisaniu adresu w js/config.js ---------- */
  var social = cfg.social || {};
  var anySocial = false;
  $$('[data-social]').forEach(function (li) {
    var url = safeUrl(social[li.getAttribute('data-social')]);
    if (!url) return;
    li.querySelector('a').href = url;
    li.hidden = false;
    anySocial = true;
  });
  if (anySocial) {
    $$('.social-ph').forEach(function (el) { el.remove(); });
  }

  /* ---------- Filmy: odtwarzacz ładuje się dopiero po kliknięciu ---------- */
  var videos = (cfg.videos || []).filter(function (v) { return v && /^[\w-]{6,20}$/.test(v.youtubeId || '') && v.title; });
  var vSection = document.querySelector('[data-videos]');
  var vList = document.getElementById('v-list');
  if (vSection && vList && videos.length) {
    videos.forEach(function (v) {
      var li = document.createElement('li'); li.className = 'film';
      var thumb = document.createElement('div'); thumb.className = 'film-thumb';
      if (v.thumbnail) { var img = document.createElement('img'); img.src = v.thumbnail; img.alt = ''; img.loading = 'lazy'; thumb.appendChild(img); }
      var play = document.createElement('button'); play.type = 'button'; play.className = 'film-play';
      play.setAttribute('aria-label', 'Odtwórz film: ' + v.title);
      play.innerHTML = '<span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15L20 12z"/></svg></span>';
      play.addEventListener('click', function () {
        var f = document.createElement('iframe');
        f.src = 'https://www.youtube-nocookie.com/embed/' + v.youtubeId + '?autoplay=1&rel=0' + (v.captions ? '&cc_load_policy=1&cc_lang_pref=pl' : '');
        f.title = v.title; f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen'; f.allowFullscreen = true;
        thumb.innerHTML = ''; thumb.appendChild(f); f.focus();
      });
      thumb.appendChild(play);
      var h = document.createElement('h3'); h.textContent = v.title;
      li.appendChild(thumb); li.appendChild(h);
      if (v.description) { var p = document.createElement('p'); p.className = 'muted'; p.textContent = v.description; li.appendChild(p); }
      if (v.captions) { var c = document.createElement('p'); c.className = 'muted'; c.textContent = 'Film ma napisy.'; li.appendChild(c); }
      if (v.transcript) {
        var d = document.createElement('details'); d.className = 'transcript';
        var s = document.createElement('summary'); s.textContent = 'Transkrypcja'; d.appendChild(s);
        String(v.transcript).split(/\n\s*\n/).forEach(function (t) { var tp = document.createElement('p'); tp.className = 'muted'; tp.textContent = t; d.appendChild(tp); });
        li.appendChild(d);
      }
      vList.appendChild(li);
    });
    vSection.hidden = false;
  }

  /* ---------- Pasek podglądu redakcyjnego ---------- */
  if (root.classList.contains('demo')) {
    var base = (document.querySelector('link[rel="stylesheet"]').getAttribute('href') || '').replace('css/style.css', '');
    var demoBar = document.createElement('div');
    demoBar.className = 'demo-bar';
    demoBar.setAttribute('role', 'note');
    demoBar.innerHTML = '<span><b>Podgląd redakcyjny.</b> Elementy w przerywanej ramce czekają na treść lub akceptację; te z napisem „do akceptacji” są widoczne publicznie, pozostałe – tylko tutaj.</span>' +
      '<a href="' + base + 'podglad.html">Plansze i brakujące materiały</a>' +
      (root.hasAttribute('data-always-demo') ? '<a href="' + base + 'index.html?podglad=1">Strona w trybie podglądu</a>' : '<a href="?podglad=0">Pokaż wersję publiczną</a>');
    document.body.appendChild(demoBar);
  }

  /* ---------- Formularz kontaktowy ----------
     Nigdy nie pokazujemy potwierdzenia wysłania, jeśli usługa nie przyjęła wiadomości.
     data-provider: '' (brak usługi – pola wyłączone, informacja nad nimi), 'endpoint' (POST na data-endpoint), 'netlify' (Netlify Forms). */
  var form = document.getElementById('contact-form');
  if (!form) return;
  var topic = (params.get('temat') || '').replace(/[^a-z-]/g, '');
  if (topic && form.elements.temat.querySelector('option[value="' + topic + '"]')) {
    form.elements.temat.value = topic;
    form.elements.temat.classList.add('from-link');
  }
  var provider = form.getAttribute('data-provider');
  if (!provider) return;

  var msg = document.getElementById('form-msg');
  var done = document.getElementById('form-done');
  var submit = form.querySelector('button[type="submit"]');

  // komunikat błędu stoi przy polu (element, którego id kończy się na „-err”)
  function errEl(input) {
    var ids = (input.getAttribute('aria-describedby') || '').split(' ');
    for (var i = 0; i < ids.length; i++) if (/-err$/.test(ids[i])) return document.getElementById(ids[i]);
    return null;
  }
  function setError(input, text) {
    var err = errEl(input);
    if (err) err.textContent = text || '';
    if (text) input.setAttribute('aria-invalid', 'true'); else input.removeAttribute('aria-invalid');
    return !text;
  }
  function validate() {
    var f = form.elements, ok = true, first = null;
    if (!setError(f.imie, f.imie.value.trim() ? '' : 'Wpisz imię.')) { ok = false; first = first || f.imie; }
    var c = f.kontakt.value.trim();
    var looksOk = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(c) || c.replace(/[^\d]/g, '').length >= 9;
    if (!setError(f.kontakt, !c ? 'Wpisz telefon albo e-mail.' : (looksOk ? '' : 'Sprawdź numer telefonu albo adres e-mail – coś się nie zgadza.'))) { ok = false; first = first || f.kontakt; }
    if (!setError(f.temat, f.temat.value ? '' : 'Wybierz temat sprawy. Jeśli żaden nie pasuje, wybierz „Inna sprawa”.')) { ok = false; first = first || f.temat; }
    if (first) first.focus();
    return ok;
  }
  ['imie', 'kontakt'].forEach(function (n) {
    form.elements[n].addEventListener('input', function () { if (this.getAttribute('aria-invalid')) setError(this, ''); });
  });
  form.elements.temat.addEventListener('change', function () { if (this.value) setError(this, ''); });

  function showMsg(title, text) {
    msg.innerHTML = '';
    var s = document.createElement('strong'); s.textContent = title;
    var p = document.createElement('span'); p.textContent = text;
    msg.appendChild(s); msg.appendChild(p);
    msg.hidden = false; msg.focus();
  }
  function showDone() {
    done.innerHTML = '<h2>Dziękuję – prośba o kontakt dotarła.</h2><p>Oddzwonię lub odpiszę, żeby umówić termin rozmowy.</p>';
    form.hidden = true; done.hidden = false; done.focus();
  }
  var label = submit.querySelector('.btn-label');
  var labelText = label ? label.textContent : '';
  if (label) label.setAttribute('data-label', labelText);
  function setBusy(on) {
    if (on) { submit.setAttribute('aria-busy', 'true'); submit.disabled = true; if (label) label.textContent = 'Wysyłanie…'; }
    else { submit.removeAttribute('aria-busy'); submit.disabled = false; if (label) label.textContent = labelText; }
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    msg.hidden = true;
    if (form.elements.www && form.elements.www.value) return; // pole-pułapka dla botów
    if (!validate()) return;
    var endpoint = form.getAttribute('data-endpoint');
    var ctrl = window.AbortController ? new AbortController() : null;
    var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 20000) : null;
    var opts = { method: 'POST', signal: ctrl ? ctrl.signal : undefined };
    var req;
    if (provider === 'netlify') {
      opts.headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
      opts.body = new URLSearchParams(new FormData(form)).toString();
      req = fetch('/', opts);
    } else {
      opts.headers = { Accept: 'application/json' };
      opts.body = new FormData(form);
      req = fetch(endpoint, opts);
    }
    setBusy(true);
    req.then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.headers.get('content-type') && r.headers.get('content-type').indexOf('json') !== -1 ? r.json() : {};
    }).then(function (data) {
      if (data && data.ok === false) throw new Error('odrzucone');
      showDone();
    }).catch(function () {
      showMsg('Nie udało się wysłać prośby o kontakt.', ' Usługa jej nie przyjęła albo nie ma połączenia z internetem. Wpisane dane zostały w formularzu – spróbuj ponownie za chwilę.');
    }).then(function () {
      if (timer) clearTimeout(timer);
      setBusy(false);
    });
  });
})();
