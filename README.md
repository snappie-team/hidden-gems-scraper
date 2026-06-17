# hidden-gems-scraper

Tool CLI Python untuk scraping konten dari **TikTok**, **Instagram**, dan **Threads** berdasarkan hashtag, keyword, atau lokasi. Output berupa file CSV yang berisi data post (platform, lokasi, username, likes, comments, shares).

Cocok dipakai untuk riset tempat-tempat menarik yang belum viral, analisis tren konten lokal, atau pengumpulan data social media untuk keperluan marketing.

---

## Fitur

- Scraping dari tiga platform sekaligus atau per-platform
- Filter berdasarkan **hashtag**, **keyword**, dan/atau **lokasi**
- Deduplication otomatis — post yang sama tidak muncul dua kali
- Rate limiting bawaan antar request agar tidak kena ban
- Session management untuk Instagram (tidak perlu login ulang)
- Output CSV siap pakai, dengan timestamp di nama file

---

## Struktur Project

```
hidden-gems-scraper/
├── main.py              # CLI entry point
├── base_scraper.py      # Abstract base class semua scraper
├── config.py            # Konfigurasi dari environment variables
├── models.py            # Data model: Post, ScrapeQuery, ScrapeResult
├── requirements.txt
├── .env.example
├── scrapers/
│   ├── instagram.py     # Scraper Instagram (via instaloader)
│   ├── tiktok.py        # Scraper TikTok (via TikTokApi, async)
│   └── threads.py       # Scraper Threads (via Meta Graph API)
└── utils/
    └── __init__.py      # Helper CSV writer
```

---

## Instalasi

### 1. Clone dan buat virtual environment

```bash
git clone https://github.com/yourusername/hidden-gems-scraper.git
cd hidden-gems-scraper

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Playwright browser (wajib untuk TikTok)

```bash
playwright install chromium
```

### 4. Setup konfigurasi

Salin `.env.example` ke `.env` lalu isi sesuai kebutuhan:

```bash
cp .env.example .env
```

---

## Konfigurasi (.env)

```env
# Instagram - wajib untuk hashtag/location search
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password

# TikTok - ambil msToken dari cookie browser di tiktok.com
TIKTOK_MS_TOKEN=your_ms_token
TIKTOK_BROWSER=chromium

# Threads - Meta Graph API
# Docs: https://developers.facebook.com/docs/threads
THREADS_ACCESS_TOKEN=your_access_token
THREADS_USER_ID=your_user_id

# Delay antar request dalam detik (default: 1.5)
REQUEST_DELAY=1.5
```

### Cara dapat kredensial

| Platform  | Yang dibutuhkan | Cara mendapatkan |
|-----------|----------------|-----------------|
| Instagram | `INSTAGRAM_USERNAME` + `INSTAGRAM_PASSWORD` | Akun Instagram biasa. Setelah login pertama kali, session disimpan di `.sessions/instagram.session` |
| TikTok    | `TIKTOK_MS_TOKEN` | Buka `tiktok.com` di browser → DevTools → Application → Cookies → cari `msToken` |
| Threads   | `THREADS_ACCESS_TOKEN` | Buat app di [Meta for Developers](https://developers.facebook.com/), aktifkan Threads API, lalu generate token |

---

## Penggunaan

### Sintaks dasar

```bash
python main.py [--platform PLATFORM] [--hashtag HASHTAG] [--keyword KEYWORD] [--location LOCATION] [--max-results N] [--output FILE.csv]
```

Minimal salah satu dari `--hashtag`, `--keyword`, atau `--location` harus diisi.

### Contoh penggunaan

**Scraping semua platform berdasarkan hashtag:**
```bash
python main.py --hashtag kuliner --hashtag wisata
```

**Scraping TikTok saja dengan keyword:**
```bash
python main.py --platform tiktok --keyword "hidden gem jakarta"
```

**Scraping Instagram berdasarkan lokasi:**
```bash
python main.py --platform instagram --location "Bali"
```

**Kombinasi hashtag + keyword + lokasi, semua platform, 100 hasil:**
```bash
python main.py --hashtag hiddengemjakarta --keyword "kafe estetik" --location "Jakarta" --max-results 100
```

**Simpan ke file tertentu:**
```bash
python main.py --hashtag wisataalam --output hasil_wisata.csv
```

### Argumen CLI

| Argumen | Shorthand | Default | Keterangan |
|---------|-----------|---------|------------|
| `--platform` | `-p` | semua platform | Platform target: `tiktok`, `instagram`, `threads`. Bisa diulang. |
| `--hashtag` | - | - | Hashtag tanpa `#`. Bisa diulang. |
| `--keyword` | - | - | Keyword pencarian. Bisa diulang. |
| `--location` | `-l` | - | Nama lokasi atau location ID (Instagram). |
| `--max-results` | `-n` | `50` | Maksimum hasil per platform. |
| `--output` | `-o` | `output/scrape_<platform>_<timestamp>.csv` | Path file CSV output. |

---

## Format Output CSV

File CSV berisi kolom berikut:

| Kolom | Tipe | Keterangan |
|-------|------|-----------|
| `platform` | string | `tiktok`, `instagram`, atau `threads` |
| `lokasi` | string | Nama lokasi yang terdeteksi dari post |
| `username` | string | Username pembuat konten |
| `likes` | integer | Jumlah likes / diggs |
| `comments` | integer | Jumlah komentar / replies |
| `shares` | integer | Jumlah share / repost |

Contoh isi CSV:

```
platform,lokasi,username,likes,comments,shares
tiktok,Kawah Putih Bandung,traveler_id,15420,230,891
instagram,Bali,explorerbali,3200,45,0
threads,,foodie_jakarta,980,12,34
```

---

## Catatan Penting

- **Instagram**: Penggunaan berlebihan bisa memicu rate limit atau temporary block dari Instagram. Gunakan delay yang cukup (`REQUEST_DELAY=2.0` atau lebih).
- **TikTok**: `ms_token` bersifat sementara dan perlu diperbarui secara berkala. Ambil ulang dari cookie browser jika scraping tiba-tiba gagal.
- **Threads**: Threads Graph API memiliki keterbatasan — tidak semua post bisa diakses tergantung permission app yang didaftarkan di Meta Developer.
- Jangan commit file `.env` ke repository. File ini sudah ada di `.gitignore`.

---

## Dependencies

| Library | Versi | Kegunaan |
|---------|-------|---------|
| `instaloader` | ≥4.13 | Scraping Instagram |
| `TikTokApi` | ≥6.5.0 | Scraping TikTok |
| `playwright` | ≥1.44.0 | Browser automation untuk TikTok |
| `httpx` | ≥0.27.0 | HTTP client untuk Threads API |
| `python-dotenv` | ≥1.0.0 | Load environment variables dari `.env` |

---

## Lisensi

MIT
