#!/usr/bin/env python3
import socket
import time
import requests
import uuid
import os

NICKSERV_PASS = os.environ["NICKSERV_PASS"]
# ================= IRC-KONFIG =================
SERVER = "atw.hu.eu.dal.net"
PORT = 6667

PRIMARY_NICK = "nick"
ALT_NICKS = ["nick_"]
REALNAME = "Azure Bot"

CHANNEL_IN = "#channel"
CHANNEL_OUT = "#channel_en"

RECONNECT_DELAY = 10
NICK_RETRY_INTERVAL = 60
PING_TIMEOUT = 600        # Sekunder utan PONG-svar innan vi anser anslutningen död
PING_INTERVAL = 90        # Hur ofta vi skickar PING till servern
SOCKET_TIMEOUT = 120      # Socket recv-timeout i sekunder
# ============================================

# ================= AZURE =====================
AZURE_KEY = os.environ["AZURE_TRANSLATOR_KEY"]
AZURE_REGION = os.environ["AZURE_TRANSLATOR_REGION"]
AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com/translate"
# ============================================

current_nick = None
last_nick_retry = 0

# ------ Språkheuristik ------
def looks_english(text):
    if any(c in text.lower() for c in "åäö"):
        return False
    english_markers = [" the ", " and ", " you ", " is ", " are ", " i "]
    t = f" {text.lower()} "
    return any(w in t for w in english_markers)

# ------ Azure-översättning ------
def translate_sv_to_en(text):
    params = {"api-version": "3.0", "from": "sv", "to": "en"}
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_KEY,
        "Ocp-Apim-Subscription-Region": AZURE_REGION,
        "Content-Type": "application/json",
        "X-ClientTraceId": str(uuid.uuid4())
    }
    body = [{"text": text}]
    try:
        r = requests.post(AZURE_ENDPOINT, headers=headers, params=params, json=body, timeout=10)
        r.raise_for_status()
        return r.json()[0]["translations"][0]["text"]
    except Exception as e:
        print("Translate error:", e)
        return None

# ------ Säker send ------
def safe_send(sock, msg):
    """Skickar data på socketen. Kastar ConnectionError vid alla OS-fel,
    vilket triggar återanslutning i run_bot()."""
    try:
        sock.send(msg.encode())
    except (OSError, BrokenPipeError, ConnectionResetError) as e:
        raise ConnectionError(f"Send failed: {e}")

# ------ IRC-anslutning ------
def connect_irc():
    global current_nick

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(SOCKET_TIMEOUT)  # Viktigt: förhindrar evig blockering
    sock.connect((SERVER, PORT))

    current_nick = None  # Återställ nick vid varje ny anslutning
    safe_send(sock, f"NICK {PRIMARY_NICK}\r\n")
    safe_send(sock, f"USER {PRIMARY_NICK} 0 * :{REALNAME}\r\n")

    nick_index = 0
    buffer = ""

    while True:
        data = sock.recv(4096).decode("utf-8", errors="ignore")
        buffer += data
        lines = buffer.split("\r\n")
        buffer = lines.pop()

        for line in lines:
            print("DEBUG:", line)

            if line.startswith("PING"):
                safe_send(sock, f"PONG {line.split()[1]}\r\n")

            if " 433 " in line:
                if nick_index < len(ALT_NICKS):
                    current_nick = ALT_NICKS[nick_index]
                    nick_index += 1
                    print("Nick in use, trying:", current_nick)
                    safe_send(sock, f"NICK {current_nick}\r\n")
                else:
                    raise RuntimeError("No available nicknames")

            if " 001 " in line:
                if not current_nick:
                    current_nick = PRIMARY_NICK
                safe_send(sock, f"PRIVMSG NickServ@services.dal.net :IDENTIFY {NICKSERV_PASS}\r\n")
                time.sleep(2)  # Give NickServ time to process before joining
                safe_send(sock, f"JOIN {CHANNEL_IN}\r\n")
                safe_send(sock, f"JOIN {CHANNEL_OUT}\r\n")
                print(f"Connected as {current_nick}")
                return sock

# ------ Försök återta primärt nick ------
def try_reclaim_primary(sock):
    global last_nick_retry, current_nick
    if current_nick == PRIMARY_NICK:
        return
    if time.time() - last_nick_retry >= NICK_RETRY_INTERVAL:
        print("Trying to reclaim primary nick")
        safe_send(sock, f"NICK {PRIMARY_NICK}\r\n")
        last_nick_retry = time.time()

# ------ Huvudloop ------
def run_bot():
    global current_nick
    while True:
        try:
            sock = connect_irc()
            buffer = ""
            last_pong = time.time()    # Tidsstämpel för senaste PONG (eller start)
            last_ping_sent = 0         # Tvinga PING direkt vid uppstart

            while True:
                now = time.time()

                # Skicka PING till servern med jämna mellanrum
                if now - last_ping_sent >= PING_INTERVAL:
                    safe_send(sock, f"PING :{SERVER}\r\n")
                    last_ping_sent = now

                # Timeout triggas BARA om vi skickat PING och inte fått PONG tillbaka
                if last_ping_sent > last_pong and now - last_ping_sent >= PING_TIMEOUT:
                    raise ConnectionError(f"Ping timeout ({PING_TIMEOUT}s utan PONG-svar)")

                try:
                    data = sock.recv(4096).decode("utf-8", errors="ignore")
                except socket.timeout:
                    # Ingen data inom SOCKET_TIMEOUT – loopa och kontrollera ping timeout
                    continue
                except (OSError, ConnectionResetError) as e:
                    # "Connection reset by peer" och liknande OS-fel vid recv
                    raise ConnectionError(f"Recv failed: {e}")

                if not data:
                    raise ConnectionError("Disconnected (tom data)")

                buffer += data
                lines = buffer.split("\r\n")
                buffer = lines.pop()

                for line in lines:
                    print("DEBUG:", line)

                    if line.startswith("PING"):
                        safe_send(sock, f"PONG {line.split()[1]}\r\n")
                        continue

                    # Serverns PONG-svar på vår PING
                    if line.startswith("PONG") or " PONG " in line:
                        last_pong = time.time()  # Återställ timeout-räknaren
                        continue

                    try_reclaim_primary(sock)

                    # Hantera nick-byte bekräftelse (436 = nick collision)
                    if " 436 " in line or " 433 " in line:
                        if current_nick != PRIMARY_NICK:
                            pass  # Redan på alt-nick, gör inget
                        else:
                            current_nick = ALT_NICKS[0]
                            safe_send(sock, f"NICK {current_nick}\r\n")

                    if "PRIVMSG" in line:
                        parts = line.split(" ", 3)
                        if len(parts) < 4:
                            continue
                        sender = parts[0].split("!")[0][1:]
                        channel = parts[2]
                        message = parts[3][1:]

                        if sender.lower() == current_nick.lower():
                            continue

                        if channel.lower() == CHANNEL_IN.lower():
                            # Engelska → skicka direkt
                            if looks_english(message):
                                out = f"{sender}: {message}"
                                safe_send(sock, f"PRIVMSG {CHANNEL_OUT} :{out}\r\n")
                                continue
                            # Svenska → översätt
                            translated = translate_sv_to_en(message)
                            if translated:
                                out = f"{sender}: {translated}"
                                safe_send(sock, f"PRIVMSG {CHANNEL_OUT} :{out}\r\n")

        except Exception as e:
            print(f"IRC error: {e} – återansluter om {RECONNECT_DELAY}s...")
            current_nick = None  # Återställ nick-state inför nästa försök
            try:
                sock.close()
            except Exception:
                pass
            time.sleep(RECONNECT_DELAY)

# ------ Start ------
if __name__ == "__main__":
    print(f"Starting IRC bot with Azure translation (Region: {AZURE_REGION})")
    run_bot()
