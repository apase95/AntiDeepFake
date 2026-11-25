# AntiDeepFake - Hướng dẫn Dùng thử Trực tuyến (Online Demo & Evaluation Guide)

Tài liệu này được định dạng theo tiêu chuẩn 1 trang A4 để gửi kèm bài dự thi MoMo TechDay '26, giúp Ban giám khảo kiểm thử trực tuyến nhanh chóng, thuận tiện.

---

## 1. Truy cập Kiểm thử Trực tuyến
- **URL Sản phẩm**: `https://antideepfake.vercel.app` (hoặc tên miền triển khai chính thức của đội)
- **Tài khoản dùng thử**: Cấu hình mở tự do cho Ban giám khảo (không yêu cầu đăng ký hay đăng nhập).
- **Cách thức thử nghiệm**: Ban giám khảo chọn 1 trong 3 video mẫu có sẵn trên giao diện. Hệ thống AI sẽ tự động phân tích luồng video theo từng block 5 giây và gắn cờ cảnh báo tương ứng trên thanh Timeline thời gian thực.

---

## 2. Ba Kịch bản Kiểm thử Thực tế (Test Cases)

### Ca 1: Ca chính - Video Face-Swap kết hợp Lời nói đáng ngờ
- **Dữ liệu đầu vào**: Video sử dụng công nghệ ghép mặt Deepfake, nhân vật nói câu: *"Chuyển ngay giúp em 15 triệu, đừng gọi cho mẹ nhé"*.
- **Phản ứng của Hệ thống**:
  - Tại giây 00:00 - 00:05: Sightengine phát hiện viền ghép mặt bị mờ (`cv_score: 0.86`).
  - Tại giây 00:05 - 00:10: NLP bắt được câu hối thúc chuyển tiền và câu ngăn gọi xác minh.
  - **Kết quả hiển thị**: Mốc Timeline tại 00:10 chuyển sang màu **ĐỎ RỰC (Confirmed Scam - Độ tin cậy 95%)**.
  - **Bằng chứng cung cấp**: Highlight trực quan câu trích dẫn *"đừng gọi cho mẹ"* và chỉ số can thiệp khuôn mặt.
  - **Khuyến nghị hành động**: *"Cảnh báo lừa đảo khẩn cấp: Tạm dừng giao dịch ngay. Hãy gọi trực tiếp qua số điện thoại đã lưu để xác minh."*

### Ca 2: Ca đối chứng - Webcam người thật nhưng Lời nói đáng ngờ
- **Dữ liệu đầu vào**: Video quay bằng webcam thông thường của người thật (hình ảnh chuẩn), người nói đọc cùng câu: *"Chuyển ngay giúp em, đừng gọi cho mẹ"*.
- **Phản ứng của Hệ thống**:
  - CV trả về điểm số an toàn (`cv_score: 0.08`, không gắn cờ).
  - NLP phát hiện dấu hiệu thao túng tâm lý và nỗ lực ngăn chặn xác thực.
  - **Kết quả hiển thị**: Mốc Timeline chuyển sang màu **CAM (Verbal Pressure Only - Độ tin cậy 88%)**.
  - **Ý nghĩa thực tiễn**: Hệ thống vẫn bảo vệ người dùng kể cả khi hình ảnh không bị deepfake (phòng ngừa trường hợp tài khoản người thân bị chiếm đoạt và kẻ gian ép nạn nhân quay video).

### Ca 3: Ca chất lượng thấp - Video mạng yếu, khung hình bị mờ
- **Dữ liệu đầu vào**: Video thực tế quay qua đường truyền internet yếu, khung hình bị mờ hạt và vỡ nét, nội dung hỏi thăm công việc bình thường.
- **Phản ứng của Hệ thống**:
  - CV tránh báo động giả, tự động gán trạng thái: *"Không đủ dữ liệu hình ảnh (Insufficient Visual Data)"*.
  - NLP xác nhận nội dung nói chuyện an toàn.
  - **Kết quả hiển thị**: Mốc Timeline giữ màu **XANH LÁ (Normal - An toàn)**, hiển thị thông báo mạng yếu mà không gây phiền toái bằng các cảnh báo sai.
