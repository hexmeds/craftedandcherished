#!/usr/bin/env python3
import os
import re
import sys
import json
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import html2text

BASE_URL = "https://craftedandcherished.com"
DEST_DIR = "/data/data/com.termux/files/home/craftedandcherished"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Forbidden image patterns (Rule: NO images of girls/women/models)
FORBIDDEN_URL_PATTERNS = [
    'wearing-floral-crochet-headscarf',
    'beginner-crochet-bandana-yarn-hook',
    'crochet-daisy-backpack-worn-outdoors',
    'simple-crochet-top-pattern-for-women',
    'stefan-stefancik-QXevDflbl8A',
    'susan-elizabeth-jones-ohYXl4U7gbY',
    'iam_os-ArVjpHI04N0',
    'rodeo-project-management-software',
    'paige-cody-ITTqjS3UpoY',
    'female_vector',
    'determined-woman-throws-darts',
    'raymond-petrik-SEUwArtIcPc'
]

def is_forbidden_image(url, alt=""):
    url_lower = url.lower()
    alt_lower = alt.lower()
    for p in FORBIDDEN_URL_PATTERNS:
        if p in url_lower:
            return True
    for kw in ['woman', 'women', 'girl', 'girls', 'lady', 'ladies', 'model']:
        if re.search(r'\b' + kw + r'\b', alt_lower):
            return True
    return False

def download_file(url, dest_path):
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            return True, dest_path
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code == 200:
            with open(dest_path, "wb") as f:
                f.write(r.content)
            return True, dest_path
        return False, f"Status {r.status_code}"
    except Exception as e:
        return False, str(e)

# Initialize html2text converter
h2t = html2text.HTML2Text()
h2t.ignore_links = False
h2t.ignore_images = False
h2t.body_width = 0

print("=" * 60)
print(f"[*] STEP 1: Fetching WordPress REST API Data")
print("=" * 60)

os.makedirs(DEST_DIR, exist_ok=True)
data_dir = os.path.join(DEST_DIR, "data")
content_dir = os.path.join(DEST_DIR, "content")
os.makedirs(data_dir, exist_ok=True)
os.makedirs(os.path.join(content_dir, "posts"), exist_ok=True)
os.makedirs(os.path.join(content_dir, "pages"), exist_ok=True)

def fetch_all_wp(endpoint):
    items = []
    page = 1
    while True:
        url = f"{BASE_URL}/wp-json/wp/v2/{endpoint}?per_page=100&page={page}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=25)
            if r.status_code != 200:
                break
            data = r.json()
            if not data or not isinstance(data, list):
                break
            items.extend(data)
            print(f"  Fetched {endpoint} page {page}: {len(data)} items (Total: {len(items)})")
            page += 1
        except Exception as e:
            print(f"  Error on {endpoint} page {page}: {e}")
            break
    return items

posts = fetch_all_wp("posts")
pages = fetch_all_wp("pages")
categories = fetch_all_wp("categories")
tags = fetch_all_wp("tags")
media = fetch_all_wp("media")

with open(os.path.join(data_dir, "posts.json"), "w", encoding="utf-8") as f:
    json.dump(posts, f, indent=2, ensure_ascii=False)
with open(os.path.join(data_dir, "pages.json"), "w", encoding="utf-8") as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)
with open(os.path.join(data_dir, "categories.json"), "w", encoding="utf-8") as f:
    json.dump(categories, f, indent=2, ensure_ascii=False)
with open(os.path.join(data_dir, "tags.json"), "w", encoding="utf-8") as f:
    json.dump(tags, f, indent=2, ensure_ascii=False)
with open(os.path.join(data_dir, "media.json"), "w", encoding="utf-8") as f:
    json.dump(media, f, indent=2, ensure_ascii=False)

cat_map = {c['id']: c['name'] for c in categories}
tag_map = {t['id']: t['name'] for t in tags}
media_map = {m['id']: m.get('source_url', '') for m in media}

print(f"[+] Exported {len(posts)} posts, {len(pages)} pages, {len(categories)} categories, {len(tags)} tags, {len(media)} media records.")

print("=" * 60)
print(f"[*] STEP 2: Creating Markdown files with YAML frontmatter")
print("=" * 60)

for p in posts:
    slug = p.get('slug', f"post-{p['id']}")
    title = p.get('title', {}).get('rendered', '')
    date = p.get('date', '')
    modified = p.get('modified', '')
    post_cats = [cat_map.get(cid, str(cid)) for cid in p.get('categories', [])]
    post_tags = [tag_map.get(tid, str(tid)) for tid in p.get('tags', [])]
    feat_img_id = p.get('featured_media')
    feat_img_url = media_map.get(feat_img_id, '') if feat_img_id else ''
    excerpt = p.get('excerpt', {}).get('rendered', '').strip()
    raw_html = p.get('content', {}).get('rendered', '')
    
    md_content = h2t.handle(raw_html)
    
    frontmatter = f"""---
title: "{title.replace('\"', '\\\"')}"
date: "{date}"
modified: "{modified}"
slug: "{slug}"
categories: {json.dumps(post_cats)}
tags: {json.dumps(post_tags)}
featured_image: "{feat_img_url}"
excerpt: "{excerpt.replace('\"', '\\\"').replace('\n', ' ')}"
---

{md_content}
"""
    with open(os.path.join(content_dir, "posts", f"{slug}.md"), "w", encoding="utf-8") as f:
        f.write(frontmatter)

for pg in pages:
    slug = pg.get('slug', f"page-{pg['id']}")
    title = pg.get('title', {}).get('rendered', '')
    date = pg.get('date', '')
    raw_html = pg.get('content', {}).get('rendered', '')
    md_content = h2t.handle(raw_html)
    frontmatter = f"""---
title: "{title.replace('\"', '\\\"')}"
date: "{date}"
slug: "{slug}"
---

{md_content}
"""
    with open(os.path.join(content_dir, "pages", f"{slug}.md"), "w", encoding="utf-8") as f:
        f.write(frontmatter)

print(f"[+] Created Markdown files for all posts and pages in {content_dir}")

print("=" * 60)
print(f"[*] STEP 3: Compiling List of All HTML URLs to Clone")
print("=" * 60)

urls_to_clone = []

# Home
urls_to_clone.append((f"{BASE_URL}/", os.path.join(DEST_DIR, "index.html")))

# Pages
for pg in pages:
    slug = pg['slug']
    if slug == 'home':
        continue
    rel_path = os.path.join(DEST_DIR, slug, "index.html")
    urls_to_clone.append((f"{BASE_URL}/{slug}/", rel_path))

# Blog pagination (1 to 16)
urls_to_clone.append((f"{BASE_URL}/blog/", os.path.join(DEST_DIR, "blog", "index.html")))
for page_num in range(2, 17):
    urls_to_clone.append((f"{BASE_URL}/blog/page/{page_num}/", os.path.join(DEST_DIR, "blog", "page", str(page_num), "index.html")))

# Categories & pagination
cat_page_counts = {
    'crochet-blog': 2,
    'crochet-home-decor': 6,
    'crochet-inspiration': 1,
    'crochet-wearables': 6,
    'free-crochet-patterns': 3
}

for cat_slug, total_p in cat_page_counts.items():
    urls_to_clone.append((f"{BASE_URL}/category/{cat_slug}/", os.path.join(DEST_DIR, "category", cat_slug, "index.html")))
    for p_num in range(2, total_p + 1):
        urls_to_clone.append((f"{BASE_URL}/category/{cat_slug}/page/{p_num}/", os.path.join(DEST_DIR, "category", cat_slug, "page", str(p_num), "index.html")))

# Posts (all 157)
for p in posts:
    slug = p['slug']
    urls_to_clone.append((f"{BASE_URL}/{slug}/", os.path.join(DEST_DIR, slug, "index.html")))

print(f"[+] Total HTML pages to clone: {len(urls_to_clone)}")

print("=" * 60)
print(f"[*] STEP 4: Downloading HTML Pages")
print("=" * 60)

raw_html_cache = {}

def fetch_html_page(item):
    url, out_path = item
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)
        if r.status_code == 200:
            return url, out_path, r.text, None
        return url, out_path, None, f"Status {r.status_code}"
    except Exception as e:
        return url, out_path, None, str(e)

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(fetch_html_page, item) for item in urls_to_clone]
    completed = 0
    for f in as_completed(futures):
        url, out_path, html, err = f.result()
        completed += 1
        if html:
            raw_html_cache[out_path] = (url, html)
            if completed % 25 == 0 or completed == len(urls_to_clone):
                print(f"  Downloaded HTML {completed}/{len(urls_to_clone)}")
        else:
            print(f"  Failed {url}: {err}")

print(f"[+] Successfully fetched {len(raw_html_cache)} HTML pages.")

print("=" * 60)
print(f"[*] STEP 5: Extracting and Downloading All Assets (CSS, JS, Fonts, Images)")
print("=" * 60)

asset_urls = set()

# Regexes for asset extraction
re_css = re.compile(r'<link[^>]+rel=[\'\"]stylesheet[\'\"][^>]+href=[\'\"]([^\'\"]+)[\'\"]')
re_js = re.compile(r'<script[^>]+src=[\'\"]([^\'\"]+)[\'\"]')
re_img = re.compile(r'<img[^>]+src=[\'\"]([^\'\"]+)[\'\"]')
re_srcset = re.compile(r'srcset=[\'\"]([^\'\"]+)[\'\"]')
re_font = re.compile(r'url\([\'\"]?(https://craftedandcherished\.com/[^\'\"\)]+\.woff2?)[\'\"]?\)')

for out_path, (page_url, html) in raw_html_cache.items():
    for m in re_css.findall(html):
        asset_urls.add(m.split('?')[0])
    for m in re_js.findall(html):
        asset_urls.add(m.split('?')[0])
    for m in re_img.findall(html):
        asset_urls.add(m.split('?')[0])
    for srcset in re_srcset.findall(html):
        for part in srcset.split(','):
            src = part.strip().split(' ')[0]
            if src:
                asset_urls.add(src.split('?')[0])
    for m in re_font.findall(html):
        asset_urls.add(m.split('?')[0])

# Also add media items from REST API
for m in media:
    src = m.get('source_url', '')
    if src:
        asset_urls.add(src.split('?')[0])
    details = m.get('media_details', {}).get('sizes', {})
    for sz_name, sz_info in details.items():
        sz_src = sz_info.get('source_url', '')
        if sz_src:
            asset_urls.add(sz_src.split('?')[0])

# Known fonts from fonts.css
known_fonts = [
    "https://craftedandcherished.com/wp-content/uploads/generatepress/fonts/marcellus/wEO_EBrOk8hQLDvIAF81VvoK.woff2",
    "https://craftedandcherished.com/wp-content/uploads/generatepress/fonts/nunito/XRXV3I6Li01BKofINeaB.woff2",
    "https://craftedandcherished.com/wp-content/uploads/generatepress/fonts/nunito/XRXX3I6Li01BKofIMNaDRs4.woff2",
    "https://craftedandcherished.com/wp-content/uploads/generatepress/fonts/allura/9oRPNYsQpS4zjuA_iwgW.woff2"
]
for kf in known_fonts:
    asset_urls.add(kf)

# Filter assets: only internal (wp-content or wp-includes on craftedandcherished.com)
internal_assets = []
for a in asset_urls:
    if a.startswith('//'):
        a = 'https:' + a
    if a.startswith(BASE_URL):
        # Check rule: No girl / woman photos
        if is_forbidden_image(a):
            continue
        rel = a[len(BASE_URL):].lstrip('/')
        # Don't download dynamic php files or ad endpoints
        if any(rel.endswith(ext) for ext in ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot', '.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico']):
            dest_file = os.path.join(DEST_DIR, rel)
            internal_assets.append((a, dest_file))

print(f"[+] Found {len(internal_assets)} internal assets to download.")

def download_asset_task(item):
    url, dest_path = item
    ok, res = download_file(url, dest_path)
    return url, ok, res

with ThreadPoolExecutor(max_workers=12) as executor:
    futures = [executor.submit(download_asset_task, item) for item in internal_assets]
    downloaded = 0
    for f in as_completed(futures):
        url, ok, res = f.result()
        downloaded += 1
        if downloaded % 50 == 0 or downloaded == len(internal_assets):
            print(f"  Downloaded asset {downloaded}/{len(internal_assets)}")

print(f"[+] Finished asset downloads.")

print("=" * 60)
print(f"[*] STEP 6: Cleaning and Rewriting HTML Files")
print("=" * 60)

# Create a neutral craft placeholder svg for any forbidden images that might be referenced
placeholder_svg_rel = "wp-content/uploads/placeholder-crochet.svg"
placeholder_svg_path = os.path.join(DEST_DIR, placeholder_svg_rel)
os.makedirs(os.path.dirname(placeholder_svg_path), exist_ok=True)
with open(placeholder_svg_path, "w", encoding="utf-8") as f:
    f.write('''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="0 0 600 400" fill="#fdfbf7">
<rect width="600" height="400" fill="#f5ede3"/>
<circle cx="300" cy="200" r="80" fill="#e8dacb"/>
<path d="M260,200 C260,160 340,160 340,200 C340,240 260,240 260,200 Z" fill="none" stroke="#b08968" stroke-width="6"/>
<text x="300" y="290" font-family="sans-serif" font-size="20" fill="#7f5539" text-anchor="middle">Crafted &amp; Cherished Crochet</text>
</svg>''')

ad_script_patterns = [
    r'<script[^>]*journeymv[^>]*>.*?</script>',
    r'<script[^>]*prebid[^>]*>.*?</script>',
    r'<script[^>]*googletagmanager[^>]*>.*?</script>',
    r'<script[^>]*google-site-kit[^>]*>.*?</script>',
    r'<script[^>]*scriptwrapper[^>]*>.*?</script>',
    r'<script[^>]*cloudfront[^>]*>.*?</script>',
]

for out_path, (page_url, html) in raw_html_cache.items():
    # 1. Remove ad / analytics scripts
    cleaned_html = html
    for pat in ad_script_patterns:
        cleaned_html = re.sub(pat, '', cleaned_html, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. Replace forbidden images
    for p in FORBIDDEN_URL_PATTERNS:
        cleaned_html = re.sub(r'https://craftedandcherished\.com/wp-content/uploads/[^\'\"\s]*' + p + r'[^\'\"\s]*', f'/{placeholder_svg_rel}', cleaned_html)
        cleaned_html = re.sub(r'/wp-content/uploads/[^\'\"\s]*' + p + r'[^\'\"\s]*', f'/{placeholder_svg_rel}', cleaned_html)

    # 3. Replace site absolute URLs with relative paths
    cleaned_html = cleaned_html.replace("https://craftedandcherished.com/", "/")
    cleaned_html = cleaned_html.replace("https:\\/\\/craftedandcherished.com\\/", "\\/")
    cleaned_html = cleaned_html.replace("//craftedandcherished.com/", "/")
    
    # 4. Remove external ad CSS or broken endpoints
    cleaned_html = re.sub(r'<link[^>]+href=[\'\"][^\'\"]*(?:journeymv|prebid|google-site-kit)[^\'\"]*[\'\"][^>]*>', '', cleaned_html)
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(cleaned_html)

print(f"[+] Cleaned and written {len(raw_html_cache)} HTML files.")

print("=" * 60)
print(f"[*] STEP 7: Rewriting CSS Files to Use Local Fonts and Assets")
print("=" * 60)

for root, dirs, files in os.walk(DEST_DIR):
    for fl in files:
        if fl.endswith('.css'):
            css_path = os.path.join(root, fl)
            try:
                with open(css_path, "r", encoding="utf-8", errors="ignore") as f:
                    c = f.read()
                c_new = c.replace("https://craftedandcherished.com/", "/")
                c_new = c_new.replace("//craftedandcherished.com/", "/")
                if c_new != c:
                    with open(css_path, "w", encoding="utf-8") as f:
                        f.write(c_new)
            except Exception as e:
                pass

print("[+] CSS files updated with local paths.")

print("=" * 60)
print(f"[*] STEP 8: Creating Local Dev Server & Package Configuration")
print("=" * 60)

# Local python server that handles clean URLs (e.g. /about serves /about/index.html)
server_py = """#!/usr/bin/env python3
import http.server
import socketserver
import os
import urllib.parse

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # If it's a directory or URL without extension
        full_path = os.path.join(DIRECTORY, path.lstrip('/'))
        if os.path.isdir(full_path):
            index_path = os.path.join(full_path, 'index.html')
            if os.path.exists(index_path):
                if not path.endswith('/'):
                    self.send_response(301)
                    new_path = path + '/'
                    if parsed.query:
                        new_path += '?' + parsed.query
                    self.send_header('Location', new_path)
                    self.end_headers()
                    return
        elif not os.path.exists(full_path):
            # Check if adding .html exists
            if os.path.exists(full_path + '.html'):
                self.path = path + '.html'
            # Check if directory with index.html exists
            elif os.path.exists(os.path.join(full_path, 'index.html')):
                self.send_response(301)
                new_path = path + '/'
                if parsed.query:
                    new_path += '?' + parsed.query
                self.send_header('Location', new_path)
                self.end_headers()
                return

        return super().do_GET()

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), CleanURLHandler) as httpd:
        print(f"[*] Crafted & Cherished local mirror running at http://localhost:{PORT}")
        print(f"[*] Press Ctrl+C to stop.")
        httpd.serve_forever()
"""

with open(os.path.join(DEST_DIR, "server.py"), "w", encoding="utf-8") as f:
    f.write(server_py)
os.chmod(os.path.join(DEST_DIR, "server.py"), 0o755)

# Package.json for quick npm workflows
pkg_json = {
    "name": "craftedandcherished-clone",
    "version": "1.0.0",
    "description": "100% complete static clone & content archive of craftedandcherished.com",
    "scripts": {
        "start": "python3 server.py",
        "serve": "npx serve ."
    },
    "author": "hexmeds",
    "license": "MIT"
}

with open(os.path.join(DEST_DIR, "package.json"), "w", encoding="utf-8") as f:
    json.dump(pkg_json, f, indent=2)

print("[+] Created server.py and package.json.")
print("=" * 60)
print("[*] COMPLETE CLONE FINISHED SUCCESSFULLY!")
print("=" * 60)
