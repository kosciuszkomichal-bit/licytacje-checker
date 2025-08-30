import requests
from bs4 import BeautifulSoup
import hashlib
import os
from datetime import datetime

# --- Konfiguracja źródeł do sprawdzania ---
URLS = {
    "pruszkow": [
        "https://pruszkow.sr.gov.pl/obwieszczenia-o-licytacjach,m,mg,59"
    ],
    "warszawa": [
        f"https://www.mazowieckie.kas.gov.pl/izba-administracji-skarbowej-w-warszawie/ogloszenia/obwieszczenia-o-licytacjach{i}" for i in range(1, 13)
    ],
    "grodziskmazowiecki": [
        "https://www.mazowieckie.kas.gov.pl/urzad-skarbowy-w-grodzisku-mazowieckim/ogloszenia/obwieszczenia-o-licytacji"
    ],
    "pruszkow": [
        "https://www.mazowieckie.kas.gov.pl/urzad-skarbowy-w-pruszkowie/ogloszenia/obwieszczenia-o-licytacji"
    ]
}

LOG_FILE = "log.txt"

# --- Pobieranie ogłoszeń z listy URL ---
def fetch_announcements(urls):
    announcements = []
    for url in urls:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            
            # 🔹 tu trzeba dostosować selektor pod stronę (np. <a>, <li>, <div>)
            for item in soup.find_all("a"):
                text = item.get_text(strip=True)
                if text:
                    announcements.append(text)
        except Exception as e:
            announcements.append(f"[BŁĄD przy pobieraniu {url}: {e}]")
    return announcements

# --- Hash listy ogłoszeń ---
def get_hash(announcements):
    content = "\n".join(announcements)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

# --- Główna logika ---
def main():
    for court, urls in URLS.items():
        announcements = fetch_announcements(urls)
        current_hash = get_hash(announcements)

        state_file = f"state_{court}.txt"

        if os.path.exists(state_file):
            with open(state_file, "r") as f:
                old_hash = f.read().strip()
        else:
            old_hash = ""

        if current_hash != old_hash:
            with open(LOG_FILE, "a") as log:
                log.write(f"[{datetime.now()}] Nowe obwieszczenia ({court})!\n")
                for a in announcements:
                    log.write(f"- {a}\n")
                log.write("\n")
            with open(state_file, "w") as f:
                f.write(current_hash)
        else:
            with open(LOG_FILE, "a") as log:
                log.write(f"[{datetime.now()}] Brak zmian ({court}).\n")

if __name__ == "__main__":
    main()
