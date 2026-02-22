{\rtf1\ansi\ansicpg1252\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 DejaVuSansMono-Bold;\f1\fnil\fcharset0 DejaVuSansMono;}
{\colortbl;\red255\green255\blue255;\red252\green50\blue32;\red0\green0\blue0;\red50\green244\blue241;
\red55\green239\blue32;\red251\green30\blue255;\red97\green34\blue255;\red161\green210\blue7;}
{\*\expandedcolortbl;;\cssrgb\c100000\c29539\c16203;\csgray\c0;\cssrgb\c19572\c95778\c95688;
\cssrgb\c22319\c93015\c16433;\cssrgb\c100000\c29675\c100000;\cssrgb\c46228\c27437\c100000;\cspthree\c71744\c83854\c26362;}
\paperw11900\paperh16840\margl1440\margr1440\vieww19760\viewh24820\viewkind0
\pard\tx560\tx1120\tx1680\tx2240\tx2800\tx3360\tx3920\tx4480\tx5040\tx5600\tx6160\tx6720\pardirnatural\partightenfactor0

\f0\b\fs28 \cf2 \CocoaLigature0 #!/usr/bin/env python3
\f1\b0 \cf3 \

\f0\b \cf4 import
\f1\b0 \cf3  socket\

\f0\b \cf4 import
\f1\b0 \cf3  time\

\f0\b \cf4 import
\f1\b0 \cf3  requests\

\f0\b \cf4 import
\f1\b0 \cf3  uuid\

\f0\b \cf4 import
\f1\b0 \cf3  os\
\

\f0\b \cf2 # ================= IRC-KONFIG =================
\f1\b0 \cf3 \
SERVER = 
\f0\b \cf5 "irc.server.net"
\f1\b0 \cf3       
\f0\b \cf2  # change to desired IRC server
\f1\b0 \cf3 \
PORT = 6667\
\
PRIMARY_NICK = 
\f0\b \cf5 \'94nick\'94
\f1\b0 \cf3 \
ALT_NICKS = [
\f0\b \cf5 \'94nick_\'94
\f1\b0 \cf3 ]\
REALNAME = 
\f0\b \cf5 \'94Owner Azure Bot"
\f1\b0 \cf3 \
\
CHANNEL_IN = 
\f0\b \cf5 \'94#channel\'94
\f1\b0 \cf3 \
CHANNEL_OUT = 
\f0\b \cf5 \'94#channel_en"
\f1\b0 \cf3 \
\
RECONNECT_DELAY = 10\
NICK_RETRY_INTERVAL = 60\

\f0\b \cf2 # ============================================
\f1\b0 \cf3 \
\

\f0\b \cf2 # ================= AZURE =====================
\f1\b0 \cf3 \

\f0\b \cf2 # Put you key and location here
\f1\b0 \cf3 \
AZURE_KEY = 
\f0\b \cf5 \'94ALongAPIKey\'94
\f1\b0 \cf3 \
AZURE_REGION = 
\f0\b \cf5 \'94location\'94
\f1\b0 \cf3 \
AZURE_ENDPOINT = 
\f0\b \cf5 "https://api.cognitive.microsofttranslator.com/translate"
\f1\b0 \cf3 \

\f0\b \cf2 # ============================================
\f1\b0 \cf3 \
\
current_nick = 
\f0\b \cf6 None
\f1\b0 \cf3 \
last_nick_retry = 0\
\

\f0\b \cf2 # -------- Spr\'e5kheuristik --------
\f1\b0 \cf3 \

\f0\b \cf4 def\cf7  looks_english
\f1\b0 \cf3 (text):\
    
\f0\b \cf4 if
\f1\b0 \cf3  any(c 
\f0\b \cf4 in
\f1\b0 \cf3  text.lower() 
\f0\b \cf4 for
\f1\b0 \cf3  c 
\f0\b \cf4 in
\f1\b0 \cf3  
\f0\b \cf5 "\'e5\'e4\'f6"
\f1\b0 \cf3 ):\
        
\f0\b \cf4 return
\f1\b0 \cf3  
\f0\b \cf6 False
\f1\b0 \cf3 \
    english_markers = [
\f0\b \cf5 " the "
\f1\b0 \cf3 , 
\f0\b \cf5 " and "
\f1\b0 \cf3 , 
\f0\b \cf5 " you "
\f1\b0 \cf3 , 
\f0\b \cf5 " is "
\f1\b0 \cf3 , 
\f0\b \cf5 " are "
\f1\b0 \cf3 , 
\f0\b \cf5 " i "
\f1\b0 \cf3 ]\
    t = f
\f0\b \cf5 " \{text.lower()\} "
\f1\b0 \cf3 \
    
\f0\b \cf4 return
\f1\b0 \cf3  any(w 
\f0\b \cf4 in
\f1\b0 \cf3  t 
\f0\b \cf4 for
\f1\b0 \cf3  w 
\f0\b \cf4 in
\f1\b0 \cf3  english_markers)\
\

\f0\b \cf2 # -------- Azure-\'f6vers\'e4ttning --------
\f1\b0 \cf3 \

\f0\b \cf4 def\cf7  translate_sv_to_en
\f1\b0 \cf3 (text):\
    params = \{
\f0\b \cf5 "api-version"
\f1\b0 \cf3 : 
\f0\b \cf5 "3.0"
\f1\b0 \cf3 , 
\f0\b \cf5 "from"
\f1\b0 \cf3 : 
\f0\b \cf5 "sv"
\f1\b0 \cf3 , 
\f0\b \cf5 "to"
\f1\b0 \cf3 : 
\f0\b \cf5 "en"
\f1\b0 \cf3 \}\
    headers = \{\
        
\f0\b \cf5 "Ocp-Apim-Subscription-Key"
\f1\b0 \cf3 : AZURE_KEY,\
        
\f0\b \cf5 "Ocp-Apim-Subscription-Region"
\f1\b0 \cf3 : AZURE_REGION,\
        
\f0\b \cf5 "Content-Type"
\f1\b0 \cf3 : 
\f0\b \cf5 "application/json"
\f1\b0 \cf3 ,\
        
\f0\b \cf5 "X-ClientTraceId"
\f1\b0 \cf3 : str(uuid.uuid4())\
    \}\
    body = [\{
\f0\b \cf5 "text"
\f1\b0 \cf3 : text\}]\
    
\f0\b \cf4 try
\f1\b0 \cf3 :\
        r = requests.post(AZURE_ENDPOINT, headers=headers, params=params, json=body, timeout=10)\
        r.raise_for_status()\
        
\f0\b \cf4 return
\f1\b0 \cf3  r.json()[0][
\f0\b \cf5 "translations"
\f1\b0 \cf3 ][0][
\f0\b \cf5 "text"
\f1\b0 \cf3 ]\
    
\f0\b \cf4 except
\f1\b0 \cf3  Exception 
\f0\b \cf4 as
\f1\b0 \cf3  e:\
        print(
\f0\b \cf5 "Translate error:"
\f1\b0 \cf3 , e)\
        
\f0\b \cf4 return
\f1\b0 \cf3  
\f0\b \cf6 None
\f1\b0 \cf3 \
\

\f0\b \cf2 # -------- IRC-anslutning --------
\f1\b0 \cf3 \

\f0\b \cf4 def\cf7  connect_irc
\f1\b0 \cf3 ():\
    
\f0\b \cf4 global
\f1\b0 \cf3  current_nick\
\
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\
    sock.connect((SERVER, PORT))\
\
    sock.send(f
\f0\b \cf5 "NICK \{PRIMARY_NICK\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
    sock.send(f
\f0\b \cf5 "USER \{PRIMARY_NICK\} 0 * :\{REALNAME\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
\
    nick_index = 0\
    buffer = 
\f0\b \cf5 ""
\f1\b0 \cf3 \
\
    
\f0\b \cf4 while
\f1\b0 \cf3  
\f0\b \cf6 True
\f1\b0 \cf3 :\
        data = sock.recv(4096).decode(
\f0\b \cf5 "utf-8"
\f1\b0 \cf3 , errors=
\f0\b \cf5 "ignore"
\f1\b0 \cf3 )\
        buffer += data\
        lines = buffer.split(
\f0\b \cf5 "
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 )\
        buffer = lines.pop()\
\
        
\f0\b \cf4 for
\f1\b0 \cf3  line 
\f0\b \cf4 in
\f1\b0 \cf3  lines:\
            print(
\f0\b \cf5 "DEBUG:"
\f1\b0 \cf3 , line)\
\
            
\f0\b \cf4 if
\f1\b0 \cf3  line.startswith(
\f0\b \cf5 "PING"
\f1\b0 \cf3 ):\
                sock.send(f
\f0\b \cf5 "PONG \{line.split()[1]\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
\
            
\f0\b \cf4 if
\f1\b0 \cf3  
\f0\b \cf5 " 433 "
\f1\b0 \cf3  
\f0\b \cf4 in
\f1\b0 \cf3  line:\
                
\f0\b \cf4 if
\f1\b0 \cf3  nick_index < len(ALT_NICKS):\
                    current_nick = ALT_NICKS[nick_index]\
                    nick_index += 1\
                    print(
\f0\b \cf5 "Nick in use, trying:"
\f1\b0 \cf3 , current_nick)\
                    sock.send(f
\f0\b \cf5 "NICK \{current_nick\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
                
\f0\b \cf4 else
\f1\b0 \cf3 :\
                    
\f0\b \cf4 raise
\f1\b0 \cf3  RuntimeError(
\f0\b \cf5 "No available nicknames"
\f1\b0 \cf3 )\
\
            
\f0\b \cf4 if
\f1\b0 \cf3  
\f0\b \cf5 " 001 "
\f1\b0 \cf3  
\f0\b \cf4 in
\f1\b0 \cf3  line:\
                
\f0\b \cf4 if
\f1\b0 \cf3  
\f0\b \cf4 not
\f1\b0 \cf3  current_nick:\
                    current_nick = PRIMARY_NICK\
               
\f0\b \cf2  # Join channels
\f1\b0 \cf3 \
                sock.send(f
\f0\b \cf5 "JOIN \{CHANNEL_IN\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
                sock.send(f
\f0\b \cf5 "JOIN \{CHANNEL_OUT\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
                print(f
\f0\b \cf5 "Connected as \{current_nick\}"
\f1\b0 \cf3 )\
                
\f0\b \cf4 return
\f1\b0 \cf3  sock\
\

\f0\b \cf2 # -------- F\'f6rs\'f6k \'e5terta prim\'e4rt nick --------
\f1\b0 \cf3 \

\f0\b \cf4 def\cf7  try_reclaim_primary
\f1\b0 \cf3 (sock):\
    
\f0\b \cf4 global
\f1\b0 \cf3  last_nick_retry, current_nick\
    
\f0\b \cf4 if
\f1\b0 \cf3  current_nick == PRIMARY_NICK:\
        
\f0\b \cf4 return
\f1\b0 \cf3 \
    
\f0\b \cf4 if
\f1\b0 \cf3  time.time() - last_nick_retry >= NICK_RETRY_INTERVAL:\
        print(
\f0\b \cf5 "Trying to reclaim primary nick"
\f1\b0 \cf3 )\
        sock.send(f
\f0\b \cf5 "NICK \{PRIMARY_NICK\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
        last_nick_retry = time.time()\
\

\f0\b \cf2 # -------- Huvudloop --------
\f1\b0 \cf3 \

\f0\b \cf4 def\cf7  run_bot
\f1\b0 \cf3 ():\
    
\f0\b \cf4 global
\f1\b0 \cf3  current_nick\
    
\f0\b \cf4 while
\f1\b0 \cf3  
\f0\b \cf6 True
\f1\b0 \cf3 :\
        
\f0\b \cf4 try
\f1\b0 \cf3 :\
            sock = connect_irc()\
            buffer = 
\f0\b \cf5 ""
\f1\b0 \cf3 \
            
\f0\b \cf4 while
\f1\b0 \cf3  
\f0\b \cf6 True
\f1\b0 \cf3 :\
                data = sock.recv(4096).decode(
\f0\b \cf5 "utf-8"
\f1\b0 \cf3 , errors=
\f0\b \cf5 "ignore"
\f1\b0 \cf3 )\
                
\f0\b \cf4 if
\f1\b0 \cf3  
\f0\b \cf4 not
\f1\b0 \cf3  data:\
                    
\f0\b \cf4 raise
\f1\b0 \cf3  ConnectionError(
\f0\b \cf5 "Disconnected"
\f1\b0 \cf3 )\
                buffer += data\
                lines = buffer.split(
\f0\b \cf5 "
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 )\
                buffer = lines.pop()\
\
                
\f0\b \cf4 for
\f1\b0 \cf3  line 
\f0\b \cf4 in
\f1\b0 \cf3  lines:\
                    print(
\f0\b \cf5 "DEBUG:"
\f1\b0 \cf3 , line)\
\
                    
\f0\b \cf4 if
\f1\b0 \cf3  line.startswith(
\f0\b \cf5 "PING"
\f1\b0 \cf3 ):\
                        sock.send(f
\f0\b \cf5 "PONG \{line.split()[1]\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
                        
\f0\b \cf4 continue
\f1\b0 \cf3 \
\
                    try_reclaim_primary(sock)\
\
                    
\f0\b \cf4 if
\f1\b0 \cf3  
\f0\b \cf5 "PRIVMSG"
\f1\b0 \cf3  
\f0\b \cf4 in
\f1\b0 \cf3  line:\
                        parts = line.split(
\f0\b \cf5 " "
\f1\b0 \cf3 , 3)\
                        
\f0\b \cf4 if
\f1\b0 \cf3  len(parts) < 4:\
                            
\f0\b \cf4 continue
\f1\b0 \cf3 \
                        sender = parts[0].split(
\f0\b \cf5 "!"
\f1\b0 \cf3 )[0][1:]\
                        channel = parts[2]\
                        message = parts[3][1:]\
\
                        
\f0\b \cf4 if
\f1\b0 \cf3  sender.lower() == current_nick.lower():\
                            
\f0\b \cf4 continue
\f1\b0 \cf3 \
\
                        
\f0\b \cf4 if
\f1\b0 \cf3  channel.lower() == CHANNEL_IN.lower():\
                           
\f0\b \cf2  # Engelska \uc0\u8594  skicka direkt
\f1\b0 \cf3 \
                            
\f0\b \cf4 if
\f1\b0 \cf3  looks_english(message):\
                                out = f
\f0\b \cf5 "\{sender\}: \{message\}"
\f1\b0 \cf3 \
                                sock.send(f
\f0\b \cf5 "PRIVMSG \{CHANNEL_OUT\} :\{out\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
                                
\f0\b \cf4 continue
\f1\b0 \cf3 \
                           
\f0\b \cf2  # Svenska \uc0\u8594  \'f6vers\'e4tt
\f1\b0 \cf3 \
                            translated = translate_sv_to_en(message)\
                            
\f0\b \cf4 if
\f1\b0 \cf3  translated:\
                                out = f
\f0\b \cf5 "\{sender\}: \{translated\}"
\f1\b0 \cf3 \
                                sock.send(f
\f0\b \cf5 "PRIVMSG \{CHANNEL_OUT\} :\{out\}
\f1\b0 \cf8 \\r\\n
\f0\b \cf5 "
\f1\b0 \cf3 .encode())\
\
        
\f0\b \cf4 except
\f1\b0 \cf3  Exception 
\f0\b \cf4 as
\f1\b0 \cf3  e:\
            print(
\f0\b \cf5 "IRC error:"
\f1\b0 \cf3 , e)\
            time.sleep(RECONNECT_DELAY)\
\

\f0\b \cf2 # -------- Start --------
\f1\b0 \cf3 \

\f0\b \cf4 if
\f1\b0 \cf3  __name__ == 
\f0\b \cf5 "__main__"
\f1\b0 \cf3 :\
    print(f
\f0\b \cf5 "Starting IRC bot with Azure translation (Region: \{AZURE_REGION\})"
\f1\b0 \cf3 )\
    run_bot()}