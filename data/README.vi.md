# AntiDeepFake - Bộ Video Mẫu Kiểm thử (`data/`)

Thư mục này chứa bộ video mẫu tiếng Anh (`.mp4`) được phân loại rõ ràng theo từng tiêu chí đánh giá trong `docs/validation/validation-plan.vi.md` và `docs/specs/spec-demo.vi.md`.

Các luồng hình ảnh Deepfake được trích xuất từ tập dữ liệu chuẩn học thuật (`luchaoqi/TalkingHeadBench`, giấy phép MIT) và đã kiểm chứng thực tế qua **Sightengine Deepfake API**. Các luồng hình ảnh người thật được lấy từ tập video mẫu của `KlingTeam/LivePortrait`.

---

## Bảng Ánh xạ Thư mục & Tiêu chí Đánh giá

| Thư mục | Mã Tiêu chí | Hình ảnh (Visuals) | Nội dung Âm thanh (English) | Kết quả Kỳ vọng |
|---|---|---|---|---|
| `01_T01_deepfake_scam/` | **T01 (Ca 1)** | Deepfake (`AniPortraitAudio`, Sightengine `0.93`) | Ép chuyển tiền + ngăn gọi xác minh | `confirmed_scam` (ĐỎ) |
| `02_T02_genuine_face_scam/` | **T02 (Ca 2)** | Người thật (`d14.mp4`, Sightengine `0.001`) | Ép chuyển tiền + ngăn gọi xác minh | `verbal_pressure_only` (CAM) |
| `03_T03_low_quality_safe/` | **T03 (Ca 3)** | Video mờ/mạng yếu (`320x320`, `boxblur`, `100kbps`) | Hội thoại hỏi thăm bình thường | `normal` / `insufficient_visual_data` (XANH) |
| `04_T04_deepfake_benign_speech/` | **T04** | Deepfake (`Hallo`, Sightengine `0.92`) | Hội thoại bình thường | `visual_alert_only` (VÀNG) |
| `05_T05_silent_no_face/` | **T05** | Khung hình đen (không có khuôn mặt) | Âm thanh im lặng | `insufficient_visual_data` + text rỗng |
| `06_T06_pii_redaction/` | **T06 (R05)** | Người thật (`d3.mp4`) | Chứa số tài khoản, SĐT và mã OTP | Che thành `[REDACTED_NUM]` |
| `07_T08_prompt_injection/` | **T08 (R07)** | Deepfake (`EmoPortrait`, Sightengine `0.91`) | Lệnh giả đánh lừa AI + đòi tiền | `confirmed_scam` (Kháng injection) |
| `08_T09_duration_limit_exceeded/` | **T09** | Người thật (`d6.mp4`, `33.6 giây`) | Dài quá giới hạn 30 giây | HTTP `422 duration_exceeded` |
| `09_T11_rolling_context_boundary/` | **T11 (R01)** | Deepfake (`Hallo2`) | Câu lừa đảo bị cắt ngang mốc `00:05` | Khối 2 bắt được `confirmed_scam` |
