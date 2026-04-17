# Spec: Tài liệu README.md cho Dự án Log Expert

## 1. Giới thiệu chung
Dự án **Log Expert** là một công cụ hỗ trợ Senior SRE (Site Reliability Engineer) tự động hóa quy trình giám sát và phân tích log trên hạ tầng Google Compute Engine (GCE). Hệ thống tập trung vào việc thu thập dữ liệu song song từ nhiều cụm server, phân tích dựa trên thư viện kiến thức chuyên gia và báo cáo nhanh chóng qua Discord.

## 2. Nguyên lý hoạt động (Core Principles)
Hệ thống vận hành dựa trên 3 nguyên lý cốt lõi:

*   **Parallel Multi-node Auditing (Kiểm tra đa nút song song):** Sử dụng cơ chế Multi-threading trong Python để thực hiện lệnh SSH đồng thời tới tất cả các server trong danh sách (`wsz-server`, `wsz-web-us`, `wsz-web-sea`). Điều này giúp giảm thiểu độ trễ mạng và thời gian chờ đợi phản hồi từ từng node riêng lẻ.
*   **Context-Aware Analysis (Phân tích theo ngữ cảnh):** Thay vì chỉ lọc từ khóa "Error" đơn thuần, hệ thống đối chiếu dữ liệu thu được với bộ quy tắc trong `expert-knowledge.md`. Các mẫu lỗi như OOM (Out of Memory), Database Timeout, hay Retry Storm được nhận diện dựa trên sự kết hợp giữa log ứng dụng và trạng thái tài nguyên hệ thống (RAM, CPU, Disk).
*   **Structured Alerting (Cảnh báo có cấu trúc):** Mọi kết quả phân tích đều được chuẩn hóa thành định dạng JSON chuyên nghiệp (Discord Embed). Cách tiếp cận này giúp các kỹ sư SRE nhanh chóng nắm bắt các thông tin quan trọng (Status, Critical Errors, Proposed Actions) thông qua giao diện trực quan của Discord thay vì đọc hàng ngàn dòng log thô.

## 3. Luồng hoạt động (System Workflow)
Quy trình xử lý dữ liệu của Log Expert bao gồm 3 giai đoạn chính:

1.  **Giai đoạn Thu thập (Collection):**
    *   Kích hoạt thông qua script `system_audit.py`.
    *   Sử dụng `gcloud compute ssh` để thực thi các lệnh Docker (`docker ps`, `docker logs --since 1h`) và lệnh hệ thống (`free -h`, `df -h`).
2.  **Giai đoạn Phân tích (Analysis):**
    *   **Health Check:** Kiểm tra trạng thái các container (Up/Down/Unhealthy).
    *   **Traffic Analysis:** Thống kê và trích xuất TOP 10 IP có lưu lượng request cao nhất trong 1 giờ qua để phát hiện dấu hiệu Crawl/Attack.
    *   **Error Filtering:** Lọc và tóm tắt các dòng log chứa lỗi nghiêm trọng (5xx, Exception, Timeout, Fatal).
3.  **Giai đoạn Báo cáo (Reporting):**
    *   Kết hợp kết quả từ Giai đoạn 2 thành một Payload JSON.
    *   Script `send_to_discord.py` nhận Payload này và đẩy lên Discord Webhook dưới dạng tin nhắn Embed màu sắc (Đỏ cho Lỗi nghiêm trọng, Vàng cho Cảnh báo).

## 4. Hướng dẫn sử dụng thủ công (Manual Usage)
Hệ thống được thiết kế để vận hành linh hoạt thông qua dòng lệnh:

### 4.1. Cấu hình ban đầu
Người dùng cần khai báo Discord Webhook URL thông qua một trong hai cách:
*   **File cấu hình:** Tạo file `.env.logexpert` tại thư mục gốc:
    ```bash
    DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/your_id/your_token"
    ```
*   **Biến môi trường:** `export DISCORD_WEBHOOK_URL="..."`

### 4.2. Chạy lệnh Audit hệ thống
Thực hiện quét toàn bộ các server và hiển thị kết quả phân tích ngay tại terminal:
```bash
python3 scripts/system_audit.py
```

### 4.3. Gửi báo cáo lên Discord
Sau khi có kết quả từ lệnh Audit, người dùng có thể đóng gói thành JSON và gửi báo cáo thủ công:
```bash
python3 scripts/send_to_discord.py '<json_payload>'
```

## 5. Thư viện Kiến thức & Mở rộng
*   Toàn bộ logic nhận diện lỗi được lưu trữ tại `references/expert-knowledge.md`.
*   Để thêm server mới, người dùng chỉ cần cập nhật danh sách `SERVERS` trong file `scripts/system_audit.py`.
