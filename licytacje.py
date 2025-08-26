import requests
from bs4 import BeautifulSoup
import hashlib
import os
from datetime import datetime

URL = "https://pruszkow.sr.gov.pl/obwieszczenia-o-licytacjach,m,mg,59"
STATE_FILE = "last_state.txt"
LOG_FILE = "log.txt"

def fetch_announcements():
    r = requests.get(URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # wszystkie linki w sekcji obwieszczeń
    items = soup.select("div.article-list a")
    announcements = [a.get_text(strip=True) + " | " + a["href"] for a in items if a.get("href")]
    return announcements

def get_hash(data):
    return hashlib.sha256("\n".join(data).encode("utf-8")).hexdigest()

def main():
    # Testowy zapis – żeby sprawdzić, czy workflow w ogóle działa
    with open("log.txt", "a") as f:
        f.write("[TEST] Skrypt działa!\n")

    announcements = fetch_announcements()
    current_hash = get_hash(announcements)

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""

    if current_hash != old_hash:
        with open(LOG_FILE, "a") as log:
            log.write(f"[{datetime.now()}] Nowe obwieszczenia!\n")
            for a in announcements:
                log.write(f"- {a}\n")
        with open(STATE_FILE, "w") as f:
            f.write(current_hash)
    else:
        with open(LOG_FILE, "a") as log:
            log.write(f"[{datetime.now()}] Brak zmian.\n")

if __name__ == "__main__":
    main()
    
print("[TEST] Skrypt działa!")
