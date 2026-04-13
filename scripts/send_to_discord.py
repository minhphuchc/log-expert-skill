#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error
import datetime
import os

def send_to_discord(webhook_url, payload_or_content):
    if isinstance(payload_or_content, str) and payload_or_content.strip().startswith('{'):
        try:
            payload = json.loads(payload_or_content)
        except:
            payload = {"content": payload_or_content}
    else:
        # Mặc định tạo Embed nếu truyền text thô
        payload = {
            "embeds": [{
                "title": "🛡️ SRE System Health Report",
                "description": payload_or_content,
                "color": 0xFFAA00,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "footer": {"text": "LogExpert SRE System"}
            }]
        }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(webhook_url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'LogExpert-SRE-Reporter')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"Success: Status {response.getcode()}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    url = os.environ.get('DISCORD_WEBHOOK_URL')
    if len(sys.argv) >= 2:
        # Nếu truyền 2 tham số, tham số 1 là URL, tham số 2 là message
        if len(sys.argv) == 3:
            url = sys.argv[1]
            content = sys.argv[2]
        else:
            content = sys.argv[1]
            
        if not url:
            print("Error: Webhook URL missing")
            sys.exit(1)
        send_to_discord(url, content)
