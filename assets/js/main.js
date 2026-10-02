/* HọcFree.vn – main.js */
(function () {
  "use strict";

  var doc = document.documentElement;
  var ROOT = doc.getAttribute("data-root") || "";
  var POSTS = window.HF_POSTS || [];
  var $ = function (s, el) { return (el || document).querySelector(s); };
  var $$ = function (s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); };

  /* ---------- Giao diện sáng / tối ---------- */
  var themeBtn = $(".theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var dark = doc.classList.toggle("dark");
      try { localStorage.setItem("hf-theme", dark ? "dark" : "light"); } catch (e) { /* bỏ qua */ }
    });
  }

  /* ---------- Menu mobile ---------- */
  var burger = $(".burger");
  var nav = $(".main-nav");
  if (burger && nav) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  /* ---------- Tìm kiếm ---------- */
  function normalize(s) {
    return (s || "").toLowerCase().replace(/đ/g, "d")
      .normalize("NFD").replace(/[̀-ͯ]/g, "");
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function search(q) {
    var terms = normalize(q).split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    return POSTS.map(function (p) {
      var title = normalize(p.t);
      var hay = title + " " + normalize(p.e) + " " + normalize(p.tags.join(" ")) + " " + normalize(p.cn);
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        if (hay.indexOf(terms[i]) === -1) return null;
        score += title.indexOf(terms[i]) !== -1 ? 3 : 1;
      }
      return { p: p, score: score };
    }).filter(Boolean).sort(function (a, b) { return b.score - a.score; })
      .map(function (r) { return r.p; });
  }
  function highlight(text, q) {
    var safe = escapeHtml(text);
    var terms = q.trim().split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) return safe;
    var re = new RegExp("(" + terms.map(function (t) {
      return escapeHtml(t).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    }).join("|") + ")", "gi");
    return safe.replace(re, "<mark>$1</mark>");
  }

  var panel = $(".search-panel");
  var panelInput = panel && $("input", panel);
  var suggest = panel && $(".search-suggest", panel);

  function openSearch() {
    if (!panel) return;
    panel.hidden = false;
    panelInput.focus();
  }
  function closeSearch() {
    if (!panel) return;
    panel.hidden = true;
    panelInput.value = "";
    suggest.innerHTML = "";
  }
  if (panel) {
    $(".search-toggle").addEventListener("click", function () {
      panel.hidden ? openSearch() : closeSearch();
    });
    $(".search-close", panel).addEventListener("click", closeSearch);
    panelInput.addEventListener("input", function () {
      var q = panelInput.value.trim();
      if (!q) { suggest.innerHTML = ""; return; }
      var res = search(q).slice(0, 6);
      suggest.innerHTML = res.length ? res.map(function (p) {
        return '<a href="' + ROOT + p.u + '"><img src="' + ROOT + p.img + '" alt="" loading="lazy">' +
          "<span>" + highlight(p.t, q) + "<small>" + escapeHtml(p.cn) + " · " + p.d + "</small></span></a>";
      }).join("") : '<p class="empty">Không tìm thấy bài viết phù hợp. Nhấn Enter để tìm kỹ hơn.</p>';
    });
    document.addEventListener("keydown", function (ev) {
      var tag = (ev.target.tagName || "").toLowerCase();
      if (ev.key === "Escape" && !panel.hidden) closeSearch();
      if (ev.key === "/" && tag !== "input" && tag !== "textarea") { ev.preventDefault(); openSearch(); }
    });
  }

  /* Trang search.html */
  var results = $("#search-results");
  if (results) {
    var q = new URLSearchParams(location.search).get("q") || "";
    var input = $("#search-page-input");
    var summary = $("#search-summary");
    input.value = q;
    var list = q ? search(q) : POSTS;
    summary.textContent = q
      ? (list.length ? "Tìm thấy " + list.length + " bài viết cho “" + q + "”" : "Không có kết quả cho “" + q + "”. Hãy thử từ khóa khác.")
      : "Tất cả " + POSTS.length + " bài viết";
    if (q) document.title = "Tìm: " + q + " | HọcFree";
    results.innerHTML = list.map(function (p) {
      var url = ROOT + p.u;
      return '<article class="post-row">' +
        '<a class="thumb" href="' + url + '" tabindex="-1" aria-hidden="true"><img src="' + ROOT + p.img + '" alt="" loading="lazy"></a>' +
        '<div class="post-row-body"><a class="kicker cat-' + p.c + '" href="' + ROOT + p.c + '/index.html">' + escapeHtml(p.cn) + "</a>" +
        '<h3><a href="' + url + '">' + highlight(p.t, q) + "</a></h3>" +
        "<p>" + highlight(p.e, q) + "</p>" +
        '<div class="meta"><span>' + p.d + "</span><span>" + p.m + " phút đọc</span></div></div></article>";
    }).join("");
  }

  /* ---------- Bài viết: bảng, nút copy code, tiến độ đọc ---------- */
  $$(".prose table").forEach(function (t) {
    var wrap = document.createElement("div");
    wrap.className = "table-wrap";
    t.parentNode.insertBefore(wrap, t);
    wrap.appendChild(t);
  });

  function copyText(text, done) {
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(done, function () { fallbackCopy(text); done(); });
    } else { fallbackCopy(text); done(); }
  }
  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) { /* bỏ qua */ }
    document.body.removeChild(ta);
  }

  $$(".prose pre").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.type = "button";
    btn.textContent = "Sao chép";
    btn.addEventListener("click", function () {
      copyText(pre.querySelector("code").innerText, function () {
        btn.textContent = "Đã chép ✓";
        setTimeout(function () { btn.textContent = "Sao chép"; }, 1600);
      });
    });
    pre.appendChild(btn);
  });

  $$(".copy-link").forEach(function (btn) {
    btn.addEventListener("click", function () {
      copyText(btn.getAttribute("data-url"), function () {
        btn.classList.add("copied");
        setTimeout(function () { btn.classList.remove("copied"); }, 1600);
      });
    });
  });

  var progress = $(".progress");
  var article = $(".prose");
  var toTop = $(".to-top");
  function onScroll() {
    var y = window.scrollY;
    if (progress && article) {
      var rect = article.getBoundingClientRect();
      var total = article.offsetHeight - window.innerHeight + 200;
      var pct = Math.min(100, Math.max(0, (-rect.top + 200) / total * 100));
      progress.style.width = pct + "%";
    }
    if (toTop) toTop.classList.toggle("show", y > 600);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
  if (toTop) toTop.addEventListener("click", function () { window.scrollTo({ top: 0 }); });
})();
