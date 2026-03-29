import requests
import os
from datetime import datetime


TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
GROQ_API_KEY = os.environ['GROQ_API_KEY']


def get_google_trends():
    try:
        url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=AT"
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return response.text[:3000]
    except Exception as e:
        return f"Google Trends nicht verfuegbar: {e}"


def get_music_charts():
    try:
        url = "https://itunes.apple.com/at/rss/topsongs/limit=20/json"
        response = requests.get(url, timeout=10)
        data = response.json()
        entries = data.get('feed', {}).get('entry', [])
        charts = []
        for i, entry in enumerate(entries[:10], 1):
            name = entry.get('im:name', {}).get('label', 'Unknown')
            artist = entry.get('im:artist', {}).get('label', 'Unknown')
            charts.append(f"{i}. {name} - {artist}")
        return "\n".join(charts)
    except Exception as e:
        return f"Charts nicht verfuegbar: {e}"


def analyze_with_groq(trends, charts):
    today = datetime.now().strftime("%d.%m.%Y")

    prompt = f"""KONTEXT: Du schreibst fuer Denis, Independent-Musiker. Er will seinen Sound auf TikTok viral bringen - Leute sollen ihn als Audio nutzen und dann auf Spotify streamen.

AKTUELLE DATEN - {today}:
Google Trends AT/DE: {trends[:2000]}
Charts AT Top 10: {charts}

ABSOLUTE VERBOTE - wenn du das schreibst, hast du versagt:
- "Nutze aktuelle Trends" (welche konkret?)
- "Erstelle ansprechende Inhalte" (was genau?)
- "Sei authentisch" (bedeutungslos)
- "Verwende relevante Hashtags" (welche?)
- Irgendwas mit "koennte" oder "vielleicht"

DEIN JOB: 3 fertige Video-Konzepte liefern. Jedes Konzept so beschrieben dass Denis es HEUTE filmen kann ohne nachzudenken.

Fuer jedes Video GENAU dieses Format:

VIDEO [Nummer]: [einpraegsamr Titel]
Situation: [exakt was passiert im Video - eine Szene, ein Ort, eine Handlung]
Hook (0-2 Sek): [exakter Text-Overlay oder gesprochener Satz - woertlich]
Mitte: [was passiert, was sieht man, was steht im Text]
Warum der Sound hier viral geht: [ein Satz - psychologischer Grund]
Caption: [fertige Caption zum Copy-Pasten inkl. Call-to-Action]

---

Dann noch:

🔥 TREND HEUTE: Nimm den groessten Trend aus den Google Trends oben. Erklaere in 2 Saetzen wie Denis diesen SPEZIFISCHEN Trend mit seiner Musik verbindet. Nicht allgemein - den konkreten Trend beim Namen nennen.

#️⃣ HASHTAGS: 5 kleine (#unter500k) + 3 grosse. Nur die Liste, keine Erklaerung.

Antworte auf Deutsch. Keine Markdown. Maximal 3500 Zeichen."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein TikTok Creator der selbst Musik viral gebracht hat. Du weisst: vage Tipps sind wertlos. Du lieferst nur konkrete, filmbare Video-Konzepte mit exaktem Wortlaut. Wenn du in Versuchung kommst etwas Allgemeines zu schreiben - schreib stattdessen ein konkretes Beispiel."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.8
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    result = response.json()
    return result['choices'][0]['message']['content']


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    if len(message) > 4000:
        message = message[:4000] + "..."
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload, timeout=30)
    return response.json()


def main():
    print("Starte TikTok Trend Bot...")

    print("Hole Google Trends...")
    trends = get_google_trends()

    print("Hole Music Charts...")
    charts = get_music_charts()

    print("Analysiere mit Groq AI...")
    analysis = analyze_with_groq(trends, charts)

    today = datetime.now().strftime("%d.%m.%Y")
    message = f"🎵 TikTok Marktanalyse {today}\n\n{analysis}"

    print("Sende an Telegram...")
    result = send_telegram(message)

    if result.get('ok'):
        print("Erfolgreich gesendet!")
    else:
        print(f"Fehler: {result}")


if __name__ == "__main__":
    main()
