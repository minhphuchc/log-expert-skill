---
name: log-expert
description: Chuyên gia phân tích log hệ thống trên GCE, hỗ trợ Docker logs và gửi báo cáo qua Discord. Kích hoạt khi cần kiểm tra sức khỏe server wsz-server, điều tra lỗi ứng dụng (JSON, OpenAI, DB, OOM, CPU, Stacktrace, Anomaly), hoặc tổng hợp báo cáo log Senior SRE level.
---

# Log Expert - Chuyên Gia Phân Tích Log (Senior SRE Level)

**LƯU Ý QUAN TRỌNG:** Luôn trả kết quả, báo cáo và phân tích bằng **tiếng Việt**.

## When to use
Kích hoạt skill này khi bạn nhận được yêu cầu:
- Kiểm tra log hoặc tình trạng của server `wsz-server` trên Google Cloud.
- Điều tra nguyên nhân các lỗi ứng dụng phức tạp (OOM, Stacktrace, Anomaly detection).
- Phân tích hệ thống theo tiêu chuẩn SRE và gửi báo cáo chuyên sâu lên Discord.

## Workflow SRE (5 Bước Chuẩn)

Chào SRE! Đây là quy trình phân tích hệ thống chuyên sâu. Hãy thực hiện nghiêm ngặt các bước sau:

### Bước 1: Thu thập Ngữ cảnh (Context Collection)
Kết nối SSH và thu thập thông tin tài nguyên hệ thống để xác định "môi trường" của lỗi:
```bash
# Kết nối GCE
gcloud compute ssh wsz-server --zone=us-central1-a --quiet

# Kiểm tra tài nguyên hệ thống
top -b -n 1 | head -n 20
df -h
free -h

# Trích xuất Docker Logs
sudo docker logs --since 1h wsz-server-v1
```

### Bước 2: Phân loại (Triage)
Dựa trên log và tài nguyên, xác định mức độ ưu tiên:
- **P0/Critical**: Hệ thống sập (OOM, DB Down, No Space Left).
- **P1/High**: Lỗi chức năng chính (OpenAI Timeout, Auth Fail).
- **P2/Normal**: Lỗi lẻ tẻ hoặc Warning.

### Bước 3: Phân tích Pattern (Pattern Analysis)
Sử dụng tài liệu tại `./references/expert-knowledge.md` để tìm các dấu hiệu:
- **Retry Storm**: Request tăng đột biến kèm lỗi 429/503.
- **Cascading Failure**: Lỗi DB gây nghẽn kết nối diện rộng.
- **Memory Leak**: RAM khả dụng giảm dần theo thời gian.

### Bước 4: Tóm tắt Báo cáo (Report Summary)
Tạo báo cáo Markdown chuyên nghiệp gồm:
- **Executive Summary**: Trạng thái "Health" của hệ thống.
- **Detailed Findings**: Phân tích log patterns và số liệu tài nguyên.
- **Root Cause Analysis (RCA)**: Xác định nguyên nhân gốc rễ.

### Bước 5: Kế hoạch Hành động (Action Plan)
Đề xuất các bước khắc phục cụ thể và gửi báo cáo qua Discord. Thiết lập biến môi trường `DISCORD_WEBHOOK_URL` trước khi gửi:
```bash
# Thiết lập Webhook
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."

# Gửi báo cáo (tự động dùng DISCORD_WEBHOOK_URL)
python3 ./scripts/send_to_discord.py "NỘI_DUNG_BÁO_CÁO_SRE"

# Hoặc cung cấp trực tiếp URL
python3 ./scripts/send_to_discord.py "https://discord.com/api/webhooks/..." "NỘI_DUNG_BÁO_CÁO_SRE"
```

## Tài Nguyên Cấu Thành

- **./references/expert-knowledge.md**: Thư viện mẫu lỗi, Pattern & Anomaly.
- **./scripts/send_to_discord.py**: Công cụ gửi thông báo qua Discord Webhook.
