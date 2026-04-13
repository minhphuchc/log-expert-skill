---
name: log-expert
description: Chuyên gia phân tích log hệ thống trên GCE, hỗ trợ Docker logs và gửi báo cáo qua Discord. Kích hoạt khi cần kiểm tra sức khỏe các server (wsz-server, orcas, instance-20240707-081221), điều tra lỗi ứng dụng (JSON, OpenAI, DB, OOM, CPU, Stacktrace, Anomaly), hoặc tổng hợp báo cáo log Senior SRE level.
---

# Log Expert - Chuyên Gia Phân Tích Log (Senior SRE Level)

**LƯU Ý QUAN TRỌNG:** Luôn trả kết quả, báo cáo và phân tích bằng **tiếng Việt**.

## When to use
Kích hoạt skill này khi bạn nhận được yêu cầu:
- Kiểm tra log hoặc tình trạng của các server trọng yếu: `wsz-server`, `orcas`, hoặc `instance-20240707-081221`.
- Điều tra nguyên nhân các lỗi ứng dụng phức tạp (OOM, Stacktrace, Anomaly detection).
- Phân tích hệ thống theo tiêu chuẩn SRE và gửi báo cáo chuyên sâu lên Discord.

## Danh sách Server & Cấu hình (GCE)

| Server Name | Zone | Mục đích |
| :--- | :--- | :--- |
| **wsz-server** | us-central1-a | Server chính (v1/v2) |
| **orcas** | us-central1-a | Server xử lý dữ liệu |
| **instance-20240707-081221** | asia-southeast1-a | Server khu vực Đông Nam Á |

## Workflow SRE (Nâng cấp)

Thực hiện theo quy trình tự động hóa sau:

### Bước 1: Thu thập Dữ liệu Tổng hợp
Chạy script audit để lấy dữ liệu từ cả 3 server:
```bash
python3 ./scripts/system_audit.py
```

### Bước 2: Phân tích Chuyên sâu (AI Analyzer)
Đọc dữ liệu từ Bước 1 và thực hiện:
1. **Health Check**: Xác định container Unhealthy/Exited và tìm nguyên nhân trong log.
2. **Crawl Detection**: Kiểm tra "TOP 10 IPs". Nếu một IP có lượng request vượt trội (> 30% tổng) hoặc User-Agent lạ, đánh dấu là "Crawl Detected".
3. **Error Analysis**: Nhận diện các lỗi Critical (5xx, Timeout, OOM).
4. **Correlation**: Kiểm tra xem lỗi có xảy ra đồng thời trên nhiều server/container không.

### Bước 3: Đưa ra Gợi ý Hành động
Dựa trên phân tích, đề xuất các hành động:
- Restart container cụ thể.
- Chặn IP (nếu crawl/attack).
- Kiểm tra kết nối mạng/DB.

### Bước 4: Báo cáo Discord (Embed Format)
AI sẽ tạo một JSON payload chuyên nghiệp và gửi qua:
```bash
python3 ./scripts/send_to_discord.py '<JSON_PAYLOAD>'
```
Cấu trúc JSON mong muốn:
{
  "embeds": [{
    "title": "🛡️ BÁO CÁO SRE CHI TIẾT",
    "color": 15158332,
    "fields": [
      {"name": "Server status", "value": "..."},
      {"name": "Error details", "value": "..."},
      {"name": "Crawl & Traffic", "value": "..."},
      {"name": "Actionable Suggestions", "value": "..."}
    ],
    "footer": {"text": "LogExpert v2.0"}
  }]
}

## Tài Nguyên Cấu Thành

- **./references/expert-knowledge.md**: Thư viện mẫu lỗi, Pattern & Anomaly.
- **./scripts/send_to_discord.py**: Công cụ gửi thông báo qua Discord Webhook.
