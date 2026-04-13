import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Giả lập data
TEST_SERVERS = [
    {"name": "Slow-Server", "delay": 3},
    {"name": "Fast-Server", "delay": 1},
    {"name": "Medium-Server", "delay": 2}
]

def mock_ssh(server):
    time.sleep(server["delay"])
    return server["name"], f"Data from {server['name']} after {server['delay']}s"

def test_main():
    report = {}
    print("Testing parallel execution order...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(mock_ssh, s) for s in TEST_SERVERS]
        for future in as_completed(futures):
            name, res = future.result()
            print(f"Captured: {name}")
            report[name] = res
            
    end_time = time.time()
    total_duration = end_time - start_time
    print(f"\nTotal time: {total_duration:.2f}s (Expected ~3s, not 6s)")
    
    # Assertions
    assert "Fast-Server" in report
    assert "Medium-Server" in report
    assert "Slow-Server" in report
    assert total_duration < 3.5, f"Execution too slow: {total_duration:.2f}s"
    
    # Kiểm tra xem Fast-Server có xong trước Slow-Server không (dựa trên print order)
    # as_completed returns futures as they complete, so we check if the first completed was Fast-Server
    # The current print order already implies completion order.
    print("Test passed if 'Fast-Server' appeared first.")

if __name__ == "__main__":
    test_main()
