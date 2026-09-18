# Crafted & Cherished - Complete Website Clone (Mirror & Data Archive)

## 📌 Description (Darija)
Had l-projet huwa clone kamel w 100% self-contained dyal l-website dyal crochet [craftedandcherished.com](https://craftedandcherished.com/).
T-clona mn kolchi:
1. **Frontend Static Kamel**: Ga3 les pages HTML (Home, Blog, Categories, 157 Articles/Posts, Pages About, Contact, Privacy Policy, Pagination).
2. **Assets Kamlin**: Ga3 les styles CSS (GeneratePress, GenerateBlocks), fonts WOFF2 (Marcellus, Nunito, Allura), scripts JS, w tsawer dyal crochet.
3. **Clean & Fast**: T-7eydo ga3 les scripts dyal les pubs (Mediavine/Journey, Prebid, Google Tag Manager) bach l-site y-khdem tayra w y-koun nqi.
4. **Data Kamla (JSON & XML)**:
   - `data/posts.json` (157 articles kamlin)
   - `data/pages.json`
   - `data/categories.json`
   - `data/tags.json`
   - `data/media.json` (631 image records)
   - `data/craftedandcherished_export.xml` (WordPress WXR export ready bach t-importh f ay WordPress jdida direct mn Tools -> Import).
5. **Content Markdown**: Ga3 les articles m-7totin f `content/posts/*.md` b-YAML frontmatter (khasin b Astro, Next.js, Hugo, etc.).

---

## 🚀 Kifach T-khdem L-website f Local (Run Local Server)

### 1. Khedem b Python Server (Recommended - Clean URLs):
```bash
python3 server.py
```
W ftah f l-browser: [http://localhost:8080](http://localhost:8080)

### 2. Khedem b NPM:
```bash
npm start
# wla
npm run serve
```

---

## 📂 Structure dyal L-projet

```
craftedandcherished/
├── index.html                    # Homepage
├── about/index.html              # About page
├── contact/index.html            # Contact page
├── privacy-policy/index.html     # Privacy Policy page
├── blog/                         # Blog archive & pagination (1 to 16)
│   ├── index.html
│   └── page/
├── category/                     # Category archives & pagination
│   ├── crochet-blog/
│   ├── crochet-home-decor/
│   ├── crochet-inspiration/
│   ├── crochet-wearables/
│   └── free-crochet-patterns/
├── {post-slug}/index.html        # 157 Single post pages
├── wp-content/                   # Local assets (CSS, JS, Fonts, Images)
│   ├── uploads/
│   ├── themes/generatepress/
│   └── plugins/
├── wp-includes/                  # Core JS & styles (jQuery, etc.)
├── content/                      # Clean Markdown version
│   ├── posts/                    # 157 Markdown files with YAML frontmatter
│   └── pages/                    # 5 Markdown files
├── data/                         # Database exports
│   ├── posts.json
│   ├── pages.json
│   ├── categories.json
│   ├── tags.json
│   ├── media.json
│   └── craftedandcherished_export.xml  # WordPress Import ready file
├── server.py                     # Custom local HTTP server with clean URLs
├── package.json
└── README.md
```

---

## 🔒 Image Safety Audit Compliance
Had l-clone m-tebbeq fih l-rule dyal image filtering (No girls / female model photos). Ga3 tsawer m-khtarin b 3inaya w fihom ghir crochet craft, flat lays, bags, amigurumi, decor, w materials.
