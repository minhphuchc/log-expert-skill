#!/usr/bin/env python3
import sys
import json
import urllib.request
import urllib.error

def send_to_discord(webhook_url, content_or_payload):
    """
    Sends a message or embed to a Discord webhook using urllib.
    Supports raw strings (auto-wrapped in embed) or JSON strings (full payload).
    """
    import datetime

    # Check if content is already a JSON string (full payload)
    if isinstance(content_or_payload, str) and content_or_payload.strip().startswith('{'):
        try:
            payload = json.loads(content_or_payload)
        except:
            # Fallback to simple text if JSON is invalid
            payload = {"content": content_or_payload}
    else:
        # Construct a professional Embed by default
        status_color = 0xFFAA00  # Warning (Orange) by default
        if "CRITICAL" in content_or_payload.upper() or "ERROR" in content_or_payload.upper():
            status_color = 0xFF0000 # Red
        elif "HEALTHY" in content_or_payload.upper() or "SUCCESS" in content_or_payload.upper():
            status_color = 0x00FF00 # Green

        payload = {
            "embeds": [{
                "title": "🛡️ SRE System Health Report",
                "description": content_or_payload,
                "color": status_color,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "footer": {
                    "text": "LogExpert Monitoring System",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/689/689355.png"
                }
            }]
        }

    data = json.dumps(payload).encode('utf-8')
    
    req = urllib.request.Request(webhook_url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('User-Agent', 'LogExpert-SRE-Reporter')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            if 200 <= status_code < 300:
                print(f"Success: Message sent to Discord (Status: {status_code}).")
            else:
                print(f"Error: Discord API returned status {status_code}.")
                sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"Failed to send message: HTTP Error {e.code}: {e.read().decode('utf-8')}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Failed to send message: Network error: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to send message: Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    import os
    env_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
    
    if len(sys.argv) == 2:
        # Only one argument provided: it's the message. Use webhook from env.
        if not env_webhook_url:
            print("Error: DISCORD_WEBHOOK_URL environment variable is not set and no URL provided.")
            print("Usage: python3 send_to_discord.py <MESSAGE_CONTENT> (uses DISCORD_WEBHOOK_URL env var)")
            sys.exit(1)
        webhook_url = env_webhook_url
        message_content = sys.argv[1]
    elif len(sys.argv) >= 3:
        # At least two arguments provided: webhook URL and message.
        webhook_url = sys.argv[1]
        message_content = sys.argv[2]
    else:
        print("Usage:")
        print("  python3 send_to_discord.py <MESSAGE_CONTENT> (uses DISCORD_WEBHOOK_URL env var)")
        print("  python3 send_to_discord.py <WEBHOOK_URL> <MESSAGE_CONTENT>")
        sys.exit(1)
    
    send_to_discord(webhook_url, message_content)
