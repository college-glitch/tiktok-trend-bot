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

    prompt = f"""Analysiere folgende aktuelle Daten und erstelle eine TikTok Virality Strategie fuer einen Musiker der tanzbare Musik macht:

GOOGLE TRENDS (AT/DE):
{trends[:2000]}

MUSIC CHARTS (AT Top 10):
{charts}

Datum: {today}

Erstelle einen strukturierten Tagesbericht:

🔥 TOP 5 TIKTOK TRENDS HEUTE
(konkrete aktuelle Trends die ich heute nutzen kann)

💃 AI-INFLUENCER TANZ IDEEN
(konkrete Choreographie-Konzepte - was fuer Moves, welcher Stil, wie geht der Trend viral?)

😂 MEME KONZEPTE
(konkrete Meme-Ideen mit Beschreibung die viral gehen koennen)

#️⃣ BESTE HASHTAGS FUER HEUTE
(15-20 relevante Hashtags)

⚡ TOP 3 SOFORTMASSNAHMEN
(was ich HEUTE noch umsetzen soll fuer maximale Reichweite)

Sei sehr konkret und kreativ. Keine Markdown Formatierung, nur Emojis. Antworte auf Deutsch. Maximal 3000 Zeichen."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein Elite TikTok Marketing Stratege spezialisiert auf Musikvirality, AI Influencer Kampagnen und Meme Marketing. Gib immer konkrete, direkt umsetzbare Ideen - keine allgemeinen Tipps."
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
