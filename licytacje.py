import requests
from bs4 import BeautifulSoup
import hashlib
import os
from datetime import datetime

# --- Konfiguracja źródeł do sprawdzania ---
URLS = {
    "pruszkow sad": [
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

# --- Pobieranie treści strony ---
def fetch_content(urls):
    content = ""
    for url in urls:
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            content += soup.get_text(" ", strip=True) + "\n"
        except Exception as e:
            content += f"[BŁĄD przy pobieraniu {url}: {e}]\n"
    return content

# --- Tworzenie hash ---
def get_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# --- Główna logika ---
def main():
    with open(LOG_FILE, "w", encoding="utf-8") as log:  # zawsze nadpisuje log.txt
        for court, urls in URLS.items():
            content = fetch_content(urls)
            current_hash = get_hash(content)

            state_file = f"state_{court}.txt"

            if os.path.exists(state_file):
                with open(state_file, "r") as f:
                    old_hash = f.read().strip()
            else:
                old_hash = ""

            if current_hash != old_hash:
                log.write(f"{court}: ZMIANA\n")
                with open(state_file, "w") as f:
                    f.write(current_hash)
            else:
                log.write(f"{court}: brak zmian\n")

if __name__ == "__main__":
    main()
