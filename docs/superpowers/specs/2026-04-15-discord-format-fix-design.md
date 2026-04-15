# Design Spec: Fix Discord Message Formatting (\n Issue)

**Date:** 2026-04-15
**Status:** Draft
**Topic:** Sửa lỗi hiển thị ký tự xuống dòng `\n` trong Discord Embeds khi gửi báo cáo SRE từ LogExpert.

## 1. Problem Statement
Hiện tại, khi LogExpert AI Skill gửi báo cáo SRE lên Discord thông qua script `scripts/send_to_discord.py`, các ký tự xuống dòng (`\n`) trong nội dung báo cáo thường bị hiển thị dưới dạng văn bản thô (`\n`) thay vì ngắt dòng thực tế. Điều này xảy ra do sự chồng chéo trong việc escape ký tự giữa môi trường Shell (khi AI gọi lệnh) và logic xử lý JSON trong Python.

## 2. Proposed Solution (Approach 1)
Nâng cấp logic xử lý trong `scripts/send_to_discord.py` để "thông minh" hơn trong việc nhận diện và chuyển đổi các ký tự ngắt dòng.

### 2.1. Cải tiến hàm `process_payload`
Hàm `process_payload` hiện tại chỉ thay thế chuỗi literal `\\n` thành `\n`. Chúng ta sẽ bổ sung logic để xử lý an toàn các chuỗi JSON phức tạp:
- Đảm bảo các ký tự xuống dòng thực tế (newline characters) không bị lỗi khi `json.loads` giải mã.
- Tự động chuyển đổi các biến thể của ký tự xuống dòng (như `\\n`, `\\\n`) về dạng chuẩn mà Discord API hiểu được (`\n` trong JSON payload).

### 2.2. Xử lý Input an toàn hơn
- Thay vì chỉ dựa vào `json.loads`, script sẽ kiểm tra xem input có bị bao quanh bởi các ký tự dư thừa từ shell không.
- Bổ sung log cảnh báo nếu JSON input không hợp lệ để dễ dàng debug cho AI Skill.

## 3. Implementation Details
- **File:** `scripts/send_to_discord.py`
- **Thay đổi chính:**
    - Cập nhật hàm `process_payload(obj)`.
    - Cải thiện khối `if __name__ == "__main__":` để xử lý tham số CLI linh hoạt hơn.

## 4. Verification Plan
### 4.1. Automated Test
Tạo script test `tests/test_discord_format.py` để kiểm tra 3 trường hợp:
1. **Raw String:** `python3 scripts/send_to_discord.py "Line1\nLine2"`
2. **JSON String (Single Quote):** `python3 scripts/send_to_discord.py '{"content": "Line1\\nLine2"}'`
3. **Complex Embed JSON:** Sử dụng đúng chuỗi báo cáo SRE mà người dùng cung cấp.

### 4.2. Manual Verification
Gửi thử nghiệm thực tế lên Discord (nếu có Webhook URL) hoặc mock server để kiểm tra payload cuối cùng gửi đi có đúng format `\n` (newline character) trong chuỗi JSON hay không.

## 5. Success Criteria
- Tin nhắn trên Discord hiển thị ngắt dòng đúng tại các vị trí có `\n`.
- Không còn ký tự `\n` dư thừa xuất hiện trong văn bản hiển thị trên Discord.
- Script vẫn hoạt động ổn định với các báo cáo cũ.
