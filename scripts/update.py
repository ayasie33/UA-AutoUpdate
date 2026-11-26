#!/usr/bin/env python3
"""Membuat user-agents.json.

- Otomatis: Chrome (Android/Desktop/iOS), Edge, Firefox (Android/Desktop)
  -> versi terbaru diambil dari API, riwayat = 9 versi mayor sebelumnya.
- Statis (ubah manual bila perlu): Safari iOS, Samsung Internet, Opera, Android lama.
- Jika pengambilan versi gagal, memakai versi dari JSON sebelumnya
  (atau DEFAULT di bawah bila belum ada).
"""
import datetime
import json
import pathlib
import urllib.request

OUT = pathlib.Path(__file__).resolve().parent.parent / "user-agents.json"
DEFAULT = {"chrome": 142, "firefox": 144}
HISTORY = 9  # jumlah versi mayor sebelumnya


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ua-updater/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)


def fetch_chrome():
    d = get_json(
        "https://versionhistory.googleapis.com/v1/chrome/platforms/win/"
        "channels/stable/versions?orderBy=version%20desc&pageSize=1"
    )
    return int(d["versions"][0]["version"].split(".")[0])


def fetch_firefox():
    d = get_json("https://product-details.mozilla.org/1.0/firefox_versions.json")
    return int(d["LATEST_FIREFOX_VERSION"].split(".")[0])


def previous_versions():
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))["meta"]["versions"]
    except Exception:
        return {}


def resolve_versions():
    prev = previous_versions()
    out = {}
    for key, fn in (("chrome", fetch_chrome), ("firefox", fetch_firefox)):
        try:
            out[key] = fn()
        except Exception as e:  # noqa: BLE001
            print(f"PERINGATAN: gagal ambil {key}: {e}")
            out[key] = prev.get(key, DEFAULT[key])
    return out


def item(label, ua):
    return {"label": label, "ua": ua}


def sec(title, items):
    return {"title": title, "items": items}


def auto(label, variants, ver):
    secs = []
    for os_name, tpl in variants:
        secs.append(sec(f"Terbaru · {os_name}", [item(f"{label} {ver}", tpl.format(v=ver))]))
    os_name, tpl = variants[0]
    secs.append(
        sec(
            f"Riwayat · {os_name}",
            [item(f"{label} {v}", tpl.format(v=v)) for v in range(ver - 1, ver - 1 - HISTORY, -1)],
        )
    )
    return secs


def cat(cid, name, color, sections, note=""):
    return {"id": cid, "name": name, "color": color, "note": note, "sections": sections}


CH_AND = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Mobile Safari/537.36"
CH_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
CH_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
CH_LIN = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
CRIOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{v}.0.0.0 Mobile/15E148 Safari/604.1"
FF_AND = "Mozilla/5.0 (Android 15; Mobile; rv:{v}.0) Gecko/{v}.0 Firefox/{v}.0"
FF_WIN = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
FF_MAC = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
FF_LIN = "Mozilla/5.0 (X11; Linux x86_64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
EDGE_WIN = CH_WIN.replace(" Safari/537.36", " Safari/537.36 Edg/{v}.0.0.0")
EDGE_AND = CH_AND + " EdgA/{v}.0.0.0"

SAFARI_IOS = [
    ("Safari 26.0 (iOS 26)", "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1"),
    ("Safari 18.6 (iOS 18)", "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1"),
    ("Safari 17.6 (iOS 17)", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1"),
    ("Safari 16.7 (iOS 16)", "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.7 Mobile/15E148 Safari/604.1"),
    ("Safari 15.6 (iOS 15)", "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1"),
    ("Safari iPad 18.6", "Mozilla/5.0 (iPad; CPU OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Mobile/15E148 Safari/604.1"),
]

SAMSUNG = [
    ("Samsung Internet 28.0", "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/28.0 Chrome/130.0.0.0 Mobile Safari/537.36"),
    ("Samsung Internet 27.0", "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/27.0 Chrome/125.0.0.0 Mobile Safari/537.36"),
    ("Samsung Internet 26.0", "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/26.0 Chrome/122.0.0.0 Mobile Safari/537.36"),
    ("Samsung Internet 25.0", "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.36"),
]

OPERA = [
    ("Opera 120 · Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 OPR/120.0.0.0"),
    ("Opera 119 · Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 OPR/119.0.0.0"),
    ("Opera 118 · Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0"),
    ("Opera 117 · Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/117.0.0.0"),
]

# Contoh tipikal Chrome di Android lama (build ID bisa berbeda di tiap perangkat).
LEGACY_ANDROID = [
    ("Android 9 (Pie)", "Mozilla/5.0 (Linux; Android 9; Pixel 2 XL Build/PPR1.180610.009) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.91 Mobile Safari/537.36"),
    ("Android 8.0 (Oreo)", "Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 Build/OPD1.170816.010) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36"),
    ("Android 7.0 (Nougat)", "Mozilla/5.0 (Linux; Android 7.0; Nexus 5X Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.91 Mobile Safari/537.36"),
    ("Android 6.0 (Marshmallow)", "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.81 Mobile Safari/537.36"),
    ("Android 5.0 (Lollipop)", "Mozilla/5.0 (Linux; Android 5.0; Nexus 5 Build/LRX21O) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.89 Mobile Safari/537.36"),
    ("Android 4.4 (KitKat)", "Mozilla/5.0 (Linux; Android 4.4.2; Nexus 5 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.102 Mobile Safari/537.36"),
]


# ---------- Template tambahan ----------
CH_TAB = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
CH_CROS = "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36"
FF_UBU = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
FXIOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/{v}.0 Mobile/15E148 Safari/605.1.15"
EDGE_IOS = "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 EdgiOS/{v}.0.0.0 Mobile/15E148 Safari/605.1.15"
WEBVIEW = "Mozilla/5.0 (Linux; Android 10; K; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{v}.0.0.0 Mobile Safari/537.36"
GOOGLEBOT_DESKTOP = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/{v}.0.0.0 Safari/537.36"
GOOGLEBOT_MOBILE = "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
BINGBOT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm) Chrome/{v}.0.0.0 Safari/537.36"

# ---------- Data statis ----------
SAFARI_MAC = [
    ("Safari 26.0 (macOS 26)", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Safari/605.1.15"),
    ("Safari 18.6", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 Safari/605.1.15"),
    ("Safari 17.6", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"),
    ("Safari 16.6", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15"),
    ("Safari 15.6", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15"),
]

OPERA_ANDROID = [
    ("Opera Android (contoh)", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36 OPR/86.0.0.0"),
]

OTHER_BROWSERS = [
    ("UC Browser (Android)", "Mozilla/5.0 (Linux; U; Android 9; en-US; Redmi Note 7 Build/PKQ1.180904.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/13.4.0.1306 Mobile Safari/537.36"),
    ("MIUI Browser (Xiaomi)", "Mozilla/5.0 (Linux; U; Android 13; id-id; Redmi Note 12 Build/TKQ1.221114.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/112.0.5615.136 Mobile Safari/537.36 XiaoMi/MiuiBrowser/14.5.0-g"),
    ("Yandex Browser · Windows", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36"),
    ("Tor Browser 15 (ESR 140)", "Mozilla/5.0 (Windows NT 10.0; rv:140.0) Gecko/20100101 Firefox/140.0"),
    ("Tor Browser 14 (ESR 128)", "Mozilla/5.0 (Windows NT 10.0; rv:128.0) Gecko/20100101 Firefox/128.0"),
]

WEBVIEW_STATIC = [
    ("iOS WKWebView", "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"),
    ("Facebook in-app · Android", "Mozilla/5.0 (Linux; Android 13; SM-A536E Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.0.0 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/450.0.0.0.0;]"),
    ("Facebook in-app · iOS", "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 [FBAN/FBIOS;FBAV/450.0.0.0.0;FBBV/0;FBDV/iPhone16,2;FBMD/iPhone;FBSN/iOS;FBSV/18.6;FBSS/3;FBID/phone;FBLC/en_US;FBOP/5]"),
]

TV_CONSOLE = [
    ("Samsung Smart TV (Tizen 7)", "Mozilla/5.0 (SMART-TV; Linux; Tizen 7.0) AppleWebKit/537.36 (KHTML, like Gecko) 94.0.4606.31/7.0 TV Safari/537.36"),
    ("LG webOS TV", "Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.211 Safari/537.36 WebAppManager"),
    ("Android TV (contoh)", "Mozilla/5.0 (Linux; Android 12; SHIELD Android TV Build/SR1A.211012.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"),
    ("PlayStation 5", "Mozilla/5.0 (PlayStation; PlayStation 5/2.26) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15"),
    ("PlayStation 4", "Mozilla/5.0 (PlayStation 4 11.00) AppleWebKit/605.1.15 (KHTML, like Gecko)"),
    ("Xbox One", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; Xbox; Xbox One) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36 Edge/20.02"),
    ("Nintendo Switch", "Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/601.6 (KHTML, like Gecko) NF/4.0.0.5.10 NintendoBrowser/5.1.0.13343"),
]

BOTS = [
    ("Bing (klasik)", "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"),
    ("Googlebot (klasik)", "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"),
    ("DuckDuckBot", "DuckDuckBot/1.1; (+http://duckduckgo.com/duckduckbot.html)"),
    ("YandexBot", "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"),
    ("Baiduspider", "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"),
    ("Applebot", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15 (Applebot/0.1; +http://www.apple.com/go/applebot)"),
    ("Facebook link preview", "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)"),
    ("Twitterbot", "Twitterbot/1.0"),
    ("Slackbot", "Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)"),
    ("LinkedInBot", "LinkedInBot/1.0 (compatible; Mozilla/5.0; Apache-HttpClient +http://www.linkedin.com)"),
]

HTTP_TOOLS = [
    ("curl", "curl/8.9.1"),
    ("Wget", "Wget/1.24.5"),
    ("Python requests", "python-requests/2.32.3"),
    ("Python urllib", "Python-urllib/3.12"),
    ("Node.js fetch (undici)", "node"),
    ("Axios", "axios/1.7.7"),
    ("Go", "Go-http-client/2.0"),
    ("OkHttp (Android)", "okhttp/4.12.0"),
    ("Android Dalvik", "Dalvik/2.1.0 (Linux; U; Android 14; Pixel 8 Build/UD1A.231105.004)"),
    ("Apache HttpClient", "Apache-HttpClient/4.5.14 (Java/17.0.9)"),
    ("Postman", "PostmanRuntime/7.43.0"),
]

LEGACY_BROWSERS = [
    ("Internet Explorer 11", "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"),
    ("Internet Explorer 10", "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)"),
    ("Internet Explorer 9", "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"),
    ("Internet Explorer 8", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)"),
    ("Internet Explorer 7", "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"),
    ("Internet Explorer 6", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"),
    ("Edge Legacy 18", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"),
    ("Edge Legacy 12", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240"),
]


def static_items(rows):
    return [item(label, ua) for label, ua in rows]


STATIC_NOTE = "Data statis (diperbarui manual)."


def build():
    v = resolve_versions()
    c, f = v["chrome"], v["firefox"]
    categories = [
        cat("chrome_android", "Chrome Android", "#1A73E8",
            auto("Chrome", [("Android", CH_AND), ("Android Tablet", CH_TAB)], c)),
        cat("chrome_desktop", "Chrome Desktop", "#34A853",
            auto("Chrome", [("Windows", CH_WIN), ("macOS", CH_MAC), ("Linux", CH_LIN), ("ChromeOS", CH_CROS)], c),
            "Brave dan Vivaldi memakai UA yang sama dengan Chrome."),
        cat("firefox_android", "Firefox Android", "#FF7139", auto("Firefox", [("Android", FF_AND)], f)),
        cat("firefox_desktop", "Firefox Desktop", "#E66000",
            auto("Firefox", [("Windows", FF_WIN), ("macOS", FF_MAC), ("Linux", FF_LIN), ("Ubuntu", FF_UBU)], f)),
        cat("safari_ios", "Safari iOS", "#0A84FF", [sec("iPhone & iPad", static_items(SAFARI_IOS))], STATIC_NOTE),
        cat("safari_macos", "Safari macOS", "#5AC8FA", [sec("Mac", static_items(SAFARI_MAC))], STATIC_NOTE),
        cat("chrome_ios", "Chrome iOS", "#5E5CE6", auto("Chrome iOS", [("iPhone", CRIOS)], c)),
        cat("firefox_ios", "Firefox iOS", "#FF9500", auto("Firefox iOS", [("iPhone", FXIOS)], f)),
        cat("edge", "Edge", "#0F7B6C",
            auto("Edge", [("Windows", EDGE_WIN), ("Android", EDGE_AND), ("iPhone", EDGE_IOS)], c),
            "Nomor versi mengikuti Chrome."),
        cat("samsung", "Samsung Internet", "#1428A0", [sec("Android", static_items(SAMSUNG))], STATIC_NOTE),
        cat("opera", "Opera", "#D6001C",
            [sec("Desktop", static_items(OPERA)), sec("Android", static_items(OPERA_ANDROID))], STATIC_NOTE),
        cat("browser_lain", "Browser lain", "#8E8E93", [sec("UC, MIUI, Yandex, Tor", static_items(OTHER_BROWSERS))],
            "Pola tipikal; angka versi bisa berbeda. " + STATIC_NOTE),
        cat("webview", "WebView & in-app", "#30B0C7",
            auto("Android WebView", [("Android", WEBVIEW)], c)
            + [sec("iOS & aplikasi sosial", static_items(WEBVIEW_STATIC))],
            "Aplikasi sosial punya UA sendiri-sendiri; contoh ini hanya pola tipikal."),
        cat("tv_konsol", "TV & konsol", "#AF52DE", [sec("Perangkat", static_items(TV_CONSOLE))], STATIC_NOTE),
        cat("bot_crawler", "Bot & crawler", "#636366",
            [sec("Terbaru · Googlebot & Bing", [
                item(f"Googlebot Desktop (Chrome {c})", GOOGLEBOT_DESKTOP.format(v=c)),
                item(f"Googlebot Smartphone (Chrome {c})", GOOGLEBOT_MOBILE.format(v=c)),
                item(f"Bingbot (Chrome {c})", BINGBOT.format(v=c)),
            ]), sec("Bot lain", static_items(BOTS))],
            "Situs sering memblokir UA bot palsu. Pakai hanya untuk pengujian milik sendiri."),
        cat("alat_http", "Alat & HTTP client", "#64748B", [sec("Klien HTTP", static_items(HTTP_TOOLS))],
            "Angka versi hanya contoh. " + STATIC_NOTE),
        cat("browser_lawas", "Browser lawas", "#0078D4", [sec("IE & Edge lama", static_items(LEGACY_BROWSERS))],
            "Sudah tidak didukung; hanya untuk pengujian."),
        cat("android_lama", "Android lama (≤ 9)", "#3DDC84", [sec("Chrome Android", static_items(LEGACY_ANDROID))],
            "Contoh tipikal; build ID dan model bisa berbeda di tiap perangkat."),
    ]
    return {
        "meta": {
            "updated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "versions": v,
        },
        "categories": categories,
    }


if __name__ == "__main__":
    OUT.write_text(json.dumps(build(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("Selesai:", OUT)
