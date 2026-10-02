# HọcFree.vn

Website tĩnh (HTML + CSS + JavaScript thuần) chia sẻ kiến thức lập trình, ngoại ngữ và blog, chạy trên **GitHub Pages** với tên miền **hocfree.vn**.

## Cấu trúc

```
index.html                 Trang chủ
kien-thuc-lap-trinh/       Chuyên mục + bài viết
ngoai-ngu/                 Chuyên mục + bài viết
blog/                      Chuyên mục + bài viết
search.html, gioi-thieu.html, 404.html
assets/css/style.css       Giao diện (sáng/tối, responsive)
assets/js/main.js          Tìm kiếm, menu mobile, copy code, dark mode…
assets/js/search-data.js   Chỉ mục tìm kiếm (tự sinh)
assets/images/posts/       Ảnh đại diện bài viết (1200x675)
src/posts.json             Danh sách bài viết, chuyên mục, bài "đọc nhiều"
src/posts/<slug>.html      Nội dung từng bài
tools/build.py             Sinh toàn bộ trang HTML từ src/
tools/make_thumbs.py       Vẽ ảnh đại diện tự động
CNAME                      Tên miền riêng: hocfree.vn
```

> Các file `.html` ở thư mục gốc và trong các chuyên mục được **sinh tự động**, hãy sửa trong `src/` rồi build lại.

## Thêm bài viết mới

1. Thêm một mục vào `posts` trong `src/posts.json` (slug, category, title, excerpt, date, tags, thumb).
2. Tạo file `src/posts/<slug>.html` chứa phần thân bài (`<h2>`, `<p>`, `<ul>`, `<pre><code>`…).
3. Ảnh đại diện: chép ảnh thật vào `assets/images/posts/<slug>.jpg` (tỉ lệ 16:9), hoặc chạy
   `python tools/make_thumbs.py` để vẽ tự động.
4. `python tools/build.py`
5. `git add . && git commit -m "Thêm bài ..." && git push`

## Xem thử trên máy

```
python -m http.server 8000
```
Mở http://localhost:8000

## Trỏ tên miền (Mắt Bão → GitHub Pages)

| Loại  | Host | Giá trị                    |
|-------|------|----------------------------|
| A     | @    | 185.199.108.153            |
| A     | @    | 185.199.109.153            |
| A     | @    | 185.199.110.153            |
| A     | @    | 185.199.111.153            |
| CNAME | www  | `<tên-tài-khoản>.github.io` |

Sau khi DNS cập nhật: GitHub repo → Settings → Pages → Custom domain `hocfree.vn` → bật **Enforce HTTPS**.
