import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0"}
BARK_KEY = "2qRcV2zJa2NXGAH7MFmtSd"  # ⬅️ 请替换为你 Bark App 中显示的 key

def send_bark_notification(title, msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = f"https://api.day.app/{BARK_KEY}/{title}/{msg}\n{now}"
    requests.get(url)

def check_changi():
    url = "https://www.changiairport.com/en/corporate/our-media-hub/publications/reports.html"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("a[href$='.pdf']")
    return [(link.get_text(strip=True), "https://www.changiairport.com" + link["href"]) for link in links]

def check_ocbc():
    url = "https://www.ocbc.com/group/research/index"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("a[href$='.pdf']")
    return [(link.get_text(strip=True), "https://www.ocbc.com" + link["href"]) for link in links]

def check_mas():
    url = "https://www.mas.gov.sg/news/media-releases"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("div.card--article__text > a")
    return [(i.get_text(strip=True), "https://www.mas.gov.sg" + i["href"]) for i in items]

def check_dbs():
    url = "https://www.dbs.com.sg/corporate/aics/at-a-glance.page"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("div.aics-card .title a")
    return [(i.get_text(strip=True), "https://www.dbs.com.sg" + i["href"]) for i in items]

def check_uob():
    url = "https://www.uobgroup.com/research/todays-focus.page"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    items = soup.select("a[href$='.pdf']")
    return [(i.get_text(strip=True), "https://www.uobgroup.com" + i["href"]) for i in items]

def load_history():
    if os.path.exists("history.json"):
        with open("history.json", "r") as f:
            return json.load(f)
    return {}

def save_history(history):
    with open("history.json", "w") as f:
        json.dump(history, f)

def main():
    history = load_history()
    updated = False
    keywords = ["Annual", "Financial", "Sustainability", "Report", "Outlook", "Weekly"]

    for site, func in [
        ("changi", check_changi),
        ("ocbc", check_ocbc),
        ("mas", check_mas),
        ("dbs", check_dbs),
        ("uob", check_uob)
    ]:
        if site not in history:
            history[site] = []
        for title, link in func():
            if link not in history[site]:
                if not any(k.lower() in title.lower() for k in keywords):
                    continue
                send_bark_notification(f"{site.upper()} 有新内容", f"{title}\n{link}")
                history[site].append(link)
                updated = True
    if updated:
        save_history(history)

if __name__ == "__main__":
    main()
