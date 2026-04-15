import sys
import os
import json
import subprocess

def test_format():
    script_path = "scripts/send_to_discord.py"
    # Dùng mock webhook URL
    env = os.environ.copy()
    env["DISCORD_WEBHOOK_URL"] = "http://localhost:9999" # Sẽ fail nhưng ta chỉ check payload

    print("Running format tests...")

    # Case 1: Báo cáo SRE phức tạp (JSON với literal \\n)
    sre_report = '{"embeds": [{"title": "Test", "description": "Line 1\\nLine 2"}]}'
    
    # Test case với newline thực tế trong JSON (Trường hợp hay gây lỗi nhất)
    # Gửi chuỗi JSON có newline thực sự bên trong (giả lập AI gửi qua shell)
    complex_report = '{"embeds": [{"description": "🛡️ BÁO CÁO SRE\n🔴 orcas\nStatus: CRITICAL"}]}'
    
    print("\n[Test 1] Testing complex SRE report format with real newlines...")
    result = subprocess.run(["python3", script_path, complex_report], env=env, capture_output=True, text=True)
    
    # Vì URL sai nên sẽ báo lỗi Connection Refused, nhưng ta muốn biết nó có lỗi JSONDecodeError không
    if "JSONDecodeError" in result.stdout or "JSONDecodeError" in result.stderr:
        print("❌ FAILED: JSONDecodeError detected")
    elif "Error: <urlopen error [Errno 61] Connection refused>" in result.stdout or "Error: <urlopen error [Errno 61] Connection refused>" in result.stderr or "[Errno 111] Connection refused" in result.stdout or "[Errno 111] Connection refused" in result.stderr:
        print("✅ PASSED: Script handled JSON correctly (urllib error expected as success)")
    else:
        # Some systems might have different error codes/messages for connection refused
        print(f"Output: {result.stdout}\nError: {result.stderr}")
        print("❓ Check output manually - should not contain JSONDecodeError")

if __name__ == "__main__":
    test_format()
