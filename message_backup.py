import requests
import json
import time
from datetime import datetime

USER_TOKEN = ""  # 사용자 토큰
CHANNEL_ID = ""   # 메세지를 백업할 채널 ID
OUTPUT_FILE = "channel_chat_log.txt"

headers = {
    "Authorization": USER_TOKEN,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

all_formatted_messages = []
before_id = None
count = 0

print("메시지수집 시작")

while True:
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages?limit=100" # 메시지 제한
    if before_id:
        url += f"&before={before_id}"
        
    response = requests.get(url, headers=headers)
    
    if response.status_code == 429:
        retry_after = response.json().get("retry_after", 5)
        print(f"요청 제한 {retry_after}초 대기")
        time.sleep(retry_after)
        continue
        
    if response.status_code != 200:
        print(f"에러 발생 (코드: {response.status_code})")
        break
        
    messages = response.json()
    if not messages:
        break
        
    for msg in messages:
        raw_time = msg["timestamp"]
        try:
            dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_time = raw_time[:19].replace("T", " ")

        author_name = msg["author"]["username"]
        content = msg.get("content", "").strip()

        msg_lines = []
        
        if content:
            msg_lines.append(f"[{formatted_time}] {author_name}: {content}")
        else:
            if msg.get("embeds") or msg.get("attachments"):
                msg_lines.append(f"[{formatted_time}] {author_name}:")

        if msg.get("embeds"):
            for idx, embed in enumerate(msg["embeds"], 1):
                msg_lines.append(f"[Embed #{idx}]")
                
                if embed.get("title"):
                    msg_lines.append(f"제목: {embed['title']}")
                if embed.get("description"):
                    msg_lines.append(f"설명: {embed['description']}")

                if embed.get("fields"):
                    for field in embed["fields"]:
                        msg_lines.append(f"    - {field['name']}: {field['value']}")
                        
                if embed.get("footer") and embed["footer"].get("text"):
                    msg_lines.append(f"  (하단 문구: {embed['footer']['text']})")

        if msg.get("attachments"):
            for att in msg["attachments"]:
                msg_lines.append(f"첨부파일: {att['url']}")

        full_message_text = "\n".join(msg_lines)
        if full_message_text:
            all_formatted_messages.append(full_message_text)
        
    count += len(messages)
    print(f"현재{count}개 완료")
    
    before_id = messages[-1]["id"]
    time.sleep(1.5)

all_formatted_messages.reverse()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n\n".join(all_formatted_messages))

print("-" * 50)
print(f"완료! 총 {len(all_formatted_messages)}개의 대화를'{OUTPUT_FILE}'파일에 저장")
print("-" * 50)