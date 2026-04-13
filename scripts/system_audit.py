import subprocess
import json
import sys

SERVERS = [
    {"name": "wsz-server", "zone": "us-central1-a"},
    {"name": "orcas", "zone": "us-central1-a"},
    {"name": "instance-20240707-081221", "zone": "asia-southeast1-a"}
]

def run_ssh_command(server, command):
    ssh_cmd = [
        "gcloud", "compute", "ssh", server["name"],
        "--zone", server["zone"],
        "--quiet", "--command", command
    ]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {str(e)}"

def get_audit_commands():
    # Thống kê IP, Status Code, và User-Agent từ log container trong 1h qua
    # Giả định log format chuẩn (có thể cần điều chỉnh theo thực tế)
    return """
    echo "--- DOCKER STATUS ---"
    sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
    
    echo "--- RESOURCE USAGE ---"
    free -h | grep "Mem:"
    df -h / | tail -1
    
    echo "--- TOP 10 IPs (Last 1h) ---"
    # Tìm tất cả container và lấy log 1h, sau đó thống kê IP
    sudo docker ps --format "{{.Names}}" | xargs -I {} sh -c 'sudo docker logs --since 1h {} 2>&1' | \
    grep -oE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" | sort | uniq -c | sort -nr | head -n 10
    
    echo "--- ERROR LOGS (Last 1h) ---"
    sudo docker ps --format "{{.Names}}" | xargs -I {} sh -c 'echo "Container: {}"; sudo docker logs --since 1h {} 2>&1' | \
    grep -iE "error|exception|critical|fatal|timeout|502|503|504|429" | tail -n 50
    """

def main():
    report = {}
    audit_cmd = get_audit_commands()
    for server in SERVERS:
        print(f"Auditing {server['name']}...")
        report[server['name']] = run_ssh_command(server, audit_cmd)
    
    print("\n--- FINAL AUDIT DATA ---")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
