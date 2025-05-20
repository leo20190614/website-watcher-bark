import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

HEADERS = {"User-Agent": "Mozilla/5.0"}
BARK_KEY = "2qRcV2zJa2NXGAH7MFmtSd"
IFTTT_KEY = "b15svmb9LKl10Yk-zC9AVx"


def send_notifications(source, title, link, timestamp):
    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    # 构造消息正文（详细内容）
    msg = f"\n📍 来源：{source}\n📝 标题：{title}\n🔗 链接：{link}\n🕒 抓取时间：{formatted_time}"

    # Bark 推送
    bark_url = f"https://api.day.app/{BARK_KEY}/{source} 有更新{msg}"
    try:
        requests.get(bark_url)
        print(f"✅ Bark 推送成功：{title}")
    except Exception as e:
        print(f"❌ Bark 推送失败：{e}")

    # IFTTT 推送
    ifttt_url = f"https://maker.ifttt.com/trigger/website_update/json/with/key/{IFTTT_KEY}"
    payload = {
        "value1": f"[{source}] {title}",
        "value2": link,
        "value3": formatted_time
    }
    try:
        requests.post(ifttt_url, json=payload)
        print(f"✅ IFTTT 推送成功：{title}")
    except Exception as e:
        print(f"❌ IFTTT 推送失败：{e}")


def check_ocbc():
    url = "https://www.ocbc.com/group/research/index"
    res = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")
    links = soup.select("a[href$='.pdf']")
    return [("OCBC", link.get_text(strip=True), "https://www.ocbc.com" + link["href"]) for link in links]

# 你可以添加更多 check_xxx() 方法来支持更多来源

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

    for site_func in [check_ocbc]:
        items = site_func()
        for source, title, link in items:
            if source not in history:
                history[source] = []
            if link not in history[source]:
                send_notifications(source, title, link, datetime.now())
                history[source].append(link)
                updated = True

    if updated:
        save_history(history)

if __name__ == "__main__":
    main()
