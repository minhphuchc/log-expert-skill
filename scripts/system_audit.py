import subprocess
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVERS = [
    {"name": "wsz-server", "alias": "wsz-server", "zone": "us-central1-a"},
    {"name": "orcas", "alias": "wsz-web-us", "zone": "us-central1-a"},
    {"name": "instance-20240707-081221", "alias": "wsz-web-sea", "zone": "asia-southeast1-a"}
]

def run_ssh_command(server, command):
    alias = server.get("alias", server["name"])
    ssh_cmd = [
        "gcloud", "compute", "ssh", server["name"],
        "--zone", server["zone"],
        "--quiet", "--command", command
    ]
    try:
        # Timeout 60s cho mỗi server
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return alias, result.stdout
        else:
            return alias, f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return alias, "Error: Connection Timeout (60s)"
    except Exception as e:
        return alias, f"Exception: {str(e)}"

def get_audit_commands():
    return """
    echo "--- DOCKER STATUS ---"
    sudo docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
    
    echo "--- RESOURCE USAGE ---"
    free -h | grep "Mem:"
    df -h / | tail -1
    
    echo "--- TOP 10 IPs (Last 1h) ---"
    sudo docker ps --format "{{.Names}}" | xargs -I {} sh -c 'sudo docker logs --since 1h {} 2>&1' | \
    grep -oE "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" | sort | uniq -c | sort -nr | head -n 10
    
    echo "--- ERROR LOGS (Last 1h) ---"
    sudo docker ps --format "{{.Names}}" | xargs -I {} sh -c 'echo "Container: {}"; sudo docker logs --since 1h {} 2>&1' | \
    grep -iE "error|exception|critical|fatal|timeout|502|503|504|429" | tail -n 50
    """

def main():
    report = {}
    audit_cmd = get_audit_commands()
    
    print(f"🚀 Starting parallel audit on {len(SERVERS)} servers...\n")
    
    with ThreadPoolExecutor(max_workers=len(SERVERS)) as executor:
        # Submit tasks
        future_to_server = {executor.submit(run_ssh_command, s, audit_cmd): s["name"] for s in SERVERS}
        
        # Process results as they complete
        for future in as_completed(future_to_server):
            server_name, result = future.result()
            print(f"✅ [Done] Audit completed for: {server_name}")
            report[server_name] = result
    
    print("\n--- FINAL AUDIT DATA ---")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
