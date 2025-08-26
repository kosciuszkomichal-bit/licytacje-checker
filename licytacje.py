import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import hashlib

STATE_FILE = "state.txt"
LOG_FILE = "log.txt"
URL = "https://pruszkow.sr.gov.pl/obwieszczenia-o-licytacjach,m,mg,59"

def fetch_announcements():
    r = requests.get(URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # przykładowa selekcja obwieszczeń, dopasuj do struktury strony
    items = [li.get_text(strip=True) for li in soup.select(".listing li")]
    return items

def get_hash(items):
    joined = "\n".join(items)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()

def main():
    # utworzenie log.txt jeśli nie istnieje
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            f.write(f"[{datetime.now()}] [TEST] Skrypt działa!\n")

    announcements = fetch_announcements()
    current_hash = get_hash(announcements)

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            old_hash = f.read().strip()
    else:
        old_hash = ""
        # jeśli pierwszy raz, zapisujemy hash
        with open(STATE_FILE, "w") as f:
            f.write(current_hash)
        return  # zakończ pierwszy run, log już utworzony

    # jeśli hash się zmienił
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
