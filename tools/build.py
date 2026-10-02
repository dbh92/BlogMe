"""Sinh toàn bộ website tĩnh HọcFree từ src/posts.json + src/posts/*.html.

Chạy:  python tools/build.py

Thêm bài viết mới:
  1. Thêm một mục vào "posts" trong src/posts.json
  2. Tạo file nội dung src/posts/<slug>.html (chỉ phần thân bài, dùng h2/p/ul/pre…)
  3. python tools/make_thumbs.py   (vẽ ảnh đại diện nếu chưa có ảnh)
  4. python tools/build.py
"""
import html
import json
import os
import re
import unicodedata
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
VERSION = date.today().strftime("%Y%m%d")

with open(os.path.join(SRC, "posts.json"), encoding="utf-8") as fh:
    DATA = json.load(fh)

SITE = DATA["site"]
CATS = {c["slug"]: c for c in DATA["categories"]}
POSTS = sorted(DATA["posts"], key=lambda p: p["date"], reverse=True)
BY_SLUG = {p["slug"]: p for p in POSTS}
e = html.escape


# ---------------------------------------------------------------- tiện ích
def slugify(text):
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def fmt_date(iso):
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"


def strip_tags(s):
    return re.sub(r"<[^>]+>", " ", s)


def post_url(p):
    return f"{p['category']}/{p['slug']}.html"


def img_url(p):
    return f"assets/images/posts/{p['slug']}.jpg"


def load_body(p):
    with open(os.path.join(SRC, "posts", p["slug"] + ".html"), encoding="utf-8") as fh:
        return fh.read()


for _p in POSTS:
    _p["body"] = load_body(_p)
    _words = len(strip_tags(_p["body"]).split())
    _p["minutes"] = max(1, -(-_words // 180))  # ~180 từ/phút, làm tròn lên
    _p["cat"] = CATS[_p["category"]]


def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(content)
    print("  ghi", rel)


# ---------------------------------------------------------------- khung trang
LOGO = """<svg class="logo-mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="var(--accent)"/><path d="M11 13l-5 7 5 7M29 13l5 7-5 7M23 10l-6 20" stroke="#fff" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>"""

ICON = {
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>',
    "moon": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>',
    "close": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    "cal": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
    "fb": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 8h3V4h-3a4 4 0 0 0-4 4v2H8v4h2v6h4v-6h3l1-4h-4V8z"/></svg>',
    "x": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4l16 16M20 4L4 20"/></svg>',
    "link": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 10a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>',
    "up": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg>',
}

TRENDING = ["HTML", "JavaScript", "Python", "Git", "SQL", "IELTS", "Tiếng Hàn", "VS Code", "AI"]


def head(root, title, desc, canonical, image, og_type="website", extra=""):
    full_title = f"{title} | {SITE['name']}" if title != SITE["name"] else f"{SITE['name']} – {SITE['tagline']}"
    img_abs = f"{SITE['domain']}/{image}"
    return f"""<!DOCTYPE html>
<html lang="vi" data-root="{root}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE['domain']}/{canonical}">
<meta property="og:site_name" content="{e(SITE['name'])}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE['domain']}/{canonical}">
<meta property="og:image" content="{img_abs}">
<meta property="og:locale" content="vi_VN">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#16181d">
<link rel="icon" href="{root}assets/images/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/style.css?v={VERSION}">
<script>try{{var t=localStorage.getItem('hf-theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.classList.add('dark')}}catch(e){{}}</script>
{extra}</head>
<body>
<a class="skip-link" href="#main">Bỏ qua đến nội dung</a>
"""


def header(root, active=""):
    active_attr = ' class="active" aria-current="page"'
    nav = "".join(
        f'<li><a href="{root}{c["slug"]}/index.html"{active_attr if c["slug"] == active else ""}>{e(c["name"])}</a></li>'
        for c in DATA["categories"])
    trend = "".join(f'<a href="{root}search.html?q={e(t)}">{e(t)}</a>' for t in TRENDING)
    return f"""<div class="progress" aria-hidden="true"></div>
<header class="site-header">
  <div class="topbar">
    <div class="container topbar-inner">
      <button class="icon-btn burger" aria-label="Mở menu" aria-expanded="false">{ICON['menu']}</button>
      <a class="logo" href="{root}index.html" aria-label="{e(SITE['name'])} – Trang chủ">{LOGO}<span>Học<b>Free</b></span></a>
      <nav class="main-nav" aria-label="Menu chính">
        <ul>{nav}</ul>
      </nav>
      <div class="topbar-actions">
        <button class="icon-btn search-toggle" aria-label="Tìm kiếm">{ICON['search']}</button>
        <button class="icon-btn theme-toggle" aria-label="Đổi giao diện sáng/tối">{ICON['moon']}</button>
      </div>
    </div>
  </div>
  <div class="trending">
    <div class="container trending-inner">
      <span class="trending-label">Xu hướng</span>
      <div class="trending-links">{trend}</div>
    </div>
  </div>
</header>
<div class="search-panel" hidden>
  <div class="container">
    <form class="search-form" action="{root}search.html" role="search">
      {ICON['search']}
      <input type="search" name="q" placeholder="Tìm bài viết: JavaScript, IELTS, Git…" autocomplete="off" aria-label="Từ khóa tìm kiếm">
      <button type="button" class="icon-btn search-close" aria-label="Đóng">{ICON['close']}</button>
    </form>
    <div class="search-suggest"></div>
  </div>
</div>
"""


def footer(root):
    cats = "".join(f'<li><a href="{root}{c["slug"]}/index.html">{e(c["name"])}</a></li>' for c in DATA["categories"])
    latest = "".join(f'<li><a href="{root}{post_url(p)}">{e(p["title"])}</a></li>' for p in POSTS[:4])
    year = date.today().year
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-about">
      <a class="logo" href="{root}index.html">{LOGO}<span>Học<b>Free</b></span></a>
      <p>{e(SITE['description'])}</p>
    </div>
    <div>
      <h3>Chuyên mục</h3>
      <ul>{cats}</ul>
    </div>
    <div>
      <h3>Bài mới</h3>
      <ul>{latest}</ul>
    </div>
    <div>
      <h3>HọcFree</h3>
      <ul>
        <li><a href="{root}gioi-thieu.html">Giới thiệu</a></li>
        <li><a href="{root}search.html">Tìm kiếm</a></li>
        <li><a href="{root}sitemap.xml">Sitemap</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container">© {year} HọcFree.vn · Kiến thức là để chia sẻ.</div>
  </div>
</footer>
<button class="to-top" aria-label="Lên đầu trang">{ICON['up']}</button>
<script src="{root}assets/js/search-data.js?v={VERSION}" defer></script>
<script src="{root}assets/js/main.js?v={VERSION}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- thành phần
def cat_pill(root, p, cls="pill"):
    return f'<a class="{cls} cat-{p["category"]}" href="{root}{p["category"]}/index.html">{e(p["cat"]["name"])}</a>'


def meta(p, author=False):
    a = f'<span class="by">{e(SITE["author"])}</span>' if author else ""
    return (f'<div class="meta">{a}<span>{ICON["cal"]}<time datetime="{p["date"]}">{fmt_date(p["date"])}</time></span>'
            f'<span>{ICON["clock"]}{p["minutes"]} phút đọc</span></div>')


def card_overlay(root, p, big=False, eager=False):
    load = "eager" if eager else "lazy"
    return f"""<article class="card-overlay{' big' if big else ''}">
  <img src="{root}{img_url(p)}" alt="{e(p['title'])}" width="1200" height="675" loading="{load}">
  <div class="card-overlay-body">
    {cat_pill(root, p)}
    <h{2 if big else 3}><a href="{root}{post_url(p)}">{e(p['title'])}</a></h{2 if big else 3}>
    {'<p>' + e(p['excerpt']) + '</p>' if big else ''}
    {meta(p)}
  </div>
</article>"""


def post_row(root, p):
    return f"""<article class="post-row">
  <a class="thumb" href="{root}{post_url(p)}" tabindex="-1" aria-hidden="true"><img src="{root}{img_url(p)}" alt="" width="1200" height="675" loading="lazy"></a>
  <div class="post-row-body">
    {cat_pill(root, p, "kicker")}
    <h3><a href="{root}{post_url(p)}">{e(p['title'])}</a></h3>
    <p>{e(p['excerpt'])}</p>
    {meta(p, author=True)}
  </div>
</article>"""


def card(root, p):
    return f"""<article class="card">
  <a class="thumb" href="{root}{post_url(p)}" tabindex="-1" aria-hidden="true"><img src="{root}{img_url(p)}" alt="" width="1200" height="675" loading="lazy"></a>
  {cat_pill(root, p, "kicker")}
  <h3><a href="{root}{post_url(p)}">{e(p['title'])}</a></h3>
  {meta(p)}
</article>"""


def sidebar(root, current=None):
    popular = [BY_SLUG[s] for s in DATA["popular"] if s in BY_SLUG and s != current][:5]
    pop = "".join(
        f'<li><a href="{root}{post_url(p)}"><span class="num">{i}</span><span class="t">{e(p["title"])}</span></a></li>'
        for i, p in enumerate(popular, 1))
    cats = "".join(
        f'<li><a href="{root}{c["slug"]}/index.html"><span>{e(c["name"])}</span><span class="count">'
        f'{sum(1 for p in POSTS if p["category"] == c["slug"])}</span></a></li>'
        for c in DATA["categories"])
    tags = sorted({t for p in POSTS for t in p["tags"]}, key=str.lower)
    tag_html = "".join(f'<a class="tag" href="{root}search.html?q={e(t)}">{e(t)}</a>' for t in tags)
    return f"""<aside class="sidebar">
  <section class="widget">
    <h2 class="widget-title">Đọc nhiều nhất</h2>
    <ol class="popular">{pop}</ol>
  </section>
  <section class="widget">
    <h2 class="widget-title">Chuyên mục</h2>
    <ul class="cat-list">{cats}</ul>
  </section>
  <section class="widget widget-about">
    <h2 class="widget-title">Về HọcFree</h2>
    <p>Nơi chia sẻ <strong>miễn phí</strong> kiến thức lập trình, ngoại ngữ và kinh nghiệm tự học dành cho người Việt. Không quảng cáo, không thu phí.</p>
    <a class="btn" href="{root}gioi-thieu.html">Tìm hiểu thêm</a>
  </section>
  <section class="widget">
    <h2 class="widget-title">Thẻ</h2>
    <div class="tags">{tag_html}</div>
  </section>
</aside>"""


def section_title(text, link=None, root=""):
    more = f'<a class="more" href="{root}{link}">Xem tất cả →</a>' if link else ""
    return f'<div class="section-title"><h2>{e(text)}</h2>{more}</div>'


# ---------------------------------------------------------------- trang chủ
def build_home():
    root = ""
    hero_main, *hero_side = POSTS[:3]
    latest = POSTS[3:11]
    blocks = ""
    for c in DATA["categories"]:
        ps = [p for p in POSTS if p["category"] == c["slug"]][:4]
        first, rest = ps[0], ps[1:]
        items = "".join(
            f'<li><a href="{post_url(p)}">{e(p["title"])}</a><time datetime="{p["date"]}">{fmt_date(p["date"])}</time></li>'
            for p in rest)
        blocks += f"""<section class="cat-block cat-{c['slug']}">
  {section_title(c['name'], c['slug'] + '/index.html')}
  {card(root, first)}
  <ul class="cat-block-list">{items}</ul>
</section>"""
    page = head(root, SITE["name"], SITE["description"], "", "assets/images/og-default.jpg")
    page += header(root)
    page += f"""<main id="main">
  <section class="container hero">
    {card_overlay(root, hero_main, big=True, eager=True)}
    <div class="hero-side">
      {''.join(card_overlay(root, p, eager=True) for p in hero_side)}
    </div>
  </section>

  <div class="container layout">
    <div class="content">
      {section_title('Bài viết mới nhất')}
      <div class="post-list">
        {''.join(post_row(root, p) for p in latest)}
      </div>
    </div>
    {sidebar(root)}
  </div>

  <div class="band">
    <div class="container cat-blocks">
      {blocks}
    </div>
  </div>
</main>
"""
    page += footer(root)
    write("index.html", page)


# ---------------------------------------------------------------- chuyên mục
def build_category(c):
    root = "../"
    ps = [p for p in POSTS if p["category"] == c["slug"]]
    page = head(root, c["name"], c["description"], f"{c['slug']}/", img_url(ps[0]))
    page += header(root, active=c["slug"])
    page += f"""<main id="main">
  <div class="page-head cat-{c['slug']}">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{root}index.html">Trang chủ</a><span>/</span><span>{e(c['name'])}</span></nav>
      <h1>{e(c['name'])}</h1>
      <p>{e(c['description'])}</p>
      <span class="page-count">{len(ps)} bài viết</span>
    </div>
  </div>
  <section class="container hero hero-cat">
    {card_overlay(root, ps[0], big=True, eager=True)}
    <div class="hero-side">{''.join(card_overlay(root, p, eager=True) for p in ps[1:3])}</div>
  </section>
  <div class="container layout">
    <div class="content">
      {section_title('Tất cả bài viết')}
      <div class="post-list">{''.join(post_row(root, p) for p in ps)}</div>
    </div>
    {sidebar(root)}
  </div>
</main>
"""
    page += footer(root)
    write(f"{c['slug']}/index.html", page)


# ---------------------------------------------------------------- bài viết
def add_heading_ids(body):
    toc = []

    def repl(m):
        level, inner = m.group(1), m.group(2)
        hid = slugify(strip_tags(inner))
        if level == "2":
            toc.append((hid, strip_tags(inner).strip()))
        return f'<h{level} id="{hid}">{inner}</h{level}>'

    body = re.sub(r"<h([23])>(.*?)</h\1>", repl, body)
    return body, toc


def build_post(p):
    root = "../"
    url = post_url(p)
    body, toc = add_heading_ids(p["body"])
    toc_html = ""
    if len(toc) >= 3:
        toc_html = ('<details class="toc" open><summary>Nội dung bài viết</summary><ol>'
                    + "".join(f'<li><a href="#{h}">{e(t)}</a></li>' for h, t in toc) + "</ol></details>")
    same = [x for x in POSTS if x["category"] == p["category"] and x["slug"] != p["slug"]]
    others = [x for x in POSTS if x["category"] != p["category"]]
    related = (same + others)[:3]
    idx = POSTS.index(p)
    newer = POSTS[idx - 1] if idx > 0 else None
    older = POSTS[idx + 1] if idx + 1 < len(POSTS) else None
    pager = '<nav class="pager" aria-label="Bài trước/sau">'
    pager += (f'<a class="prev" href="{root}{post_url(older)}"><span>← Bài trước</span>{e(older["title"])}</a>'
              if older else "<span></span>")
    pager += (f'<a class="next" href="{root}{post_url(newer)}"><span>Bài tiếp →</span>{e(newer["title"])}</a>'
              if newer else "<span></span>")
    pager += "</nav>"
    tags = "".join(f'<a class="tag" href="{root}search.html?q={e(t)}">#{e(t)}</a>' for t in p["tags"])
    share_url = f"{SITE['domain']}/{url}"
    share = f"""<div class="share">
      <span>Chia sẻ:</span>
      <a class="share-btn fb" href="https://www.facebook.com/sharer/sharer.php?u={share_url}" target="_blank" rel="noopener" aria-label="Chia sẻ Facebook">{ICON['fb']}</a>
      <a class="share-btn x" href="https://twitter.com/intent/tweet?url={share_url}" target="_blank" rel="noopener" aria-label="Chia sẻ X">{ICON['x']}</a>
      <button class="share-btn copy-link" data-url="{share_url}" aria-label="Sao chép liên kết">{ICON['link']}</button>
    </div>"""
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Article", "headline": p["title"],
        "description": p["excerpt"], "image": f"{SITE['domain']}/{img_url(p)}",
        "datePublished": p["date"], "author": {"@type": "Organization", "name": SITE["author"]},
        "publisher": {"@type": "Organization", "name": SITE["name"]},
        "mainEntityOfPage": share_url}, ensure_ascii=False)
    extra = f'<script type="application/ld+json">{ld}</script>\n'

    page = head(root, p["title"], p["excerpt"], url, img_url(p), og_type="article", extra=extra)
    page += header(root, active=p["category"])
    page += f"""<main id="main">
  <div class="container layout article-layout">
    <article class="article">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{root}index.html">Trang chủ</a><span>/</span><a href="{root}{p['category']}/index.html">{e(p['cat']['name'])}</a></nav>
      <header class="article-head">
        {cat_pill(root, p)}
        <h1>{e(p['title'])}</h1>
        <p class="lead">{e(p['excerpt'])}</p>
        <div class="article-meta">
          <span class="avatar" aria-hidden="true">HF</span>
          {meta(p, author=True)}
        </div>
      </header>
      <figure class="article-cover">
        <img src="{root}{img_url(p)}" alt="{e(p['title'])}" width="1200" height="675">
      </figure>
      {toc_html}
      <div class="prose">
{body}
      </div>
      <footer class="article-foot">
        <div class="tags">{tags}</div>
        {share}
      </footer>
      <div class="author-box">
        <span class="avatar lg" aria-hidden="true">HF</span>
        <div>
          <strong>{e(SITE['author'])}</strong>
          <p>Chúng tôi viết những bài hướng dẫn dễ hiểu, thực tế để ai cũng có thể tự học lập trình và ngoại ngữ, hoàn toàn miễn phí.</p>
        </div>
      </div>
      {pager}
    </article>
    {sidebar(root, current=p['slug'])}
  </div>
  <section class="band">
    <div class="container">
      {section_title('Có thể bạn quan tâm')}
      <div class="card-grid">{''.join(card(root, r) for r in related)}</div>
    </div>
  </section>
</main>
"""
    page += footer(root)
    write(url, page)


# ---------------------------------------------------------------- trang phụ
def build_search():
    root = ""
    page = head(root, "Tìm kiếm", "Tìm kiếm bài viết trên HọcFree.", "search.html", "assets/images/og-default.jpg",
                extra='<meta name="robots" content="noindex">\n')
    page += header(root)
    page += f"""<main id="main">
  <div class="page-head">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{root}index.html">Trang chủ</a><span>/</span><span>Tìm kiếm</span></nav>
      <h1>Tìm kiếm</h1>
      <form class="search-form big" action="search.html" role="search">
        {ICON['search']}
        <input type="search" name="q" id="search-page-input" placeholder="Nhập từ khóa…" aria-label="Từ khóa tìm kiếm">
        <button class="btn" type="submit">Tìm</button>
      </form>
    </div>
  </div>
  <div class="container layout">
    <div class="content">
      <p class="search-summary" id="search-summary"></p>
      <div class="post-list" id="search-results"></div>
    </div>
    {sidebar(root)}
  </div>
</main>
"""
    page += footer(root)
    write("search.html", page)


def build_about():
    root = ""
    counts = "".join(
        f'<li><a href="{c["slug"]}/index.html"><strong>{e(c["name"])}</strong></a>: {e(c["description"])}</li>'
        for c in DATA["categories"])
    page = head(root, "Giới thiệu", "Giới thiệu về HọcFree.vn – website chia sẻ kiến thức miễn phí.",
                "gioi-thieu.html", "assets/images/og-default.jpg")
    page += header(root)
    page += f"""<main id="main">
  <div class="container layout article-layout">
    <article class="article">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="{root}index.html">Trang chủ</a><span>/</span><span>Giới thiệu</span></nav>
      <header class="article-head"><h1>Về HọcFree</h1>
      <p class="lead">Kiến thức là để chia sẻ. HọcFree ra đời với mong muốn ai cũng có thể tự học lập trình và ngoại ngữ mà không phải lo về chi phí.</p></header>
      <div class="prose">
        <h2>Chúng tôi viết về điều gì?</h2>
        <ul>{counts}</ul>
        <h2>Nguyên tắc</h2>
        <ul>
          <li><strong>Miễn phí mãi mãi</strong>: mọi bài viết đều đọc được mà không cần đăng ký.</li>
          <li><strong>Dễ hiểu</strong>: giải thích bằng tiếng Việt, ví dụ thực tế, có thể làm theo ngay.</li>
          <li><strong>Chính xác</strong>: nội dung được kiểm tra và cập nhật thường xuyên.</li>
        </ul>
        <h2>Công nghệ</h2>
        <p>Website được xây dựng hoàn toàn bằng HTML, CSS và JavaScript thuần, lưu trữ miễn phí trên GitHub Pages. Bạn có thể đọc bài <a href="blog/github-pages-ten-mien-rieng.html">Làm website miễn phí với GitHub Pages</a> để tự làm một trang như thế này.</p>
      </div>
    </article>
    {sidebar(root)}
  </div>
</main>
"""
    page += footer(root)
    write("gioi-thieu.html", page)


def build_404():
    # Trang 404 được GitHub Pages trả về ở mọi đường dẫn, nên dùng đường dẫn tuyệt đối
    root = "/"
    page = head(root, "Không tìm thấy trang", "Trang bạn tìm không tồn tại.", "404.html", "assets/images/og-default.jpg",
                extra='<meta name="robots" content="noindex">\n')
    page += header(root)
    page += f"""<main id="main">
  <div class="container notfound">
    <p class="big-404">404</p>
    <h1>Ối, trang này không tồn tại</h1>
    <p>Có thể đường dẫn đã bị thay đổi hoặc bài viết đã được chuyển đi. Hãy thử tìm kiếm nhé.</p>
    <form class="search-form big" action="/search.html" role="search">
      {ICON['search']}
      <input type="search" name="q" placeholder="Nhập từ khóa…" aria-label="Từ khóa tìm kiếm">
      <button class="btn" type="submit">Tìm</button>
    </form>
    <a class="btn ghost" href="/">← Về trang chủ</a>
  </div>
</main>
"""
    page += footer(root)
    write("404.html", page)


def build_search_data():
    items = [{
        "t": p["title"], "u": post_url(p), "e": p["excerpt"], "c": p["category"], "cn": p["cat"]["name"],
        "d": fmt_date(p["date"]), "m": p["minutes"], "img": img_url(p), "tags": p["tags"],
    } for p in POSTS]
    write("assets/js/search-data.js",
          "/* Tự động sinh bởi tools/build.py – không sửa tay */\nwindow.HF_POSTS = "
          + json.dumps(items, ensure_ascii=False, indent=1) + ";\n")


def build_sitemap():
    today = date.today().isoformat()
    urls = [("", today, "1.0")] + [(f"{c['slug']}/", today, "0.8") for c in DATA["categories"]]
    urls += [(post_url(p), p["date"], "0.7") for p in POSTS] + [("gioi-thieu.html", today, "0.3")]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{SITE['domain']}/{u}</loc><lastmod>{d}</lastmod><priority>{pr}</priority></url>\n"
                   for u, d, pr in urls)
    xml += "</urlset>\n"
    write("sitemap.xml", xml)
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE['domain']}/sitemap.xml\n")


def main():
    build_home()
    for c in DATA["categories"]:
        build_category(c)
    for p in POSTS:
        build_post(p)
    build_search()
    build_about()
    build_404()
    build_search_data()
    build_sitemap()
    print(f"Xong: {len(POSTS)} bài viết, {len(DATA['categories'])} chuyên mục.")


if __name__ == "__main__":
    main()
