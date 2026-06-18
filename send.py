import feedparser, requests, json, time, os

RSS_URL = "https://rss-bridge.org/bridge01/?action=display&bridge=Instagram&context=Username&u=sargentomellocasal&format=Atom"
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
STATE_FILE = "sent.json"

sent = set(json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else [])

feed = feedparser.parse(RSS_URL)
novos = [e for e in feed.entries if e.id not in sent][:5]  # segurança: máx 5

for entry in novos:
    titulo = entry.get("title", "").strip()
    link = entry.get("link", "")
    caption = f"{titulo[:900]}\n\nFonte: @sargentomellocasal\n{link}"
    
    photo_url = None
    if hasattr(entry, 'media_content') and entry.media_content:
        photo_url = entry.media_content[0].get('url')
    
    try:
        if photo_url:
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={"chat_id": CHAT_ID, "photo": photo_url, "caption": caption},
                timeout=15
            )
        else:
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": caption},
                timeout=15
            )
        # se Telegram pedir para esperar (flood), respeita
        if r.status_code == 429:
            retry = r.json().get("parameters", {}).get("retry_after", 5)
            time.sleep(retry + 1)
            continue
    except Exception:
        pass
    
    sent.add(entry.id)
    time.sleep(3)  # pausa anti-ban

# guarda últimos 100
json.dump(list(sent)[-100:], open(STATE_FILE, "w"))
