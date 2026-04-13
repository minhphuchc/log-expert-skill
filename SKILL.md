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

## Cấu hình Webhook Discord

Để cấu hình Webhook URL, bạn có thể thực hiện một trong hai cách:

1.  **Biến môi trường**: `export DISCORD_WEBHOOK_URL="your_webhook_url"`
2.  **File cấu hình**: Tạo file `.env.logexpert` tại thư mục gốc với nội dung:
    ```
    DISCORD_WEBHOOK_URL="your_webhook_url"
    ```

## Workflow SRE (Nâng cấp)

Thực hiện theo quy trình tự động hóa sau:

### Bước 1: Thu thập Dữ liệu Tổng hợp (Parallel Audit)
Chạy script audit mới để lấy dữ liệu đồng thời từ cả 3 server. Script này sử dụng multi-threading để tối ưu hóa thời gian:
```bash
python3 ./scripts/system_audit.py
```
*Lưu ý: Bạn sẽ thấy các dòng `✅ [Done]` xuất hiện bất đồng bộ khi từng server hoàn tất việc quét.*

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
Cấu trúc JSON mong muốn (Sử dụng `\\n` để ngắt dòng trong JSON string):
{
  "embeds": [{
    "title": "🛡️ BÁO CÁO SRE CHI TIẾT - [NGÀY]",
    "color": 15158332, # Màu đỏ nếu có lỗi nghiêm trọng, 15844367 (Vàng) nếu cảnh báo
    "fields": [
      {"name": "🔴 wsz-server (Main)", "value": "Status: **TIMEOUT**\\nCritical: Không thể SSH vào server. Cần kiểm tra gấp trên GCE Console."},
      {"name": "🟡 orcas (Data)", "value": "Status: **STABLE/WARNING**\\n- DB Error: `ETIMEDOUT` kết nối MySQL.\\n- Traffic: IP `10.128.15.198` (2478 req/h)."},
      {"name": "🟡 SEA Instance", "value": "Status: **UNHEALTHY**\\n- `educooking-client`: Unhealthy (4 weeks).\\n- Lỗi phân quyền: `EACCES` tại Next.js cache.\\n- API Error: Gặp lỗi `429` (Too many requests)."},
      {"name": "🚀 Hành động đề xuất", "value": "1. Restart `wsz-server` nếu Console báo treo.\\n2. Fix permission cache trên SEA Instance.\\n3. Kiểm tra kết nối MySQL từ `orcas` tới DB server."}
    ],
    "footer": {"text": "LogExpert v2.0 | Senior SRE Bot"}
  }]
}


## Tài Nguyên Cấu Thành

- **./references/expert-knowledge.md**: Thư viện mẫu lỗi, Pattern & Anomaly.
- **./scripts/send_to_discord.py**: Công cụ gửi thông báo qua Discord Webhook.
