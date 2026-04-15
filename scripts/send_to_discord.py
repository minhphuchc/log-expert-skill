#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error
import datetime
import os

def process_payload(obj):
    """
    Đệ quy xử lý payload: 
    1. Chuyển literal '\\n' thành dấu xuống dòng thực tế '\n'.
    2. Giữ nguyên các dấu xuống dòng thực tế đã có.
    """
    if isinstance(obj, dict):
        return {k: process_payload(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [process_payload(i) for i in obj]
    elif isinstance(obj, str):
        # Thay thế literal \n (2 ký tự \ và n) thành newline thực tế
        return obj.replace("\\n", "\n")
    return obj

def send_to_discord(webhook_url, payload_or_content):
    # Xử lý trường hợp input là JSON string
    if isinstance(payload_or_content, str) and payload_or_content.strip().startswith('{'):
        try:
            # Thử parse JSON trực tiếp
            payload = json.loads(payload_or_content)
        except json.JSONDecodeError:
            # Nếu parse lỗi (có thể do chứa newline thực tế), thử fix format trước
            try:
                # Thay thế các newline thực tế trong chuỗi JSON thành \n để json.loads không lỗi
                fixed_content = payload_or_content.replace('\n', '\\n')
                payload = json.loads(fixed_content)
            except:
                # Nếu vẫn lỗi thì coi như text thô
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

    # Xử lý các ký tự xuống dòng trong toàn bộ payload
    payload = process_payload(payload)

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
    
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.logexpert')
    if not url and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            for line in f:
                if line.startswith('DISCORD_WEBHOOK_URL='):
                    url = line.split('=', 1)[1].strip().strip('\"').strip('\'')
                    break

    if len(sys.argv) >= 2:
        if len(sys.argv) == 3:
            url = sys.argv[1]
            content = sys.argv[2]
        else:
            content = sys.argv[1]
            
        if not url:
            print("Error: Webhook URL missing")
            sys.exit(1)
        send_to_discord(url, content)
