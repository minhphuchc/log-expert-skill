# Design Spec: Nâng cấp Hệ thống Audit SRE Song Song

**Ngày**: 13/04/2026
**Trạng thái**: Draft (Chờ phê duyệt)
**Tác giả**: LogExpert SRE Bot (Gemini CLI)

## 1. Mục tiêu (Goals)
- Tối ưu hóa thời gian thực hiện lệnh `system_audit.py` bằng cách chạy song song các phiên SSH tới 3 server GCE (`wsz-server`, `orcas`, `instance-20240707-081221`).
- Đảm bảo cơ chế "ai xong trước hiện trước" (asynchronous reporting) để người dùng thấy tiến trình ngay lập tức.
- Không sử dụng thư viện bên ngoài (chỉ dùng Python Standard Library).

## 2. Kiến trúc (Architecture)

### 2.1 Thành phần chính
- **Thư viện**: `concurrent.futures.ThreadPoolExecutor`
- **Số lượng Workers**: 3 (tương ứng với số lượng server hiện tại).
- **Cơ chế thu thập**: `as_completed(futures)`

### 2.2 Luồng xử lý (Data Flow)
1. **Khởi tạo**: `main()` tạo một danh sách các công việc (`futures`) cho từng server thông qua `executor.submit(run_ssh_command, server, audit_cmd)`.
2. **Thực thi**: Python khởi chạy 3 thread độc lập để gọi lệnh `gcloud compute ssh`.
3. **Phản hồi**: Sử dụng vòng lặp `for future in as_completed(futures):` để bắt kết quả ngay khi một thread hoàn thành.
4. **Kết quả**: In ra trạng thái hoàn tất của từng server và cuối cùng in khối JSON tổng hợp.

## 3. Chi tiết kỹ thuật (Technical Details)

### 3.1 Cấu trúc mã nguồn đề xuất
- Hàm `run_ssh_command` giữ nguyên logic nhưng có thêm xử lý ngoại lệ chặt chẽ hơn để tránh làm treo toàn bộ script.
- Hàm `main` được tái cấu trúc hoàn toàn để sử dụng `ThreadPoolExecutor`.

### 3.2 Xử lý lỗi & Timeout
- Mỗi lệnh SSH sẽ có `timeout=60` giây để tránh treo script nếu server không phản hồi.
- Nếu một server lỗi, kết quả trả về sẽ là một chuỗi mô tả lỗi thay vì làm vỡ cấu trúc JSON cuối cùng.

## 4. Kiểm thử (Testing)
- Chạy `python3 -m py_compile scripts/system_audit.py` để kiểm tra cú pháp.
- Chạy thực tế và quan sát thứ tự hoàn thành của các server (mong đợi: không theo thứ tự cố định, server nào phản hồi nhanh nhất sẽ hiện trước).

## 5. Kế hoạch triển khai (Implementation Plan)
1. Cập nhật file `scripts/system_audit.py`.
2. Kiểm tra tính tương thích với Workflow SRE trong `SKILL.md`.
3. Chạy audit thực tế để xác nhận hiệu năng.
