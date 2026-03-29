import requests
import os
from datetime import datetime

TELEGRAM_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
GROQ_API_KEY = os.environ['GROQ_API_KEY']


def get_ki_ideas():
    today = datetime.now().strftime("%d.%m.%Y")
    weekday = datetime.now().strftime("%A")

    prompt = f"""Du bist KI-Stratege fuer Denis, einen Independent-Musiker der seine Musik viral bringen will.

Denis veroeffentlicht Musik auf allen Streamingplattformen (Spotify, Apple Music etc.) und will auf TikTok viral gehen.
Ziel: Leute sollen seinen Sound benutzen + den Song streamen.
Er arbeitet mit: Claude Code, VS Code, GitHub Actions, Telegram Bots, n8n, Groq AI.
Heute: {weekday}, {today}

Erstelle seinen taeglichen KI-Arbeitsplan:

🤖 BOT-IDEE DES TAGES
Eine konkrete Bot/Automatisierungs-Idee die Denis diese Woche bauen sollte.
Beschreibe exakt: Was tut der Bot? Welches Tool (GitHub Actions / n8n / Claude)? Welches Problem loest er?
Beispiel-Level: "Ein Bot der jeden Freitag automatisch 5 TikTok Captions fuer deinen neuen Release generiert und dir per Telegram schickt"

✍️ PROMPT DES TAGES
Ein konkreter Prompt den Denis HEUTE in Claude oder ChatGPT eingeben soll.
Schreib den kompletten Prompt - copy-paste fertig.
Zweck: TikTok Content, Song-Konzepte, Marketing-Texte oder Strategie

🎵 CONTENT-AUTOMATISIERUNG
Welchen Teil seines TikTok/Musik-Workflows kann Denis mit KI automatisieren?
Konkrete Schritte wie er das umsetzt (welches Tool, wie einrichten)

🧠 KI-WORKFLOW DIESER WOCHE
Ein groesseres Automatisierungs-Projekt das Denis in 3-5 Tagen umsetzen kann.
Schritt-fuer-Schritt Anleitung. Welche Tools? Was ist das Endergebnis?

💡 UNGEWOEHNLICHE KI-IDEE
Eine kreative, unkonventionelle Art wie Denis KI nutzen koennte die die meisten Musiker noch nicht machen.
Konkret und umsetzbar - nicht Science Fiction.

Antworte auf Deutsch. Keine Markdown Formatierung, nur Emojis als Struktur. Maximal 3000 Zeichen."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "Du bist ein KI-Stratege und Automatisierungs-Experte fuer Kreative und Musiker. Du kennst Claude Code, GitHub Actions, n8n, Telegram Bots und weisst genau wie ein Solo-Musiker KI als persoenliches Team nutzen kann. Deine Ideen sind konkret, sofort umsetzbar und speziell auf Musik-Marketing auf TikTok ausgerichtet."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.9
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
    print("Starte KI-Mitarbeiter Bot...")

    print("Generiere KI-Ideen...")
    ideas = get_ki_ideas()

    today = datetime.now().strftime("%d.%m.%Y")
    message = f"🧠 Dein KI-Arbeitsplan {today}\n\n{ideas}"

    print("Sende an Telegram...")
    result = send_telegram(message)

    if result.get('ok'):
        print("Erfolgreich gesendet!")
    else:
        print(f"Fehler: {result}")


if __name__ == "__main__":
    main()
