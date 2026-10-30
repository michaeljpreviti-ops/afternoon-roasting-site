(function () {
  "use strict";
  var root = document.documentElement;

  /* ---- open / closed, in the cafe's own time zone -------------------- */
  function localHour() {
    try {
      var parts = new Intl.DateTimeFormat("en-US", {
        timeZone: "America/New_York", hour: "numeric", minute: "numeric",
        hour12: false
      }).formatToParts(new Date());
      var get = function (t) {
        for (var i = 0; i < parts.length; i++) {
          if (parts[i].type === t) { return parseInt(parts[i].value, 10); }
        }
        return 0;
      };
      return get("hour") + get("minute") / 60;
    } catch (e) { return null; }
  }
  var pill = document.getElementById("status");
  if (pill) {
    var h = localHour();
    if (h !== null) {
      /* One window a day, and it does not cross midnight: open when the hour
         is inside it. A window that wrapped would need h >= open || h < close. */
      var open = h >= OPEN_HOUR && h < CLOSE_HOUR;
      pill.setAttribute("data-open", open ? "yes" : "no");
      pill.querySelector(".status__text").textContent =
        open ? OPEN_LABEL : CLOSED_LABEL;
    }
  }

  /* ---- review carousel ------------------------------------------------ */
  document.querySelectorAll("[data-carousel]").forEach(function (root) {
    var vp = root.querySelector("[data-vp]"),
        track = root.querySelector("[data-track]"),
        prev = root.querySelector("[data-prev]"),
        next = root.querySelector("[data-next]"),
        dotbox = root.querySelector("[data-dots]"),
        play = root.querySelector("[data-play]"),
        playLabel = root.querySelector("[data-playlabel]"),
        live = root.querySelector("[data-carou-live]"),
        reduce = window.matchMedia
          && window.matchMedia("(prefers-reduced-motion: reduce)").matches,
        timer = null, paused = false, held = false;

    function slides() { return Array.prototype.slice.call(track.children); }
    function perView() {
      var sl = slides();
      if (!sl.length) { return 1; }
      return Math.max(1, Math.round(vp.clientWidth / sl[0].getBoundingClientRect().width));
    }
    function index() {
      var sl = slides();
      if (!sl.length) { return 0; }
      var w = sl[0].getBoundingClientRect().width + 16;
      return Math.max(0, Math.min(sl.length - 1, Math.round(vp.scrollLeft / w)));
    }
    function go(i, smooth) {
      var sl = slides();
      if (!sl.length) { return; }
      i = Math.max(0, Math.min(sl.length - 1, i));
      var left = sl[i].offsetLeft - track.offsetLeft;
      if (smooth && !reduce && vp.scrollTo) { vp.scrollTo({left: left, behavior: "smooth"}); }
      else { vp.scrollLeft = left; }
    }
    function sync() {
      var i = index(), sl = slides(), last = Math.max(0, sl.length - perView());
      Array.prototype.forEach.call(dotbox.children, function (d, n) {
        if (n === i) { d.setAttribute("aria-current", "true"); }
        else { d.removeAttribute("aria-current"); }
      });
      prev.disabled = i <= 0;
      next.disabled = i >= last;
      if (live) { live.textContent = "Review " + (i + 1) + " of " + sl.length; }
    }

    prev.addEventListener("click", function () { go(index() - 1, true); });
    next.addEventListener("click", function () { go(index() + 1, true); });
    dotbox.addEventListener("click", function (e) {
      var d = e.target.closest ? e.target.closest("[data-dot]") : null;
      if (d) { go(parseInt(d.getAttribute("data-dot"), 10), true); }
    });
    vp.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); go(index() + 1, true); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(index() - 1, true); }
    });
    var raf = null;
    vp.addEventListener("scroll", function () {
      if (raf) { return; }
      raf = requestAnimationFrame(function () { raf = null; sync(); });
    }, {passive: true});
    window.addEventListener("resize", sync);

    /* Auto-advance, with a Pause control so it meets WCAG 2.2.2, and held
       while the pointer or keyboard focus is inside the carousel. */
    function stop() { if (timer) { clearInterval(timer); timer = null; } }
    function start() {
      stop();
      if (reduce || paused || held || document.hidden || slides().length < 2) { return; }
      timer = setInterval(function () {
        var sl = slides(), last = Math.max(0, sl.length - perView());
        go(index() >= last ? 0 : index() + 1, true);
      }, 6000);
    }
    ["mouseenter", "focusin", "touchstart"].forEach(function (ev) {
      root.addEventListener(ev, function () { held = true; stop(); }, {passive: true});
    });
    ["mouseleave", "focusout"].forEach(function (ev) {
      root.addEventListener(ev, function () { held = false; start(); });
    });
    document.addEventListener("visibilitychange", start);
    if (play) {
      if (reduce) { play.hidden = true; }
      play.addEventListener("click", function () {
        paused = !paused;
        play.setAttribute("aria-pressed", paused ? "true" : "false");
        playLabel.textContent = paused ? "Play" : "Pause";
        if (paused) { stop(); } else { start(); }
      });
    }
    sync();
    start();
  });

  /* ---- accessibility toolbar ------------------------------------------ */
  (function () {
    var H = document.documentElement, KEY = "brewandroot_a11y_v1";
    var fab = document.getElementById("a11yFab"),
        panel = document.getElementById("a11yPanel");
    if (!fab || !panel) { return; }
    var shell = fab.parentNode;

    /* Index 1 is the untouched page in both scales, so "Default" is always one
       press away and nobody can strand themselves at an unreadable size. */
    var FS = [{s: "0.88", n: "Smaller"}, {s: "1", n: "Default"}, {s: "1.15", n: "Large"},
              {s: "1.3", n: "Larger"}, {s: "1.5", n: "X-Large"}, {s: "1.75", n: "XX-Large"}];
    var LH = [{v: "1.25", n: "Tight"}, {v: "", n: "Default"}, {v: "1.9", n: "Relaxed"},
              {v: "2.3", n: "Loose"}, {v: "2.8", n: "Very Loose"}];
    var LS = [{n: "Default"}, {v: ".06em", w: ".16em", n: "Wide"},
              {v: ".12em", w: ".26em", n: "Wider"}, {v: ".2em", w: ".4em", n: "Widest"}];
    var AL = [{n: "Default"}, {v: "left", n: "Left"}, {v: "center", n: "Center"},
              {v: "right", n: "Right"}];
    var DEF = {fs: 1, lh: 1, ls: 0, align: 0, weight: 0, readable: 0, cursor: 0,
               color: "", line: 0, mask: 0, noimg: 0, spot: 0, motion: 0, links: 0};
    var S = {};

    function load() {
      var k;
      for (k in DEF) { S[k] = DEF[k]; }
      try {
        var raw = window.localStorage.getItem(KEY);
        if (!raw) { return; }
        var o = JSON.parse(raw);
        for (k in DEF) { if (o && o[k] !== undefined) { S[k] = o[k]; } }
      } catch (e) { /* private window or blocked storage: keep the defaults */ }
    }
    function save() {
      try { window.localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* ignore */ }
    }
    function flag(attr, on) {
      if (on) { H.setAttribute(attr, ""); } else { H.removeAttribute(attr); }
    }

    /* Reading aids are drawn inside this landmark, never loose on <body>. */
    function overlay(cls) {
      var d = document.createElement("div");
      d.className = cls + " a11y-ui";
      d.setAttribute("aria-hidden", "true");
      shell.appendChild(d);
      return d;
    }
    var rule = overlay("a11y-rule"), mTop = overlay("a11y-mask"), mBot = overlay("a11y-mask");
    var spotted = null;

    function clearSpot() {
      if (spotted) { spotted.classList.remove("a11y-spot"); spotted = null; }
    }
    document.addEventListener("mousemove", function (e) {
      var y = e.clientY;
      if (S.line) { rule.style.top = (y - 2) + "px"; }
      if (S.mask) {
        mTop.style.top = "0px";
        mTop.style.height = Math.max(0, y - 62) + "px";
        mBot.style.top = (y + 62) + "px";
        mBot.style.bottom = "0px";
      }
      if (S.spot) {
        var el = document.elementFromPoint(e.clientX, y);
        el = el && el.closest
          ? el.closest("p,h1,h2,h3,h4,h5,h6,li,figcaption,blockquote") : null;
        if (el && el.closest(".a11y-ui")) { el = null; }
        if (el !== spotted) { clearSpot(); spotted = el; if (el) { el.classList.add("a11y-spot"); } }
      }
    }, {passive: true});

    function apply() {
      H.style.setProperty("--a11y-fs", FS[S.fs].s);

      var lh = LH[S.lh];
      flag("data-a11y-lh", !!lh.v);
      if (lh.v) { H.style.setProperty("--a11y-lh", lh.v); }

      var ls = LS[S.ls];
      flag("data-a11y-ls", !!ls.v);
      if (ls.v) {
        H.style.setProperty("--a11y-ls", ls.v);
        H.style.setProperty("--a11y-ws", ls.w);
      }

      var al = AL[S.align];
      flag("data-a11y-align", !!al.v);
      if (al.v) { H.style.setProperty("--a11y-align", al.v); }

      flag("data-a11y-weight", S.weight);
      flag("data-a11y-readable", S.readable);
      flag("data-a11y-cursor", S.cursor);
      flag("data-a11y-noimg", S.noimg);
      flag("data-a11y-links", S.links);
      flag("data-a11y-stopmotion", S.motion);

      if (S.color) { H.setAttribute("data-a11y-color", S.color); }
      else { H.removeAttribute("data-a11y-color"); }

      rule.style.display = S.line ? "block" : "none";
      mTop.style.display = S.mask ? "block" : "none";
      mBot.style.display = S.mask ? "block" : "none";
      if (!S.spot) { clearSpot(); }
      sync();
    }

    function tile(key) { return panel.querySelector('[data-a11y-t="' + key + '"]'); }
    function press(key, on) {
      var b = tile(key);
      if (b) { b.setAttribute("aria-pressed", on ? "true" : "false"); }
    }
    function setLab(key, base, extra) {
      var b = tile(key);
      if (b) { b.querySelector(".a11y__lab").textContent = extra ? base + ": " + extra : base; }
    }

    function sync() {
      document.getElementById("a11y-fs-v").value = FS[S.fs].n;
      document.getElementById("a11y-lh-v").value = LH[S.lh].n;
      press("readable", S.readable); press("cursor", S.cursor);
      press("weight", S.weight);     press("noimg", S.noimg);
      press("line", S.line);         press("mask", S.mask);
      press("spot", S.spot);         press("motion", S.motion);
      press("links", S.links);
      press("c-light", S.color === "light");
      press("c-high", S.color === "high");
      press("c-mono", S.color === "mono");
      press("ls", S.ls > 0);
      setLab("ls", "Letter Spacing", S.ls > 0 ? LS[S.ls].n : "");
      press("align", S.align > 0);
      setLab("align", "Align Text", S.align > 0 ? AL[S.align].n : "");
    }

    panel.addEventListener("click", function (e) {
      var b = e.target.closest ? e.target.closest("button") : null;
      if (!b || !panel.contains(b)) { return; }

      if (b.hasAttribute("data-a11y-close")) { closePanel(); return; }

      if (b.hasAttribute("data-a11y-reset")) {
        var k;
        for (k in DEF) { S[k] = DEF[k]; }
        clearSpot(); apply(); save();
        return;
      }

      var st = b.getAttribute("data-a11y-s");
      if (st) {
        var dir = parseInt(b.getAttribute("data-dir"), 10);
        var max = (st === "fs" ? FS : LH).length - 1;
        S[st] = Math.min(max, Math.max(0, S[st] + dir));
        apply(); save();
        return;
      }

      var t = b.getAttribute("data-a11y-t");
      if (!t) { return; }
      if (t === "ls") { S.ls = (S.ls + 1) % LS.length; }
      else if (t === "align") { S.align = (S.align + 1) % AL.length; }
      else if (t.indexOf("c-") === 0) {
        var mode = t.slice(2);
        S.color = (S.color === mode) ? "" : mode;   /* the colour modes are exclusive */
      } else { S[t] = S[t] ? 0 : 1; }
      apply(); save();
    });

    function openPanel() {
      panel.hidden = false;
      fab.setAttribute("aria-expanded", "true");
      fab.style.display = "none";          /* the panel sits over the launcher */
      /* preventScroll matters: without it the browser scrolls .a11y__body to
         "reveal" a header button and the panel opens halfway down the list. */
      panel.querySelector(".a11y__x").focus({preventScroll: true});
      panel.querySelector(".a11y__body").scrollTop = 0;
    }
    function closePanel() {
      panel.hidden = true;
      fab.setAttribute("aria-expanded", "false");
      fab.style.display = "";
      fab.focus();
    }
    fab.addEventListener("click", openPanel);
    document.addEventListener("keydown", function (e) {
      if ((e.key === "Escape" || e.key === "Esc") && !panel.hidden) { closePanel(); }
    });

    load();
    apply();
  }());
}());
