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

    prompt = f"""Du analysierst Daten fuer einen Independent-Musiker (Denis) der seine Musik auf allen Streamingplattformen veroeffentlicht und auf TikTok viral gehen will. Ziel: Leute sollen seinen Sound als TikTok-Audio benutzen UND den Song privat streamen. Seine Musik transportiert verschiedene Emotionen - von humorvoll bis tiefgründig.

GOOGLE TRENDS (AT/DE) - {today}:
{trends[:2000]}

MUSIC CHARTS AT Top 10:
{charts}

Erstelle einen knallharten Tagesbericht. Sei extrem konkret - keine vagen Tipps, sondern exakte Video-Konzepte die ich heute umsetzen kann:

🎯 SOUND-NUTZUNG PUSHEN
Welche konkreten Video-Formate bringen Leute dazu meinen Sound zu benutzen?
Nenne 3 spezifische Video-Konzepte (z.B. "POV: du bist der einzige auf der Party der guten Geschmack hat" + welche Emotion/Situation + warum das viral geht)

🔥 TREND-HIJACKING HEUTE
Welche aktuellen TikTok-Trends aus den Google Trends kann ich mit meiner Musik verbinden?
Fuer jeden Trend: exakter Video-Aufbau (Sekunde 0-3 Hook, Mitte, Ende), welches Gefuehl soll der Zuschauer haben

😂 HUMOR-KONZEPTE
2-3 konkrete humorvolle Video-Ideen bei denen mein Sound der Witz ist
Beschreibe exakt: Situation, Text-Overlay, Reaktion des Publikums

💔 EMOTIONALE HOOKS
2 Video-Konzepte fuer ernstere/emotionale Songs
Welche universelle menschliche Erfahrung wird getriggert? Wie baue ich den Hook in den ersten 2 Sekunden?

📈 STREAMING KONVERSION
Wie bringe ich TikTok-Zuschauer dazu den Song auch auf Spotify/Apple Music zu streamen?
Konkrete Call-to-Action Formulierungen fuer die Caption

#️⃣ HASHTAG-STRATEGIE
10 Nischen-Hashtags (unter 500k Views - bessere Chancen zu tenden) + 5 grosse Hashtags
Format: #hashtag (Begruendung warum heute relevant)

⚡ EINE SACHE DIE HEUTE VIRAL GEHEN KANN
Das konkreteste, am leichtesten umsetzbare Video-Konzept fuer heute - mit exaktem Skript

Antworte auf Deutsch. Keine Markdown Formatierung, nur Emojis als Struktur. Maximal 3500 Zeichen."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein TikTok Virality Experte spezialisiert auf Musik-Marketing fuer Independent Artists. Du kennst genau wie Sound-Trends entstehen, warum Leute einen fremden Song benutzen, und wie man aus TikTok-Views Streams auf Spotify macht. Du denkst wie ein 22-jaehriger Creator der weiss was gerade funktioniert - nicht wie ein Marketing-Lehrbuch. Deine Ideen sind spezifisch, mutig und sofort umsetzbar."
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
