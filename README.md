# Log Expert - Chuyên Gia Phân Tích Log (Senior SRE Level)

Hệ thống tự động hóa quy trình giám sát, thu thập và phân tích log trên hạ tầng Google Compute Engine (GCE), giúp Senior SRE phản ứng nhanh với các sự cố hệ thống.

## 1. Nguyên lý hoạt động (Core Principles)

Dự án vận hành dựa trên 3 trụ cột kỹ thuật:

*   **Parallel Multi-node Auditing:** Sử dụng cơ chế Multi-threading (Python) để SSH đồng thời vào toàn bộ cụm server (`wsz-server`, `wsz-web-us`, `wsz-web-sea`). Cách tiếp cận này giúp tối ưu hóa băng thông mạng và giảm 70% thời gian phản hồi so với quét tuần tự.
*   **Context-Aware Analysis:** Đối chiếu dữ liệu thu thập được với bộ quy tắc chuyên gia tại `references/expert-knowledge.md`. Hệ thống không chỉ tìm lỗi mà còn nhận diện các kịch bản phức tạp như OOM Kill, Database Timeout, hoặc dấu hiệu của một đợt Crawl Attack.
*   **Structured Alerting:** Chuẩn hóa mọi phát hiện thành định dạng JSON chuyên nghiệp (Discord Embed). Giúp đội ngũ vận hành nắm bắt tình trạng "Health" của hệ thống chỉ trong vài giây qua các khối màu sắc trực quan (Đỏ: Nguy hiểm, Vàng: Cảnh báo).
