# AntiDeepFake - Đặc tả Sản phẩm (Product Specification)

## 1. Tổng quan Dự án
- **Tên dự án**: AntiDeepFake (DeepCall Sentinel)
- **Định vị sản phẩm**: Trợ lý AI đa phương thức (Multimodal) cảnh báo lừa đảo và phát hiện Deepfake theo thời gian thực trong cuộc gọi video.
- **Chủ đề dự thi**: Chống lừa đảo / Trợ lý AI trong Fintech (TechDay '26 - MoMo).
- **Mục tiêu cốt lõi**: Can thiệp và phát tín hiệu cảnh báo ngay trong lúc cuộc gọi đang diễn ra, trước khi người dùng thực hiện chuyển tiền, cung cấp mã OTP hoặc tiết lộ thông tin bảo mật cho kẻ gian.

---

## 2. Đối tượng Người dùng Mục tiêu
- Khách hàng cá nhân sử dụng ví điện tử MoMo và các ứng dụng ngân hàng số.
- Đặc biệt hướng tới người lớn tuổi, phụ huynh hoặc các gia đình có con cái/người thân sống xa, thường xuyên nhận các cuộc gọi video nhờ chuyển tiền hoặc hỗ trợ tài chính khẩn cấp.

---

## 3. Vấn đề Cấp thiết (Pain Points)
- Kẻ gian chiếm quyền điều khiển tài khoản mạng xã hội (Facebook, Zalo, Telegram) của người thân. Chúng sử dụng công nghệ hoán đổi khuôn mặt (Face-swap Deepfake) hoặc phát lại video cũ trong một cuộc gọi ngắn (5 - 10 giây) để tạo dựng niềm tin.
- Thủ đoạn thao túng tâm lý: Kẻ lừa đảo tạo áp lực tâm lý gấp gáp bằng những câu nói như *"Chuyển ngay giúp em/con, đừng gọi cho mẹ biết nhé"*, lấy cớ đường truyền mạng chập chờn để cúp máy sớm.
- Hậu quả nghiêm trọng: Việc đưa ra cảnh báo sau khi cuộc gọi kết thúc thường đã quá muộn vì nạn nhân đã chuyển tiền xong. Sản phẩm bắt buộc phải nhận diện và chỉ ra điểm khả nghi ngay trong lúc video đang phát để người dùng kịp thời dừng lại và xác minh.

---

## 4. Lõi AI và Triết lý Can thiệp Độc lập

### 4.1. Khối Computer Vision (Phân tích hình ảnh trực tiếp)
- Lấy mẫu các khung hình (keyframes) từ luồng video theo từng cửa sổ 5 giây.
- Gọi Sightengine REST API chuyên biệt về phát hiện Deepfake/Face-swap để xuất ra điểm số tin cậy (`cv_score` từ `0.0` đến `1.0`).
- Xử lý tình huống biên: Nếu khuôn mặt quá nhỏ, bị out nét hoặc mờ do băng thông mạng kém, hệ thống sẽ đánh dấu trạng thái là `insufficient_visual_data` (Không đủ dữ liệu hình ảnh) thay vì báo động giả là video lừa đảo.

### 4.2. Khối Xử lý Ngôn ngữ Tự nhiên - NLP (Phân tích giọng nói thời gian thực)
- Bóc tách âm thanh tiếng Việt thành văn bản theo từng đoạn 5 giây bằng mô hình `gemini-3.5-transcribe` độ trễ thấp của Google.
- Tự động che chắn các thông tin nhạy cảm (số tài khoản, OTP) trước khi xử lý.
- Đánh giá các dấu hiệu thao túng tâm lý: hối thúc chuyển tiền gấp, xin mã OTP, đe dọa, yêu cầu giữ bí mật hoặc ngăn cản gọi lại cho người thân.

### 4.3. Triết lý Đánh giá Rủi ro & Can thiệp Độc lập
- **Hai nhánh CV và NLP không bắt buộc phải đồng thuận để kích hoạt cảnh báo**:
  1. **Phát hiện dấu hiệu lừa đảo bằng lời nói**: Nếu nội dung yêu cầu chuyển tiền gấp và ngăn cản gọi xác minh, hệ thống kích hoạt ngay cảnh báo ĐỎ khẩn cấp mà không cần chờ kết quả hình ảnh.
  2. **Chỉ phát hiện chỉnh sửa hình ảnh**: Nếu khuôn mặt có dấu hiệu ghép nhưng lời nói bình thường, hệ thống hiển thị cảnh báo VÀNG: *"Phát hiện dấu hiệu chỉnh sửa hình ảnh; không dùng video này để xác nhận danh tính"*, không vội vàng kết luận người gọi là kẻ lừa đảo.
  3. **Cả hai nhánh cùng xác nhận**: Kích hoạt cảnh báo ĐỎ mức cao nhất: *"Xác nhận nguy cơ lừa đảo cao - Dừng giao dịch ngay"*.
